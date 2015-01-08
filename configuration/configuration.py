from django import forms
from django.template.loader import render_to_string

from configuration.models import (
    Category,
    Configuration,
    Key,
)
from qcat.errors import (
    ConfigurationErrorInvalidConfiguration,
    ConfigurationErrorInvalidOption,
    ConfigurationErrorNoConfigurationFound,
    ConfigurationErrorNotInDatabase,
)


class QuestionnaireQuestion(object):
    """
    A class representing the configuration of a Question of the
    Questionnaire. A Question basically consists of the Key and optional
    Values (for Questions with predefined Answers)
    """

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a dict containing the
        configuration of the Question. It needs to have the following
        format::

          {
            # The key of the question.
            "key": "KEY"
          }

        .. seealso::
            :doc:`/configuration/questionnaire`

        Throws:
            ``ConfigurationErrorInvalidConfiguration``,
            ``ConfigurationErrorNotInDatabase``.
        """
        valid_options = [
            'key',
        ]

        if not isinstance(configuration, dict):
            raise ConfigurationErrorInvalidConfiguration(
                'questions', 'list of dicts', 'questions')

        invalid_options = list(set(configuration) - set(valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], configuration, self)

        key = configuration.get('key')
        if not isinstance(key, str):
            raise ConfigurationErrorInvalidConfiguration(
                'key', 'str', 'questions')

        try:
            key = Key.objects.get(keyword=key)
        except Key.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Key, key)

        self.key_object = key
        self.key_config = key.data
        self.field_type = self.key_config.get('type', 'char')
        self.label = key.get_translation()
        self.keyword = key

    def get_form(self):
        """
        Returns:
            ``forms.Field``. The form field for a single question, for
            example a text input field or a dropdown field.
        """
        if self.field_type == 'char':
            return forms.CharField(label=self.label)
        elif self.field_type == 'text':
            return forms.CharField(label=self.label, widget=forms.Textarea)
        else:
            raise ConfigurationErrorInvalidOption(
                self.field_type, 'type', self)

    def render_readonly_form(self, data={}):
        if self.field_type in ['char', 'text']:
            d = data.get(self.keyword)
            rendered = render_to_string(
                'unccd/questionnaire/readonly/textinput.html', {
                    'key': self.label,
                    'value': d})
            return rendered
        else:
            raise ConfigurationErrorInvalidOption(
                self.field_type, 'type', self)


class QuestionnaireQuestiongroup(object):
    """
    A class representing the configuration of a Questiongroup of the
    Questionnaire.
    """

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a dict containing the
        configuration of the Questiongroup. It needs to have the
        following format::

          {
            # The keyword of the questiongroup.
            "keyword": "QUESTIONGROUP_KEYWORD",

            # See class QuestionnaireQuestion for the format of
            # questions.
            "questions": [
              # ...
            ]
          }

        .. seealso::
            :class:`configuration.configuration.QuestionnaireQuestion`

        .. seealso::
            :doc:`/configuration/questionnaire`

        Throws:
            ``ConfigurationErrorInvalidConfiguration``.
        """
        valid_options = [
            'keyword',
            'questions',
        ]

        if not isinstance(configuration, dict):
            raise ConfigurationErrorInvalidConfiguration(
                'questiongroups', 'list of dicts', 'subcategories')

        invalid_options = list(set(configuration) - set(valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], configuration, self)

        keyword = configuration.get('keyword')
        if not isinstance(keyword, str):
            raise ConfigurationErrorInvalidConfiguration(
                'keyword', 'str', 'questiongroups')

        questions = []
        conf_questions = configuration.get('questions', [])
        if (not isinstance(conf_questions, list) or len(conf_questions) == 0):
            raise ConfigurationErrorInvalidConfiguration(
                'questions', 'list of dicts', 'questiongroups')

        for conf_question in conf_questions:
            questions.append(QuestionnaireQuestion(conf_question))

        self.keyword = keyword
        self.configuration = configuration
        self.questions = questions

        # TODO
        self.required = False

    def get_form(self, post_data=None, initial_data=None):
        """
        Returns:
            ``forms.formset_factory``. A formset consisting of one or
            more form fields representing a set of questions belonging
            together and which can possibly be repeated multiple times.
        """
        formfields = {}
        for f in self.questions:
            formfields[f.keyword] = f.get_form()
        Form = type('Form', (forms.Form,), formfields)
        if self.required is True:
            FormSet = forms.formset_factory(
                Form, formset=RequiredFormSet, max_num=1)
        else:
            FormSet = forms.formset_factory(Form, max_num=1)

        if initial_data and len(initial_data) == 1 and initial_data[0] == {}:
            initial_data = None

        return FormSet(post_data, prefix=self.keyword, initial=initial_data)

    def render_readonly_form(self, data=[]):
        rendered_questions = []
        for question in self.questions:
            for d in data:
                rendered_questions.append(question.render_readonly_form(d))
        rendered = render_to_string(
            'unccd/questionnaire/readonly/questiongroup.html', {
                'questions': rendered_questions})
        return rendered


