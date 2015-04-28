import floppyforms as forms
from django.forms import BaseFormSet, formset_factory
from django.template.loader import render_to_string, get_template
from django.template.base import TemplateDoesNotExist
from django.utils.translation import ugettext as _, get_language

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
    ConfigurationErrorInvalidQuestiongroupCondition,
    ConfigurationErrorNoConfigurationFound,
    ConfigurationErrorNotInDatabase,
    ConfigurationErrorTemplateNotFound,
)
from qcat.utils import (
    find_dict_in_list,
    is_empty_list_of_dicts,
)
from questionnaire.upload import (
    get_interchange_urls_by_identifier,
    get_url_by_identifier,
)


class BaseConfigurationObject(object):
    """
    This is the base class for all Questionnaire Configuration objects.
    """

    def __init__(self, parent_object, configuration):
        """
        Sets the following attributes for each configuration object:

            ``self.configuration``: The configuration dictionary.

            ``self.keyword``: The keyword identifier of the object.

            ``self.configuration_object``: The database configuration
                object

            ``self.configuration_keyword``: The code of the current
                configuration

            ``self.parent_object``: The parent configuration object.

            ``self.label``: The (translated) label.

            ``self.children``: The child configuration objects if
                available.
        """
        validate_type(
            configuration, dict, self.name_current, 'list of dicts',
            self.name_parent)
        self.configuration = configuration
        self.validate_options()

        keyword = self.configuration.get('keyword')
        if not isinstance(keyword, str):
            raise ConfigurationErrorInvalidConfiguration(
                'keyword', 'str', self.name_current)
        self.keyword = keyword

        if isinstance(self, (
                QuestionnaireSection, QuestionnaireCategory,
                QuestionnaireSubcategory)):
            try:
                self.configuration_object = Category.objects.get(
                    keyword=self.keyword)
            except Category.DoesNotExist:
                raise ConfigurationErrorNotInDatabase(Category, self.keyword)
        elif isinstance(self, QuestionnaireQuestiongroup):
            try:
                self.configuration_object = Questiongroup.objects.get(
                    keyword=self.keyword)
            except Questiongroup.DoesNotExist:
                raise ConfigurationErrorNotInDatabase(
                    Questiongroup, self.keyword)
        elif isinstance(self, QuestionnaireQuestion):
            try:
                self.configuration_object = Key.objects.get(
                    keyword=self.keyword)
            except Key.DoesNotExist:
                raise ConfigurationErrorNotInDatabase(Key, self.keyword)
        else:
            raise Exception('Unknown instance')

        self.configuration_keyword = parent_object.configuration_keyword
        self.parent_object = parent_object

        self.helptext = ''
        self.label = ''
        translation = self.configuration_object.translation
        if translation:
            self.helptext = translation.get_translation(
                'helptext', self.configuration_keyword)
            self.label = translation.get_translation(
                'label', self.configuration_keyword)

        # Should be at the bottom of the function
        children = []
        configuration_children = self.configuration.get(self.name_children)
        if configuration_children:
            if (not isinstance(configuration_children, list)
                    or len(configuration_children) == 0):
                raise ConfigurationErrorInvalidConfiguration(
                    self.name_children, 'list of dicts', self.name_current)
            for configuration_child in configuration_children:
                children.append(
                    self.Child(self, configuration_child))
            self.children = children

    def validate_options(self):
        """
        Validate a configuration dict to check if it contains invalid
        options as keys.

        Raises:
            :class:`qcat.errors.ConfigurationErrorInvalidOption`
        """
        invalid_options = list(
            set(self.configuration) - set(self.valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], self.configuration, self)

    @staticmethod
    def merge_configurations(obj, base_configuration, specific_configuration):
        """
        Merges two configuration dicts into a single one. The base
        configuration is extended by the specific configuration.

        Children are identified by their keyword and merged. The merging
        of the children is handled by the respective class.

        Args:
            ``obj`` (BaseConfigurationObject): A configuration object.

            ``base_configuration`` (dict): The base configuration on which the
            specific configuration is based.

            ``specific_configuration`` (dict): The specific configuration
            extending the base configuration.

        Returns:
            ``dict``. The merged configuration.
        """
        validate_type(
            base_configuration, dict, obj.name_current, dict, obj.name_parent)
        validate_type(
            specific_configuration, dict, obj.name_current, dict,
            obj.name_parent)

        merged_children = []
        base_children = base_configuration.get(obj.name_children, [])
        specific_children = specific_configuration.get(obj.name_children, [])

        if base_children:
            validate_type(
                base_children, list, obj.name_children, list, obj.name_current)
        validate_type(
            specific_children, list, obj.name_children, list, obj.name_current)

        # Collect all base configurations and find eventual specific
        # configurations for these children
        for base_child in base_children:
            specific_child = find_dict_in_list(
                specific_children, 'keyword', base_child.get('keyword'))
            merged_children.append(
                obj.Child.merge_configurations(
                    obj.Child, base_child.copy(), specific_child.copy()))

        # Collect all specific configurations which are not part of the
        # base children
        for specific_child in specific_children:
            base_child = find_dict_in_list(
                base_children, 'keyword', specific_child.get('keyword'))
            if not base_child:
                merged_children.append(specific_child.copy())

        if obj.name_children:
            base_configuration[obj.name_children] = merged_children
        else:
            base_configuration.update(specific_configuration)

        return base_configuration


