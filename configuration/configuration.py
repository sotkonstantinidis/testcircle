from django import forms
from django.template.loader import render_to_string

from configuration.models import Category, Key
from qcat.errors import (
    ConfigurationErrorNotInDatabase,
    ConfigurationErrorInvalidOption,
)


def read_configuration(questionnaire_configuration, code):
    conf = {
        'categories': [
            {
                'keyword': 'cat_1',
                'subcategories': [
                    {
                        'keyword': 'subcat_1_1',
                        'questiongroups': [
                            {
                                'keyword': 'qg_1',
                                'questions': [
                                    {
                                        'key': 'key_1'
                                    }, {
                                        'key': 'key_3'
                                    }
                                ]
                            }, {
                                'keyword': 'qg_2',
                                'questions': [
                                    {
                                        'key': 'key_2'
                                    }
                                ]
                            }
                        ]
                    }, {
                        'keyword': 'subcat_1_2',
                        'questiongroups': [
                            {
                                'keyword': 'qg_3',
                                'questions': [
                                    {
                                        'key': 'key_4'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }, {
                'keyword': 'cat_2',
                'subcategories': [
                    {
                        'keyword': 'subcat_2_1',
                        'questiongroups': [
                            {
                                'keyword': 'qg_4',
                                'questions': [
                                    {
                                        'key': 'key_5'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    for cat in conf.get('categories', []):
        try:
            category = Category.objects.get(keyword=cat.get('keyword'))
        except Category.DoesNotExist:
            raise ConfigurationErrorNotInDatabase(Category, cat.get('keyword'))
        questionnaire_category = QuestionnaireCategory(category)
        for subcat in cat.get('subcategories', []):
            try:
                subcategory = Category.objects.get(
                    keyword=subcat.get('keyword'))
            except Category.DoesNotExist:
                raise ConfigurationErrorNotInDatabase(
                    Category, subcat.get('keyword'))
            questionnaire_subcategory = QuestionnaireSubcategory(subcategory)
            for qgroup in subcat.get('questiongroups', []):
                questiongroup = QuestionnaireQuestiongroup(
                    qgroup.get('keyword'))
                for q in qgroup.get('questions', []):
                    try:
                        key = Key.objects.get(keyword=q.get('key'))
                    except Key.DoesNotExist:
                        raise ConfigurationErrorNotInDatabase(
                            Key, q.get('key'))
                    questiongroup.add_question(QuestionnaireQuestion(key))
                questionnaire_subcategory.add_questionset(questiongroup)
            questionnaire_category.add_subcategory(questionnaire_subcategory)
        questionnaire_configuration.add_category(questionnaire_category)


class QuestionnaireQuestion(object):

    def __init__(self, key):
        self.keyword = key.keyword
        self.label = key.get_translation()
        config = key.data
        self.field_type = config.get('type', 'char')

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
        if self.field_type == 'char':
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

    def __init__(self, keyword):
        self.keyword = keyword
        self.questions = []

    def add_question(self, question):
        self.questions.append(question)

    def get_form(self, data=None):
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
        FormSet = forms.formset_factory(Form, max_num=1)

        return FormSet(data, prefix=self.keyword)

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

    def __init__(self, subcategory):
        self.keyword = subcategory.keyword
        self.label = subcategory.get_translation()
        self.questiongroups = []

    def add_questionset(self, questiongroup):
        self.questiongroups.append(questiongroup)

    def get_form(self, data=None):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of formsets of question groups, together
            forming a subcategory.
        """
        questionset_formsets = []
        for questiongroup in self.questiongroups:
            questionset_formsets.append(questiongroup.get_form(data))
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

    def __init__(self, category):
        self.keyword = category.keyword
        self.label = category.get_translation()
        self.subcategories = []

    def add_subcategory(self, subcategory):
        self.subcategories.append(subcategory)

    def get_form(self, data=None):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of a list of subcategory formsets.
        """
        subcategory_formsets = []
        for subcategory in self.subcategories:
            subcategory_formsets.append(subcategory.get_form(data))
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

    def __init__(self, keyword):
        self.keyword = keyword
        self.categories = []
        read_configuration(self, keyword)

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
