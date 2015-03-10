import floppyforms as forms
from django.forms import BaseFormSet, formset_factory
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string, get_template
from django.template.base import TemplateDoesNotExist
from django.utils.translation import ugettext as _

from configuration.models import (
    Category,
    Configuration,
    Key,
    Questiongroup,
)
from qcat.errors import (
    ConfigurationError,
    ConfigurationErrorInvalidCondition,
    ConfigurationErrorInvalidConfiguration,
    ConfigurationErrorInvalidOption,
    ConfigurationErrorNoConfigurationFound,
    ConfigurationErrorNotInDatabase,
    ConfigurationErrorTemplateNotFound,
)
from qcat.utils import (
    find_dict_in_list,
    is_empty_list_of_dicts,
)


class QuestionnaireQuestion(object):
    """
    A class representing the configuration of a Question of the
    Questionnaire. A Question basically consists of the Key and optional
    Values (for Questions with predefined Answers)
    """
    valid_options = [
        'key',
        'list_position',
        'form_template',
        'conditions',
        'conditional'
    ]
    valid_field_types = [
        'char',
        'text',
        'bool',
        'measure',
        'checkbox',
        'image_checkbox',
    ]
    translation_original_prefix = 'original_'
    translation_translation_prefix = 'translation_'
    translation_old_prefix = 'old_'
    value_image_path = '/static/assets/img/'

    def __init__(self, questiongroup, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Question. It needs to have the following
        format::

          {
            # The key of the question.
            "key": "KEY",

            # (optional)
            "list_position": 1,

            # (optional)
            "form_template": "TEMPLATE_NAME",

            # (optional)
            "conditional": true,

            # (optional)
            "conditions": [],
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/questiongroup`

        Raises:
            :class:`qcat.errors.ConfigurationErrorInvalidConfiguration`,
            ``ConfigurationErrorNotInDatabase``.
        """
        validate_type(
            configuration, dict, 'questions', 'list of dicts',
            'questiongroups')
        validate_options(
            configuration, self.valid_options, QuestionnaireQuestion)

        key = configuration.get('key')
        if not isinstance(key, str):
            raise ConfigurationErrorInvalidConfiguration(
                'key', 'str', 'questions')

        try:
            key_object = Key.objects.get(keyword=key)
        except Key.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Key, key)

        self.questiongroup = questiongroup
        self.list_position = configuration.get('list_position')
        self.key_object = key_object
        self.key_config = key_object.configuration
        self.label = key_object.get_translation('label')
        self.keyword = key

        self.field_type = self.key_config.get('type', 'char')
        if self.field_type not in self.valid_field_types:
            raise ConfigurationErrorInvalidOption(
                self.field_type, 'type', 'Key')

        form_template = 'default'
        if self.field_type == 'measure':
            form_template = 'inline_3'
        elif self.field_type == 'image_checkbox':
            form_template = 'no_label'
        form_template = self.key_config.get('form_template', configuration.get(
            'form_template', form_template))
        self.form_template = 'form/question/{}.html'.format(form_template)
        try:
            get_template(self.form_template)
        except TemplateDoesNotExist:
            raise ConfigurationErrorTemplateNotFound(self.form_template, self)

        self.images = []
        self.choices = ()
        self.value_objects = []
        if self.field_type == 'bool':
            self.choices = ((True, _('Yes')), (False, _('No')))
        elif self.field_type in ['measure', 'checkbox', 'image_checkbox']:
            self.value_objects = self.key_object.values.all()
            if len(self.value_objects) == 0:
                raise ConfigurationErrorNotInDatabase(
                    self, '[values of key {}]'.format(self.keyword))
            if self.field_type in ['measure']:
                choices = [('', '-')]
            else:
                choices = []
            for i, v in enumerate(self.value_objects):
                if self.field_type in ['measure']:
                    choices.append((i+1, v.get_translation('label')))
                else:
                    choices.append((v.keyword, v.get_translation('label')))
                if self.field_type in ['image_checkbox']:
                    self.images.append('{}{}'.format(
                        self.value_image_path,
                        v.configuration.get('image_name')))
            self.choices = tuple(choices)

        self.conditional = configuration.get('conditional', False)

        conditions = []
        for condition in configuration.get('conditions', []):
            try:
                cond_value, cond_expression, cond_key = condition.split('|')
            except ValueError:
                raise ConfigurationErrorInvalidCondition(
                    condition, 'Needs to have form "value|condition|key"')
            # Check that value exists
            if cond_value not in [v[0] for v in self.choices]:
                raise ConfigurationErrorInvalidCondition(
                    condition, 'Value "{}" of condition not found in the Key\''
                    's choices'.format(cond_value))
            # Check the condition expression
            try:
                cond_expression = eval(cond_expression)
            except SyntaxError:
                raise ConfigurationErrorInvalidCondition(
                    condition, 'Expression "{}" is not a valid Python '
                    'condition'.format(cond_expression))
            if not isinstance(cond_expression, bool):
                raise ConfigurationErrorInvalidCondition(
                    condition,
                    'Only the following Python expressions are valid: bool')
            # Check that the key exists in the same questiongroup.
            cond_key_object = self.questiongroup.get_question_by_key_keyword(
                cond_key)
            if cond_key_object is None:
                raise ConfigurationErrorInvalidCondition(
                    condition,
                    'Key "{}" is not in the same questiongroup'.format(
                        cond_key))
            if not (
                    self.field_type == 'image_checkbox' and
                    cond_key_object.field_type == 'image_checkbox'):
                raise ConfigurationErrorInvalidCondition(
                    condition, 'Only valid for types "image_checkbox"')
            conditions.append((cond_value, cond_expression, cond_key))
        self.conditions = conditions

        # TODO
        self.required = False

    def add_form(self, formfields, templates, show_translation=False):
        """
        Adds one or more fields to a dictionary of formfields.

        Args:
            ``formfields`` (dict): A dictionary of formfields.

            ``templates`` (dict): A dictionary with templates to be used
            to render the questions.

            ``show_translation`` (bool): A boolean indicating whether to
            add additional fields for translation (``True``) or not
            (``False``). Defaults to ``False``.

        Returns:
            ``dict``. The updated formfields dictionary.

            ``dict``. The updated templates dictionary.
        """
        readonly_attrs = {'readonly': 'readonly'}
        field = None
        translation_field = None
        widget = None
        if self.field_type == 'char':
            field = forms.CharField(
                label=self.label, widget=forms.TextInput(),
                required=self.required)
            translation_field = forms.CharField(
                label=self.label, widget=forms.TextInput(attrs=readonly_attrs),
                required=self.required)
        elif self.field_type == 'text':
            field = forms.CharField(
                label=self.label, widget=forms.Textarea(),
                required=self.required)
            translation_field = forms.CharField(
                label=self.label, widget=forms.Textarea(attrs=readonly_attrs),
                required=self.required)
        elif self.field_type == 'bool':
            field = forms.NullBooleanField(
                label=self.label, widget=RadioSelect(choices=self.choices),
                required=self.required)
        elif self.field_type == 'measure':
            field = forms.ChoiceField(
                label=self.label, choices=self.choices, widget=MeasureSelect,
                required=self.required, initial=self.choices[0][0])
        elif self.field_type == 'checkbox':
            field = forms.MultipleChoiceField(
                label=self.label, widget=Checkbox, choices=self.choices,
                required=self.required)
        elif self.field_type == 'image_checkbox':
            # Make the image paths available to the widget
            widget = ImageCheckbox()
            widget.images = self.images
            field = forms.MultipleChoiceField(
                label=self.label, widget=widget, choices=self.choices,
                required=self.required)
        else:
            raise ConfigurationErrorInvalidOption(
                self.field_type, 'type', self)

        if translation_field is None:
            # Values which are not translated
            formfields[self.keyword] = field
            templates[self.keyword] = self.form_template
        else:
            # Store the old values in a hidden field
            old = forms.CharField(
                label=self.label, widget=forms.HiddenInput(),
                required=self.required)
            if show_translation:
                formfields['{}{}'.format(
                    self.translation_translation_prefix,
                    self.keyword)] = translation_field
            formfields['{}{}'.format(
                self.translation_original_prefix, self.keyword)] = field
            formfields['{}{}'.format(
                self.translation_old_prefix, self.keyword)] = old
            for f in [
                '{}{}'.format(
                    self.translation_translation_prefix,
                    self.keyword),
                '{}{}'.format(
                    self.translation_original_prefix, self.keyword),
                '{}{}'.format(
                    self.translation_old_prefix, self.keyword)
            ]:
                templates[f] = self.form_template

        if widget:
            widget.conditional = self.conditional
            widget.conditions = self.conditions

        return formfields, templates

    def get_details(self, data={}):
        value = data.get(self.keyword)
        if self.field_type in [
                'bool', 'measure', 'checkbox', 'image_checkbox']:
            # Look up the labels for the predefined values
            if not isinstance(value, list):
                value = [value]
            values = self.lookup_choices_labels_by_keywords(value)
        if self.field_type in ['char', 'text']:
            rendered = render_to_string(
                'details/field/textinput.html', {
                    'key': self.label,
                    'value': value})
            return rendered
        if self.field_type in ['bool', 'measure']:
            rendered = render_to_string(
                'details/field/textinput.html', {
                    'key': self.label,
                    'value': values[0]})
            return rendered
        elif self.field_type in ['checkbox']:
            rendered = render_to_string(
                'details/field/checkbox.html', {
                    'key': self.label,
                    'values': values
                })
            return rendered
        elif self.field_type in ['image_checkbox']:
            conditional_outputs = []
            for v in value:
                conditional_rendered = None
                for cond in self.conditions:
                    if v != cond[0]:
                        continue
                    cond_key_object = self.questiongroup.\
                        get_question_by_key_keyword(cond[2])
                    conditional_rendered = cond_key_object.get_details(data)
                conditional_outputs.append(conditional_rendered)

            # Look up the image paths for the values
            images = []
            for v in value:
                if v is not None:
                    i = [y[0] for y in list(self.choices)].index(v)
                    images.append(self.images[i])
            template = 'details/field/image_checkbox.html'
            if self.conditional:
                template = 'details/field/image_checkbox_conditional.html'
            rendered = render_to_string(
                template, {
                    'key': self.label,
                    'values': list(zip(values, images, conditional_outputs)),
                })
            return rendered
        else:
            raise ConfigurationErrorInvalidOption(
                self.field_type, 'type', self)

    def lookup_choices_labels_by_keywords(self, keywords):
        """
        Small helper function to lookup the label of choices (values of
        the keys) based on their keyword. If a label is not found, an
        empty string is added as label.

        Args:
            ``keywords`` (list): A list with value keywords.

        Returns:
            ``list``. A list with labels of the values.
        """
        labels = []
        for keyword in keywords:
            if (not isinstance(keyword, str) and not isinstance(keyword, bool)
                    and not isinstance(keyword, int)):
                labels.append('')
            labels.append(dict(self.choices).get(keyword))
        return labels


class QuestionnaireQuestiongroup(object):
    """
    A class representing the configuration of a Questiongroup of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'questions',
        'max_num',
        'min_num',
    ]
    default_template = 'default'
    default_min_num = 1

    def __init__(self, custom_configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Questiongroup. It needs to have the
        following format::

          {
            # The keyword of the questiongroup.
            "keyword": "QUESTIONGROUP_KEYWORD",

            # (optional)
            "min_num": 1,

            # (optional)
            "max_num": 1,

            # A list of questions.
            "questions": [
              # ...
            ]
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/questiongroup`

        Raises:
            :class:`qcat.errors.ConfigurationErrorInvalidConfiguration`
        """
        self.keyword = custom_configuration.get('keyword')
        if not isinstance(self.keyword, str):
            raise ConfigurationErrorInvalidConfiguration(
                'keyword', 'str', 'questiongroups')

        try:
            questiongroup_object = Questiongroup.objects.get(
                keyword=self.keyword)
        except Questiongroup.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Questiongroup, self.keyword)
        self.configuration = questiongroup_object.configuration

        self.configuration.update(custom_configuration)

        validate_type(
            self.configuration, dict, 'questiongroups', 'list of dicts',
            'subcategories')
        validate_options(
            self.configuration, self.valid_options, QuestionnaireQuestiongroup)

        self.min_num = self.configuration.get('min_num', self.default_min_num)
        if not isinstance(self.min_num, int) or self.min_num < 1:
            raise ConfigurationErrorInvalidConfiguration(
                'min_num', 'integer >= 1', 'questiongroup')

        self.max_num = self.configuration.get('max_num', self.min_num)
        if not isinstance(self.max_num, int) or self.max_num < 1:
            raise ConfigurationErrorInvalidConfiguration(
                'max_num', 'integer >= 1', 'questiongroup')

        self.helptext = ''
        translation = questiongroup_object.translation
        if translation:
            self.helptext = translation.get_translation('helptext')

        self.questions = []
        conf_questions = self.configuration.get('questions', [])
        if (not isinstance(conf_questions, list) or len(conf_questions) == 0):
            raise ConfigurationErrorInvalidConfiguration(
                'questions', 'list of dicts', 'questiongroups')

        for conf_question in conf_questions:
            self.questions.append(QuestionnaireQuestion(self, conf_question))

        # TODO
        self.required = False

    @staticmethod
    def merge_configurations(base, specific):
        """
        Merges two configurations of questiongroups into a single one.
        The base configuration is extended by the specific
        configuration.

        Questions are identified by their key and merged. If a question
        is part of both configurations, the specific configuration will
        completely overwrite the base configuration of the question.

        Args:
            ``base`` (dict): The configuration of the base Questiongroup
            on which the specific configuration is based.

            ``specific`` (dict): The configuration of the specific
            Questiongroup extending the base configuration.

        Returns:
            ``dict``. The merged configuration.
        """
        validate_type(
            base, dict, 'questiongroups', 'list of dicts', 'subcategories')
        validate_type(
            specific, dict, 'questiongroups', 'list of dicts', 'subcategories')

        merged_questions = []
        base_questions = base.get('questions', [])
        specific_questions = specific.get('questions', [])

        if base_questions:
            validate_type(
                base_questions, list, 'questions', 'list of dicts',
                'questiongroups')
        validate_type(
            specific_questions, list, 'questions', 'list of dicts',
            'questiongroups')

        # Collect all base question configurations. If the same
        # questions are also defined in the specific configuration,
        # simply overwrite the base configuration.
        for base_question in base_questions:
            specific_question = find_dict_in_list(
                specific_questions, 'key', base_question.get('key'))
            if specific_question:
                merged_questions.append(specific_question)
            else:
                merged_questions.append(base_question)

        # Collect all specific question configurations which are not
        # part of the base questions
        for specific_question in specific_questions:
            base_question = find_dict_in_list(
                base_questions, 'key', specific_question.get('key'))
            if not base_question:
                merged_questions.append(specific_question)

        base['questions'] = merged_questions
        return base

    def get_form(
            self, post_data=None, initial_data=None, show_translation=False):
        """
        Returns:
            ``forms.formset_factory``. A formset consisting of one or
            more form fields representing a set of questions belonging
            together and which can possibly be repeated multiple times.
        """
        formfields = {}
        templates = {}
        for f in self.questions:
            formfields, templates = f.add_form(
                formfields, templates, show_translation)
        Form = type('Form', (forms.Form,), formfields)

        formset_options = {
            'max_num': self.max_num,
            'min_num': self.min_num,
            'extra': 0,
            'validate_max': True,
            'validate_min': True,
        }

        if self.required is True:
            FormSet = formset_factory(
                Form, formset=RequiredFormSet, **formset_options)
        else:
            FormSet = formset_factory(Form, **formset_options)

        if initial_data and len(initial_data) == 1 and initial_data[0] == {}:
            initial_data = None

        config = {
            'keyword': self.keyword,
            'helptext': self.helptext,
            'templates': templates,
        }

        return config, FormSet(
            post_data, prefix=self.keyword, initial=initial_data)

    def get_details(self, data=[]):
        rendered_questions = []
        for question in self.questions:
            if question.conditional:
                continue
            for d in data:
                rendered_questions.append(question.get_details(d))
        rendered = render_to_string(
            'details/questiongroup.html', {
                'questions': rendered_questions})
        return rendered

    def get_question_by_key_keyword(self, key_keyword):
        for question in self.questions:
            if question.keyword == key_keyword:
                return question
        return None


class QuestionnaireSubcategory(object):
    """
    A class representing the configuration of a Subcategory of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'questiongroups',
    ]

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Subcategory. It needs to have the following
        format::

          {
            # The keyword of the subcategory.
            "keyword": "SUBCAT_KEYWORD",

            # A list of questiongroups.
            "questiongroups": [
              # ...
            ]
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/subcategory`

        Raises:
            :class:`qcat.errors.ConfigurationErrorInvalidConfiguration`,
            ``ConfigurationErrorNotInDatabase``.
        """
        validate_type(
            configuration, dict, 'subcategories', 'list of dicts',
            'categories')
        validate_options(
            configuration, self.valid_options, QuestionnaireSubcategory)

        keyword = configuration.get('keyword')
        if not isinstance(keyword, str):
            raise ConfigurationErrorInvalidConfiguration(
                'keyword', 'str', 'subcategories')

        try:
            subcategory = Category.objects.get(keyword=keyword)
        except Category.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Category, keyword)

        questiongroups = []
        conf_questiongroups = configuration.get('questiongroups', [])
        if (not isinstance(conf_questiongroups, list)
                or len(conf_questiongroups) == 0):
            raise ConfigurationErrorInvalidConfiguration(
                'questiongroups', 'list of dicts', 'subcategories')

        for conf_questiongroup in conf_questiongroups:
            questiongroups.append(
                QuestionnaireQuestiongroup(conf_questiongroup))

        self.keyword = keyword
        self.configuration = configuration
        self.questiongroups = questiongroups
        self.object = subcategory
        self.label = subcategory.get_translation('label')

    @staticmethod
    def merge_configurations(base, specific):
        """
        Merges two configurations of Subcategories into a single one.
        The base configuration is extended by the specific
        configuration.

        Questiongroups are identified by their keyword and merged.

        .. seealso::
            The merging of the configuration of questiongroups is
            handled by
            :func:`QuestionnaireQuestiongroup.merge_configurations`

        Args:
            ``base`` (dict): The configuration of the base Subcategory
            on which the specific configuration is based.

            ``specific`` (dict): The configuration of the specific
            Subcategory extending the base configuration.

        Returns:
            ``dict``. The merged configuration.
        """
        validate_type(
            base, dict, 'subcategories', 'list of dicts', 'categories')
        validate_type(
            specific, dict, 'subcategories', 'list of dicts', 'categories')

        merged_questiongroups = []
        base_questiongroups = base.get('questiongroups', [])
        specific_questiongroups = specific.get('questiongroups', [])

        if base_questiongroups:
            validate_type(
                base_questiongroups, list, 'questiongroups', 'list of dicts',
                'subcategories')
        validate_type(
            specific_questiongroups, list, 'questiongroups', 'list of dicts',
            'subcategories')

        # Collect all base questiongroup configurations and find eventual
        # specific configurations for these questiongroups
        for base_questiongroup in base_questiongroups:
            specific_questiongroup = find_dict_in_list(
                specific_questiongroups, 'keyword',
                base_questiongroup.get('keyword'))
            merged_questiongroups.append(
                QuestionnaireQuestiongroup.merge_configurations(
                    base_questiongroup, specific_questiongroup))

        # Collect all specific questiongroup configurations which are not
        # part of the base questiongroups
        for specific_questiongroup in specific_questiongroups:
            base_questiongroup = find_dict_in_list(
                base_questiongroups, 'keyword',
                specific_questiongroup.get('keyword'))
            if not base_questiongroup:
                merged_questiongroups.append(
                    QuestionnaireQuestiongroup.merge_configurations(
                        base_questiongroup, specific_questiongroup))

        base['questiongroups'] = merged_questiongroups
        return base

    def get_form(
            self, post_data=None, initial_data={}, show_translation=False):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of formsets of question groups, together
            forming a subcategory.
        """
        questionset_formsets = []
        for questiongroup in self.questiongroups:
            questionset_initial_data = initial_data.get(questiongroup.keyword)
            questionset_formsets.append(
                questiongroup.get_form(
                    post_data=post_data, initial_data=questionset_initial_data,
                    show_translation=show_translation))
        config = {
            'label': self.label,
        }
        return config, questionset_formsets

    def get_details(self, data={}):
        """
        Returns:
            ``string``. A rendered representation of the subcategory
            with its questiongroups.

            ``bool``. A boolean indicating whether the subcategory and
            its questiongroups have some data in them or not.
        """
        rendered_questiongroups = []
        has_content = False
        for questiongroup in self.questiongroups:
            questiongroup_data = data.get(questiongroup.keyword, [])
            if not is_empty_list_of_dicts(questiongroup_data):
                has_content = True
                rendered_questiongroups.append(
                    questiongroup.get_details(questiongroup_data))
        rendered = render_to_string(
            'details/subcategory.html', {
                'questiongroups': rendered_questiongroups,
                'label': self.label})
        return rendered, has_content


class QuestionnaireCategory(object):
    """
    A class representing the configuration of a Category of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'subcategories',
    ]

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Category. It needs to have the following
        format::

          {
            # The keyword of the category.
            "keyword": "CAT_KEYWORD",

            # A list of subcategories.
            "subcategories": [
              {
                # ...
              }
            ]
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/category`
        """
        validate_type(
            configuration, dict, 'categories', 'list of dicts', '-')
        validate_options(
            configuration, self.valid_options, QuestionnaireCategory)

        keyword = configuration.get('keyword')
        if not isinstance(keyword, str):
            raise ConfigurationErrorInvalidConfiguration(
                'keyword', 'str', 'categories')

        try:
            category = Category.objects.get(keyword=keyword)
        except Category.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Category, keyword)

        subcategories = []
        conf_subcategories = configuration.get('subcategories', [])
        if (not isinstance(conf_subcategories, list)
                or len(conf_subcategories) == 0):
            raise ConfigurationErrorInvalidConfiguration(
                'subcategories', 'list of dicts', 'categories')

        for conf_subcategory in conf_subcategories:
            subcategories.append(QuestionnaireSubcategory(conf_subcategory))

        self.keyword = keyword
        self.configuration = configuration
        self.subcategories = subcategories
        self.object = category
        self.label = category.get_translation('label')

    @staticmethod
    def merge_configurations(base, specific):
        """
        Merges two configurations of Categories into a single one. The
        base configuration is extended by the specific configuration.

        Subcategories are identified by their keyword and merged.

        .. seealso::
            The merging of the configuration of subcategories is handled
            by :func:`QuestionnaireSubcategory.merge_configurations`

        Args:
            ``base`` (dict): The configuration of the base Category on
            which the specific configuration is based.

            ``specific`` (dict): The configuration of the specific
            Category extending the base configuration.

        Returns:
            ``dict``. The merged configuration.
        """
        validate_type(base, dict, 'categories', 'list of dicts', '-')
        validate_type(specific, dict, 'categories', 'list of dicts', '-')

        merged_subcategories = []
        base_subcategories = base.get('subcategories', [])
        specific_subcategories = specific.get('subcategories', [])

        if base_subcategories:
            validate_type(
                base_subcategories, list, 'subcategories', 'list of dicts',
                'categories')
        validate_type(
            specific_subcategories, list, 'subcategories', 'list of dicts',
            'categories')

        # Collect all base subcategory configurations and find eventual
        # specific configurations for these subcategories
        for base_subcategory in base_subcategories:
            specific_subcategory = find_dict_in_list(
                specific_subcategories, 'keyword',
                base_subcategory.get('keyword'))
            merged_subcategories.append(
                QuestionnaireSubcategory.merge_configurations(
                    base_subcategory, specific_subcategory))

        # Collect all specific subcategory configurations which are not
        # part of the base subcategories
        for specific_subcategory in specific_subcategories:
            base_subcategory = find_dict_in_list(
                base_subcategories, 'keyword',
                specific_subcategory.get('keyword'))
            if not base_subcategory:
                merged_subcategories.append(
                    QuestionnaireSubcategory.merge_configurations(
                        base_subcategory, specific_subcategory))

        base['subcategories'] = merged_subcategories
        return base

    def validate_options(self, configuration):
        invalid_options = list(set(configuration) - set(self.valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], configuration, self)

    def get_form(
            self, post_data=None, initial_data={}, show_translation=False):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of a list of subcategory formsets.
        """
        subcategory_formsets = []
        for subcategory in self.subcategories:
            subcategory_formsets.append(
                subcategory.get_form(
                    post_data=post_data, initial_data=initial_data,
                    show_translation=show_translation))
        config = {
            'label': self.label
        }
        return config, subcategory_formsets

    def get_details(self, data={}, editable=False):
        rendered_subcategories = []
        with_content = 0
        for subcategory in self.subcategories:
            rendered_subcategory, has_content = subcategory.get_details(data)
            if has_content:
                rendered_subcategories.append(rendered_subcategory)
                with_content += 1
        rendered = render_to_string(
            'details/category.html', {
                'subcategories': rendered_subcategories,
                'label': self.label,
                'keyword': self.keyword,
                'editable': editable,
                'complete': with_content,
                'total': len(self.subcategories),
                'progress': with_content / len(self.subcategories) * 100,
                'edit_step_route': 'sample_questionnaire_new_step'
            })
        return rendered


class QuestionnaireConfiguration(object):
    """
    A class representing the configuration of a Questionnaire.

    .. seealso::
        For more information on the format and the configuration
        options, please refer to the documentation:
        :doc:`/configuration/questionnaire`
    """
    valid_options = [
        'categories',
    ]

    def __init__(self, keyword, configuration_object=None):
        self.keyword = keyword
        self.categories = []
        self.configuration_object = configuration_object
        if self.configuration_object is None:
            self.configuration_object = Configuration.get_active_by_code(
                self.keyword)
        self.configuration_error = None
        try:
            self.read_configuration()
        except Exception as e:
            if isinstance(e, ConfigurationError):
                self.configuration_error = e
            else:
                raise e

    def add_category(self, category):
        self.categories.append(category)

    def get_category(self, keyword):
        for category in self.categories:
            if category.keyword == keyword:
                return category
        return None

    def get_questiongroups(self):
        questiongroups = []
        for category in self.categories:
            for subcategory in category.subcategories:
                questiongroups.extend(subcategory.questiongroups)
        return questiongroups

    def get_questiongroup_by_keyword(self, keyword):
        for questiongroup in self.get_questiongroups():
            if questiongroup.keyword == keyword:
                return questiongroup
        return None

    def get_details(self, data={}, editable=False):
        rendered_categories = []
        for category in self.categories:
            rendered_categories.append(category.get_details(
                data, editable=editable))
        return rendered_categories

    def get_list_configuration(self):
        """
        Get the configuration for the list view of questionnaires. Loops
        through the questions to find those with the option
        ``list_position`` set. The returning list is sorted by this
        value.

        Returns:
            ``list``. A list of dicts where each dict consists of the
            following elements:

            - ``questiongroup``: The keyword of the questiongroup. Used
              to find the question in the questionnaire data.
            - ``key``: The keyword of the question, respectively of the
              Key of the question.
            - ``label``: The (translated) label of the question,
              respectively of the Key of the question.
            - ``position``: The value of ``list_position``, used to sort
              the list.
        """
        conf = []
        for questiongroup in self.get_questiongroups():
            for question in questiongroup.questions:
                if question.list_position is not None:
                    conf.append({
                        'questiongroup': questiongroup.keyword,
                        'key': question.keyword,
                        'label': question.label,
                        'position': question.list_position
                        })
        return sorted(conf, key=lambda k: k.get('position'))

    def get_list_data(self, questionnaires, details_route, current_locale):
        """
        Get the data for the list representation of questionnaires based
        on the list_configuration.

        .. seealso::
            :func:`get_list_configuration`

        Args:
            ``questionnaires`` (list): A list of
            :class:`questionnaire.models.Questionnaire` objects.

            ``details_route`` (str): The name of the route to be used
            for the links to the details page of each Questionnaire.

            ``current_locale`` (str): The current locale.

        Returns:
            ``tuple``. A tuple of tuples where the first element is the
            header and each following element represents a row of the
            list.
        """
        conf = self.get_list_configuration()

        # Header
        header_before_data = ['id']
        header_after_data = []
        list_header = []
        list_header.extend(header_before_data)
        list_header.extend([c['label'] for c in conf])
        list_header.extend(header_after_data)

        # Data
        list_data = [tuple(list_header)]
        for questionnaire in questionnaires:
            list_entry = [None] * len(list_header)
            list_entry[0] = '<a href="{}">{}</a>'.format(
                reverse(details_route, args=[questionnaire.get_id()]),
                questionnaire.get_id())
            for i, c in enumerate(conf):
                qg = questionnaire.data.get(c['questiongroup'], [])
                if len(qg) > 0:
                    entry = qg[0].get(c['key'])
                    if isinstance(entry, dict):
                        entry = entry.get(current_locale)
                    list_entry[i+len(header_before_data)] = entry
            list_data.append(tuple(list_entry))
        return tuple(list_data)

    def read_configuration(self):
        """
        This function reads an active configuration of a Questionnaire.
        If a configuration is found, it loads the configuration of all
        its categories.

        The configuration of the questionnaire needs to have the
        following format::

          {
            # See class QuestionnaireCategory for the format of categories.
            "categories": [
              # ...
            ]
          }

        .. seealso::
            :class:`configuration.configuration.QuestionnaireCategory`

        .. seealso::
            :doc:`/configuration/questionnaire`
        """
        if self.configuration_object is None:
            raise ConfigurationErrorNoConfigurationFound(self.keyword)

        specific_configuration = self.configuration_object.data
        base_configuration = {}
        if self.configuration_object.base_code:
            base_code = self.configuration_object.base_code
            base_configuration_object = Configuration.get_active_by_code(
                base_code)
            if base_configuration_object is None:
                raise ConfigurationErrorNoConfigurationFound(base_code)
            base_configuration = base_configuration_object.data

        self.configuration = QuestionnaireConfiguration.merge_configurations(
            base_configuration, specific_configuration)

        validate_options(
            self.configuration, self.valid_options, QuestionnaireConfiguration)

        conf_categories = self.configuration.get('categories')
        validate_type(
            conf_categories, list, 'categories', 'list of dicts', '-')

        for conf_category in conf_categories:
            self.add_category(QuestionnaireCategory(conf_category))

    @staticmethod
    def merge_configurations(base, specific):
        """
        Merges two configurations of Questionnaires into a single one.
        The base configuration is extended by the specific
        configuration.

        Categories are identified by their keyword and merged.

        .. seealso::
            The merging of the configuration of categories is handled by
            :func:`QuestionnaireCategory.merge_configurations`

        Args:
            ``base`` (dict): The configuration of the base
            Questionnaire on which the specific configuration is based.

            ``specific`` (dict): The configuration of the specific
            Questionnaire extending the base configuration.

        Returns:
            ``dict``. The merged configuration.
        """
        validate_type(base, dict, 'base', 'dict', '-')
        validate_type(specific, dict, 'base', 'dict', '-')

        merged_categories = []
        base_categories = base.get('categories', [])
        specific_categories = specific.get('categories', [])

        if base_categories:
            validate_type(
                base_categories, list, 'categories', 'list of dicts', '-')
        validate_type(
            specific_categories, list, 'categories', 'list of dicts', '-')

        # Collect all base category configurations and find eventual
        # specific configurations for these categories
        for base_category in base_categories:
            specific_category = find_dict_in_list(
                specific_categories, 'keyword', base_category.get('keyword'))
            merged_categories.append(
                QuestionnaireCategory.merge_configurations(
                    base_category, specific_category))

        # Collect all specific category configurations which are not
        # part of the base categories
        for specific_category in specific_categories:
            base_category = find_dict_in_list(
                base_categories, 'keyword', specific_category.get('keyword'))
            if not base_category:
                merged_categories.append(
                    QuestionnaireCategory.merge_configurations(
                        base_category, specific_category))

        base['categories'] = merged_categories
        return base


def validate_options(configuration, valid_options, obj):
    """
    Validate a configuration dict to check if it contains invalid
    options as keys.

    Args:
        ``configuration`` (dict): A configuration dictionary.

        ``valid_options`` (list): A list with possible options.

        ``obj`` (object): An object to indicate in the error message.

    Raises:
        :class:`qcat.errors.ConfigurationErrorInvalidOption`
    """
    invalid_options = list(set(configuration) - set(valid_options))
    if len(invalid_options) > 0:
        raise ConfigurationErrorInvalidOption(
            invalid_options[0], configuration, obj)


def validate_type(obj, type_, conf_name, type_name, parent_conf_name):
    """
    Validate a type of object.

    Args:
        ``obj`` (obj): The object to validate.

        ``type_`` (type): A Python type (e.g. ``list``, ``dict``).

        ``conf_name`` (str): The name of the configuration entry (used
        for the error message)

        ``type_name`` (str): The name of the expected type (used for the
        error message)

        ``parent_conf_name`` (str): The name of the parent configuration
        entry (used for the error message)

    Raises:
        :class:`qcat.errors.ConfigurationErrorInvalidConfiguration`
    """
    if not isinstance(obj, type_):
        raise ConfigurationErrorInvalidConfiguration(
            conf_name, type_name, parent_conf_name)


class RadioSelect(forms.RadioSelect):
    """
    A custom form class for a Radio Select field. Allows to overwrite
    the template used.
    """
    template_name = 'form/field/radio.html'


class MeasureSelect(forms.RadioSelect):
    template_name = 'form/field/measure.html'


class Checkbox(forms.CheckboxSelectMultiple):
    template_name = 'form/field/checkbox.html'


class ImageCheckbox(forms.CheckboxSelectMultiple):
    template_name = 'form/field/image_checkbox.html'

    def get_context_data(self):
        """
        Add the image paths to the context data so they are availabel
        within the template of the widget.
        """
        ctx = super(ImageCheckbox, self).get_context_data()
        ctx.update({
            'images': self.images,
            'conditional': self.conditional,
            'conditions': self.conditions,
        })
        return ctx


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True