class QuestionnaireSubcategory(object):
    """
    A class representing the configuration of a Subcategory of the
    Questionnaire.
    """

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a dict containing the
        configuration of the Subcategory. It needs to have the following
        format::

          {
            # The keyword of the subcategory.
            "keyword": "SUBCAT_KEYWORD",

            # See class QuestionnaireQuestiongroup for the format of
            # questiongroups.
            "questiongroups": [
              # ...
            ]
          }

        .. seealso::
            :class:`configuration.configuration.QuestionnaireQuestiongroup`

        .. seealso::
            :doc:`/configuration/questionnaire`

        Throws:
            ``ConfigurationErrorInvalidConfiguration``,
            ``ConfigurationErrorNotInDatabase``.
        """
        valid_options = [
            'keyword',
            'questiongroups',
        ]

        if not isinstance(configuration, dict):
            raise ConfigurationErrorInvalidConfiguration(
                'subcategories', 'list of dicts', 'categories')

        invalid_options = list(set(configuration) - set(valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], configuration, self)

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
        self.label = subcategory.get_translation()

    def get_form(self, post_data=None, initial_data={}):
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
                questiongroup.get_form(post_data, questionset_initial_data))
        config = {
            'label': self.label
        }
        return config, questionset_formsets

    def render_readonly_form(self, data={}):
        rendered_questiongroups = []
        for questiongroup in self.questiongroups:
            questiongroup_data = data.get(questiongroup.keyword, [])
            rendered_questiongroups.append(
                questiongroup.render_readonly_form(questiongroup_data))
        rendered = render_to_string(
            'unccd/questionnaire/readonly/subcategory.html', {
                'questiongroups': rendered_questiongroups,
                'label': self.label})
        return rendered


class QuestionnaireCategory(object):
    """
    A class representing the configuration of a Category of the
    Questionnaire.
    """

    def __init__(self, configuration):
        """
        Parameter ``configuration`` is a ``dict`` containing the
        configuration of the Category. It needs to have the following
        format::

          {
            # The keyword of the category.
            "keyword": "CAT_KEYWORD",

            # See class QuestionnaireSubcategory for the format of
            # subcategories.
            "subcategories": [
              # ...
            ]
          }

        .. seealso::
            :class:`configuration.configuration.QuestionnaireSubcategory`

        .. seealso::
            :doc:`/configuration/questionnaire`

        Throws:
            ``ConfigurationErrorInvalidConfiguration``,
            ``ConfigurationErrorNotInDatabase``.
        """
        valid_options = [
            'keyword',
            'subcategories',
        ]

        if not isinstance(configuration, dict):
            raise ConfigurationErrorInvalidConfiguration(
                'categories', 'list of dicts', '-')

        invalid_options = list(set(configuration) - set(valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], configuration, self)

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
        self.label = category.get_translation()

    def get_form(self, post_data=None, initial_data={}):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of a list of subcategory formsets.
        """
        subcategory_formsets = []
        for subcategory in self.subcategories:
            subcategory_formsets.append(
                subcategory.get_form(post_data, initial_data))
        config = {
            'label': self.label
        }
        return config, subcategory_formsets

    def render_readonly_form(self, data={}):
        rendered_subcategories = []
        for subcategory in self.subcategories:
            rendered_subcategories.append(
                subcategory.render_readonly_form(data))
        rendered = render_to_string(
            'unccd/questionnaire/readonly/category.html', {
                'subcategories': rendered_subcategories,
                'label': self.label,
                'keyword': self.keyword})
        return rendered


class QuestionnaireConfiguration(object):
    """
    TODO
    """

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
            self.configuration_error = e
        # if keyword is None:
        #     self.valid_configuration = False
        # else:
        #     self.read_configuration()

    def add_category(self, category):
        self.categories.append(category)

    def get_category(self, keyword):
        for category in self.categories:
            if category.keyword == keyword:
                return category
        return None

    def render_readonly_form(self, data={}):
        rendered_categories = []
        for category in self.categories:
            rendered_categories.append(category.render_readonly_form(data))
        return rendered_categories

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

        Throws:
            ``ConfigurationErrorInvalidConfiguration``,
            ``ConfigurationErrorNoConfigurationFound``.
        """
        if self.configuration_object is None:
            raise ConfigurationErrorNoConfigurationFound(self.keyword)

        valid_options = [
            'categories',
        ]

        self.configuration = self.configuration_object.data

        invalid_options = list(set(self.configuration) - set(valid_options))
        if len(invalid_options) > 0:
            raise ConfigurationErrorInvalidOption(
                invalid_options[0], self.configuration, self)

        conf_categories = self.configuration.get('categories', [])
        if not isinstance(conf_categories, list) or len(conf_categories) == 0:
            raise ConfigurationErrorInvalidConfiguration(
                'categories', 'list of dicts', '-')
        for conf_category in conf_categories:

            self.add_category(QuestionnaireCategory(conf_category))


class RequiredFormSet(forms.BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