class QuestionnaireQuestion(BaseConfigurationObject):
    """
    A class representing the configuration of a Question of the
    Questionnaire. A Question basically consists of the Key and optional
    Values (for Questions with predefined Answers)
    """
    valid_options = [
        'keyword',
        'in_list',
        'form_template',
        'view_template',
        'conditions',
        'conditional',
        'questiongroup_conditions',
        'max_length',
        'num_rows',
    ]
    valid_field_types = [
        'char',
        'text',
        'bool',
        'measure',
        'checkbox',
        'image_checkbox',
        'image',
        'select_type',
    ]
    translation_original_prefix = 'original_'
    translation_translation_prefix = 'translation_'
    translation_old_prefix = 'old_'
    value_image_path = 'assets/img/'
    name_current = 'questions'
    name_parent = 'questiongroups'
    name_children = ''
    Child = None

    def __init__(self, parent_object, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Question. It needs to have the following
        format::

          {
            # The keyword of the key of the question.
            "keyword": "KEY",

            # (optional)
            "in_list": true,

            # (optional)
            "form_template": "TEMPLATE_NAME",

            # (optional)
            "view_template": "TEMPLATE_NAME",

            # (optional)
            "conditional": true,

            # (optional)
            "conditions": [],

            # (optional)
            "questiongroup_conditions": [],

            # (optional)
            "max_length": 500,

            # (optional)
            "num_rows": 10,
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/questiongroup`

        Raises:
            :class:`qcat.errors.ConfigurationErrorInvalidConfiguration`,
            ``ConfigurationErrorNotInDatabase``.
        """
        super(QuestionnaireQuestion, self).__init__(
            parent_object, configuration)
        self.questiongroup = parent_object

        self.in_list = configuration.get('in_list', False)
        self.key_config = self.configuration_object.configuration

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

        self.view_template = configuration.get('view_template')

        self.max_length = configuration.get('max_length', None)
        self.num_rows = configuration.get('num_rows', 10)

        self.images = []
        self.choices = ()
        self.value_objects = []
        if self.field_type == 'bool':
            self.choices = ((1, _('Yes')), (0, _('No')))
        elif self.field_type in [
                'measure', 'checkbox', 'image_checkbox', 'select_type']:
            self.value_objects = self.configuration_object.values.all()
            if len(self.value_objects) == 0:
                raise ConfigurationErrorNotInDatabase(
                    self, '[values of key {}]'.format(self.keyword))
            if self.field_type in ['measure', 'select_type']:
                choices = [('', '-')]
            else:
                choices = []
            ordered_values = False
            for i, v in enumerate(self.value_objects):
                if v.order_value:
                    ordered_values = True
                if self.field_type in ['measure']:
                    choices.append((i+1, v.get_translation(
                        'label', self.configuration_keyword)))
                else:
                    choices.append((v.keyword, v.get_translation(
                        'label', self.configuration_keyword)))
                if self.field_type in ['image_checkbox']:
                    self.images.append('{}{}'.format(
                        self.value_image_path,
                        v.configuration.get('image_name')))
            if ordered_values is False:
                try:
                    choices = sorted(choices, key=lambda tup: tup[1])
                except TypeError:
                    pass
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

            # TODO
            # Check that the key exists in the same questiongroup.
            # cond_key_object = self.questiongroup.get_question_by_key_keyword(
            #     cond_key)
            # if cond_key_object is None:
            #     raise ConfigurationErrorInvalidCondition(
            #         condition,
            #         'Key "{}" is not in the same questiongroup'.format(
            #             cond_key))
            # if not (
            #         self.field_type == 'image_checkbox' and
            #         cond_key_object.field_type == 'image_checkbox'):
            #     raise ConfigurationErrorInvalidCondition(
            #         condition, 'Only valid for types "image_checkbox"')
            conditions.append((cond_value, cond_expression, cond_key))
        self.conditions = conditions

        questiongroup_conditions = []
        for questiongroup_condition in configuration.get(
                'questiongroup_conditions', []):
            try:
                cond_expression, cond_name = questiongroup_condition.split('|')
            except ValueError:
                raise ConfigurationErrorInvalidQuestiongroupCondition(
                    questiongroup_condition,
                    'Needs to have form "expression|name"')
            # Check the condition expression
            try:
                cond_expression = eval('{}{}'.format(0, cond_expression))
            except SyntaxError:
                raise ConfigurationErrorInvalidQuestiongroupCondition(
                    questiongroup_condition,
                    'Expression "{}" is not a valid Python condition'.format(
                        cond_expression))
            questiongroup_conditions.append(questiongroup_condition)

        self.questiongroup_conditions = questiongroup_conditions

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
            max_length = self.max_length
            if max_length is None:
                max_length = 200
            field = forms.CharField(
                label=self.label, widget=forms.TextInput(),
                required=self.required, max_length=max_length)
            translation_field = forms.CharField(
                label=self.label, widget=forms.TextInput(attrs=readonly_attrs),
                required=self.required, max_length=max_length)
        elif self.field_type == 'text':
            max_length = self.max_length
            if max_length is None:
                max_length = 500
            field = forms.CharField(
                label=self.label, widget=forms.Textarea(
                    attrs={'rows': self.num_rows}),
                required=self.required, max_length=max_length)
            translation_field = forms.CharField(
                label=self.label, widget=forms.Textarea(attrs=readonly_attrs),
                required=self.required)
        elif self.field_type == 'bool':
            widget = RadioSelect(choices=self.choices)
            field = forms.IntegerField(
                label=self.label, widget=widget,
                required=self.required)
        elif self.field_type == 'measure':
            widget = MeasureSelect()
            field = forms.ChoiceField(
                label=self.label, choices=self.choices, widget=widget,
                required=self.required, initial=self.choices[0][0])
        elif self.field_type == 'checkbox':
            widget = Checkbox()
            field = forms.MultipleChoiceField(
                label=self.label, widget=widget, choices=self.choices,
                required=self.required)
        elif self.field_type == 'image_checkbox':
            # Make the image paths available to the widget
            widget = ImageCheckbox()
            widget.images = self.images
            field = forms.MultipleChoiceField(
                label=self.label, widget=widget, choices=self.choices,
                required=self.required)
        elif self.field_type == 'image':
            formfields['file_{}'.format(self.keyword)] = forms.FileField(
                widget=ImageUpload(), required=self.required, label=self.label)
            field = forms.CharField(
                required=self.required, widget=forms.HiddenInput())
        elif self.field_type == 'select_type':
            widget = Select()
            widget.searchable = True
            field = forms.ChoiceField(
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
            widget.questiongroup_conditions = ','.join(
                self.questiongroup_conditions)

        return formfields, templates

    def get_details(self, data={}):
        value = data.get(self.keyword)
        if self.field_type in [
                'bool', 'measure', 'checkbox', 'image_checkbox',
                'select_type']:
            # Look up the labels for the predefined values
            if not isinstance(value, list):
                value = [value]
            values = self.lookup_choices_labels_by_keywords(value)
        if self.field_type in ['char']:
            rendered = render_to_string(
                'details/field/textinput.html', {
                    'key': self.label,
                    'value': value})
            return rendered
        elif self.field_type in ['text']:
            rendered = render_to_string(
                'details/field/textarea.html', {
                    'key': self.label,
                    'value': value})
            return rendered
        elif self.field_type in ['bool', 'select_type']:
            rendered = render_to_string(
                'details/field/textinput.html', {
                    'key': self.label,
                    'value': values[0]})
            return rendered
        elif self.field_type in ['measure']:
            template_name = 'measure_bar'
            if self.view_template:
                template_name = self.view_template
            template = 'details/field/{}.html'.format(template_name)
            level = None
            try:
                pos = [c[1] for c in self.choices].index(values[0])
                level = round(pos / len(self.choices) * 5)
            except ValueError:
                pass
            rendered = render_to_string(
                template, {
                    'key': self.label,
                    'value': values[0],
                    'level': level,
                })
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
        elif self.field_type in ['image']:
            value = get_url_by_identifier(value)
            rendered = render_to_string(
                'details/field/image.html', {
                    'key': self.label,
                    'value': value})
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


class QuestionnaireQuestiongroup(BaseConfigurationObject):
    """
    A class representing the configuration of a Questiongroup of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'questions',
        'max_num',
        'min_num',
        'questiongroup_condition',
        'view_template',
    ]
    default_template = 'default'
    default_min_num = 1
    name_current = 'questiongroups'
    name_parent = 'subcategories'
    name_children = 'questions'
    Child = QuestionnaireQuestion

    def __init__(self, parent_object, configuration):
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

            # (optional)
            "questiongroup_condition": "CONDITION_NAME",

            # (optional)
            "view_template": "VIEW_TEMPLATE",

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
        super(QuestionnaireQuestiongroup, self).__init__(
            parent_object, configuration)
        self.questions = self.children

        view_template = self.configuration.get('view_template', 'default')
        self.view_template = 'details/questiongroup/{}.html'.format(
            view_template)

        self.configuration = self.configuration_object.configuration
        self.configuration.update(configuration)
        self.validate_options()

        self.min_num = self.configuration.get('min_num', self.default_min_num)
        if not isinstance(self.min_num, int) or self.min_num < 1:
            raise ConfigurationErrorInvalidConfiguration(
                'min_num', 'integer >= 1', 'questiongroup')

        self.max_num = self.configuration.get('max_num', self.min_num)
        if not isinstance(self.max_num, int) or self.max_num < 1:
            raise ConfigurationErrorInvalidConfiguration(
                'max_num', 'integer >= 1', 'questiongroup')

        self.questiongroup_condition = self.configuration.get(
            'questiongroup_condition')

        # TODO
        self.required = False

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
            'label': self.label,
            'templates': templates,
            'questiongroup_condition': self.questiongroup_condition,
        }

        return config, FormSet(
            post_data, prefix=self.keyword, initial=initial_data)

    def get_details(self, data=[]):
        rendered_questions = []
        for d in data:
            for question in self.questions:
                if question.conditional:
                    continue
                rendered_questions.append(question.get_details(d))
        rendered = render_to_string(
            self.view_template, {
                'questions': rendered_questions,
            })
        return rendered

    def get_question_by_key_keyword(self, key_keyword):
        for question in self.questions:
            if question.keyword == key_keyword:
                return question
        return None


class QuestionnaireSubcategory(BaseConfigurationObject):
    """
    A class representing the configuration of a Subcategory of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'questiongroups',
        'subcategories',
    ]
    name_current = 'subcategories'
    name_parent = 'categories'
    name_children = 'questiongroups'
    Child = QuestionnaireQuestiongroup

    def __init__(self, parent_object, configuration):
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
        super(QuestionnaireSubcategory, self).__init__(
            parent_object, configuration)

        # A Subcategory can have further subcategories or questiongroups
        subcategories = []
        conf_subcategories = self.configuration.get('subcategories', [])
        for conf_subcategory in conf_subcategories:
            subcategories.append(
                QuestionnaireSubcategory(self, conf_subcategory))
        self.subcategories = subcategories

        questiongroups = []
        conf_questiongroups = self.configuration.get('questiongroups', [])
        for conf_questiongroup in conf_questiongroups:
            questiongroups.append(
                QuestionnaireQuestiongroup(self, conf_questiongroup))
        self.questiongroups = questiongroups

        if len(self.subcategories) > 0:
            self.children = self.subcategories
        else:
            self.children = self.questiongroups

    def get_form(
            self, post_data=None, initial_data={}, show_translation=False):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of formsets of question groups, together
            forming a subcategory.
        """
        formsets = []
        config = {
            'label': self.label,
        }
        for questiongroup in self.questiongroups:
            questionset_initial_data = initial_data.get(questiongroup.keyword)
            formsets.append(
                questiongroup.get_form(
                    post_data=post_data, initial_data=questionset_initial_data,
                    show_translation=show_translation))
            config['next_level'] = 'questiongroups'
        for subcategory in self.subcategories:
            formsets.append(
                subcategory.get_form(
                    post_data=post_data, initial_data=initial_data,
                    show_translation=show_translation))
            config['next_level'] = 'subcategories'
        return config, formsets

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
        subcategories = []
        for subcategory in self.subcategories:
            sub_rendered, sub_has_content = subcategory.get_details(data=data)
            if sub_has_content:
                subcategories.append(sub_rendered)
                has_content = True
        rendered = render_to_string(
            'details/subcategory.html', {
                'questiongroups': rendered_questiongroups,
                'subcategories': subcategories,
                'label': self.label})
        return rendered, has_content


class QuestionnaireCategory(BaseConfigurationObject):
    """
    A class representing the configuration of a Category of the
    Questionnaire.
    """
    valid_options = [
        'keyword',
        'subcategories',
        'view_template',
        'use_raw_data',
        'with_metadata',
        'include_toc',
    ]
    name_current = 'categories'
    name_parent = 'sections'
    name_children = 'subcategories'
    Child = QuestionnaireSubcategory

    def __init__(self, parent_object, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Category. It needs to have the following
        format::

          {
            # The keyword of the category.
            "keyword": "CAT_KEYWORD",

            # (optional)
            "view_template": "VIEW_TEMPLATE",

            # (optional)
            "use_raw_data": true,

            # (optional)
            "with_metadata": true,

            # (optional)
            "include_toc": true,

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
        super(QuestionnaireCategory, self).__init__(
            parent_object, configuration)
        self.subcategories = self.children

        view_template = self.configuration.get('view_template', 'default')
        self.view_template = 'details/category/{}.html'.format(view_template)

        self.use_raw_data = self.configuration.get(
            'use_raw_data', False) is True
        self.with_metadata = self.configuration.get(
            'with_metadata', False) is True
        self.include_toc = self.configuration.get('include_toc', False) is True

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

    def get_details(
            self, data={}, editable=False,
            edit_step_route='', questionnaire_object=None):
        rendered_subcategories = []
        with_content = 0
        raw_data = {}
        metadata = {}
        for subcategory in self.subcategories:
            rendered_subcategory, has_content = subcategory.get_details(data)
            if has_content:
                rendered_subcategories.append(rendered_subcategory)
                with_content += 1
            if self.use_raw_data is True:
                raw_data = self.get_raw_category_data(data)
            if self.with_metadata is True and questionnaire_object is not None:
                metadata = questionnaire_object.get_metadata()

        toc_content = []
        if self.include_toc:
            toc_content = self.parent_object.parent_object.get_toc_data()

        return render_to_string(
            self.view_template, {
                'subcategories': rendered_subcategories,
                'raw_data': raw_data,
                'metadata': metadata,
                'label': self.label,
                'keyword': self.keyword,
                'editable': editable,
                'complete': with_content,
                'total': len(self.subcategories),
                'progress': with_content / len(self.subcategories) * 100,
                'edit_step_route': edit_step_route,
                'configuration_name': self.configuration_keyword,
                'toc_content': tuple(toc_content),
            })

    def get_raw_category_data(self, questionnaire_data):
        """
        Return only the raw data of a category. The entire questionnaire
        data is scanned for the questiongroups belonging to the current
        category. Only the data of these questiongroups is then
        returned as a flat dict.

        .. important::
            This function may return unexpected outputs when used on
            categories with repeating questiongroups or with keys having
            the same keyword.

        Args:
            ``questionnaire_data`` (dict): The questionnaire data
            dictionary.

        Returns:
            ``dict``. A flat dictionary with only the keys and values of
            the current category.
        """
        raw_category_data = {}
        for subcategory in self.subcategories:
            for questiongroup in subcategory.questiongroups:
                questiongroups_data = questionnaire_data.get(
                    questiongroup.keyword, {})
                for question in questiongroup.questions:
                    for questiongroup_data in questiongroups_data:
                        question_data = questiongroup_data.get(
                            question.keyword)
                        raw_category_data[question.keyword] = question_data
        return raw_category_data


class QuestionnaireSection(BaseConfigurationObject):
    """
    A class representing the configuration of a Section of the
    Questionnaire.
    """
    valid_options = [
        'categories',
        'keyword',
        'view_template',
        'include_toc',
    ]
    name_current = 'sections'
    name_parent = None
    name_children = 'categories'
    Child = QuestionnaireCategory

    def __init__(self, parent_object, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Section. It needs to have the following
        format::

          {
            # The keyword of the section.
            "keyword": "SECTION_KEYWORD",

            # (optional)
            "view_template": "VIEW_TEMPLATE",

            # (optional)
            "include_toc": true,

            # A list of categories.
            "categories": [
              {
                # ...
              }
            ]
          }

        .. seealso::
            For more information on the format and the configuration
            options, please refer to the documentation:
            :doc:`/configuration/section`
        """
        super(QuestionnaireSection, self).__init__(
            parent_object, configuration)
        self.categories = self.children

        view_template = self.configuration.get('view_template', 'default')
        self.view_template = 'details/section/{}.html'.format(view_template)

        self.include_toc = self.configuration.get('include_toc', False) is True

    def get_details(
            self, data={}, editable=False, edit_step_route='',
            questionnaire_object=None):

        rendered_categories = []
        for category in self.categories:
            rendered_categories.append(category.get_details(
                data, editable=editable, edit_step_route=edit_step_route,
                questionnaire_object=questionnaire_object))

        toc_content = []
        if self.include_toc:
            toc_content = self.parent_object.get_toc_data()

        return render_to_string(self.view_template, {
            'label': self.label,
            'keyword': self.keyword,
            'categories': rendered_categories,
            'toc_content': toc_content,
        })


class QuestionnaireConfiguration(BaseConfigurationObject):
    """
    A class representing the configuration of a Questionnaire.

    .. seealso::
        For more information on the format and the configuration
        options, please refer to the documentation:
        :doc:`/configuration/questionnaire`
    """
    valid_options = [
        'sections',
    ]
    name_current = '-'
    name_parent = '-'
    name_children = 'sections'
    Child = QuestionnaireSection

    def __init__(self, keyword, configuration_object=None):
        self.keyword = keyword
        self.configuration_keyword = keyword
        self.sections = []
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
        for section in self.sections:
            for category in section.categories:
                if category.keyword == keyword:
                    return category
        return None

    def get_questiongroups(self):
        def unnest_questiongroups(nested):
            ret = []
            try:
                for child in nested.children:
                    if not isinstance(child, QuestionnaireQuestiongroup):
                        ret.extend(unnest_questiongroups(child))
                    else:
                        ret.append(child)
            except AttributeError:
                pass
            return ret
        return unnest_questiongroups(self)

    def get_questiongroup_by_keyword(self, keyword):
        for questiongroup in self.get_questiongroups():
            if questiongroup.keyword == keyword:
                return questiongroup
        return None

    def get_details(
            self, data={}, editable=False, edit_step_route='',
            questionnaire_object=None):
        rendered_sections = []
        for section in self.sections:
            rendered_sections.append(section.get_details(
                data, editable=editable, edit_step_route=edit_step_route,
                questionnaire_object=questionnaire_object))
        return rendered_sections

    def get_toc_data(self):
        sections = []
        for section in self.sections:
            categories = []
            for category in section.categories:
                categories.append((category.keyword, category.label))
            sections.append(
                (section.keyword, section.label, tuple(categories)))
        return tuple(sections)

    def get_image_data(self, data):
        """
        Return image data from outside the category. Loops through all
        the fields to find the questiongroups containing images. For all
        these, basic information about the images are collected and
        returned as a list of dictionaries.

        Args:
            ``data`` (dict): A questionnaire data dictionary.

        Returns:
            ``list``. A list of dictionaries for each image. Each
            dictionary has the following entries:

            - ``image``: The URL of the original image.

            - ``interchange``: The data which can be used for the
              interchange of images.

            - ``caption``: The caption of the image. Corresponds to
              field ``image_caption``.

            - ``date_location``: The date and location of the image.
              Corresponds to field ``image_date_location``.

            - ``photographer``: The photographer of the image.
              Corresponds to field ``image_photographer``.
        """
        image_questiongroups = []
        for questiongroup in self.get_questiongroups():
            for question in questiongroup.questions:
                if question.field_type == 'image' and data.get(
                        questiongroup.keyword) is not None:
                    image_questiongroups.extend(
                        data.get(questiongroup.keyword))

        images = []
        for image in image_questiongroups:
            images.append({
                'image': get_url_by_identifier(image.get('image')),
                'interchange': get_interchange_urls_by_identifier(
                    image.get('image')),
                'caption': image.get('image_caption'),
                'date_location': image.get('image_date_location'),
                'photographer': image.get('image_photographer')
            })
        return images

    def get_list_data(self, questionnaires):
        """
        Get the data for the list representation of questionnaires.
        Which questions are shown depends largely on the option
        ``in_list`` of the question configuration. Additionally, some
        meta information about the questionnaire are returned.

        Args:
            ``questionnaires`` (list): A list of
            :class:`questionnaire.models.Questionnaire` objects.

        Returns:
            ``list``. A list of dicts. The data of each questionnaire is
            stored as a dict where the key is either the keyword of the
            question to appear in the list or a predefined keyword. Such
            predefined keywords are:

                - ``id``: The internal id of the questionnaire.

                - ``image``: The URL of the main image (default format).
        """
        from questionnaire.utils import (
            get_questionnaire_data_in_single_language,
        )

        # Collect which keys are to be shown in the list.
        list_configuration = []
        for questiongroup in self.get_questiongroups():
            for question in questiongroup.questions:
                if question.in_list is True:
                    list_configuration.append((
                        questiongroup.keyword, question.keyword,
                        question.field_type))

        questionnaire_values = []
        for questionnaire in questionnaires:
            data = get_questionnaire_data_in_single_language(
                questionnaire.data, get_language())
            questionnaire_value = {}
            for list_entry in list_configuration:
                for question_data in data.get(list_entry[0], []):
                    key = list_entry[1]
                    value = question_data.get(list_entry[1])
                    if list_entry[2] == 'image':
                        key = 'image'
                        value = get_url_by_identifier(value, 'default')
                    if list_entry[2] in [
                            'bool', 'measure', 'checkbox', 'image_checkbox',
                            'select_type']:
                        # Look up the labels for the predefined values
                        if not isinstance(value, list):
                            value = [value]
                        qg = self.get_questiongroup_by_keyword(list_entry[0])
                        if qg is None:
                            break
                        k = qg.get_question_by_key_keyword(list_entry[1])
                        if k is None:
                            break
                        values = k.lookup_choices_labels_by_keywords(value)
                        if list_entry[2] in ['bool', 'measure', 'select_type']:
                            value = values[0]
                    questionnaire_value[key] = value

            configurations = [
                c.code for c in questionnaire.configurations.all()]

            questionnaire_value.update({
                'id': questionnaire.id,
                'configurations': configurations,
                'native_configuration': self.keyword in configurations,
            })
            questionnaire_value.update(questionnaire.get_metadata())
            questionnaire_values.append(questionnaire_value)

        return questionnaire_values

    def read_configuration(self):
        """
        This function reads an active configuration of a Questionnaire.
        If a configuration is found, it loads the configuration of all
        its sections.

        The configuration of the questionnaire needs to have the
        following format::

          {
            # See class QuestionnaireSection for the format of sections.
            "sections": [
              # ...
            ]
          }

        .. seealso::
            :class:`configuration.configuration.QuestionnaireSection`

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

        self.configuration = self.merge_configurations(
            self, base_configuration, specific_configuration)
        self.validate_options()

        conf_sections = self.configuration.get('sections')
        validate_type(
            conf_sections, list, 'sections', 'list of dicts', '-')

        for conf_section in conf_sections:
            self.sections.append(QuestionnaireSection(self, conf_section))
        self.children = self.sections


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

    def get_context_data(self):
        """
        Add the questiongroup conditions to the context data so they are
        available within the template of the widget.
        """
        ctx = super(RadioSelect, self).get_context_data()
        ctx.update({
            'questiongroup_conditions': self.questiongroup_conditions,
        })
        return ctx


class Select(forms.Select):
    template_name = 'form/field/select.html'

    def get_context_data(self):
        """
        Add a variable (searchable or not) to the context data so it is
        available within the template of the widget.
        """
        ctx = super(Select, self).get_context_data()
        ctx.update({
            'searchable': self.searchable,
        })
        return ctx


class MeasureSelect(forms.RadioSelect):
    template_name = 'form/field/measure.html'

    def get_context_data(self):
        """
        Add the questiongroup conditions to the context data so they are
        available within the template of the widget.
        """
        ctx = super(MeasureSelect, self).get_context_data()
        ctx.update({
            'questiongroup_conditions': self.questiongroup_conditions,
        })
        return ctx


class Checkbox(forms.CheckboxSelectMultiple):
    template_name = 'form/field/checkbox.html'

    def get_context_data(self):
        """
        Add the questiongroup conditions to the context data so they are
        available within the template of the widget.
        """
        ctx = super(Checkbox, self).get_context_data()
        ctx.update({
            'questiongroup_conditions': self.questiongroup_conditions,
        })
        return ctx


class ImageCheckbox(forms.CheckboxSelectMultiple):
    template_name = 'form/field/image_checkbox.html'

    def get_context_data(self):
        """
        Add the image paths to the context data so they are available
        within the template of the widget.
        """
        ctx = super(ImageCheckbox, self).get_context_data()
        ctx.update({
            'images': self.images,
            'conditional': self.conditional,
            'conditions': self.conditions,
        })
        return ctx


class ImageUpload(forms.FileInput):
    template_name = 'form/field/image_upload.html'


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = True
