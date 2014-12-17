from django import forms

from configuration.models import Category, Key
from qcat.errors import (
    ConfigurationErrorNotInDatabase,
    ConfigurationErrorInvalidOption,
)

LOCALE = 'en'  # TODO: Locale needed


def read_configuration(code):
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
                questionset = QuestionnaireQuestionset(qgroup.get('keyword'))
                for q in qgroup.get('questions', []):
                    try:
                        key = Key.objects.get(keyword=q.get('key'))
                    except Key.DoesNotExist:
                        raise ConfigurationErrorNotInDatabase(
                            Key, q.get('key'))
                    questionset.add_question(QuestionnaireQuestion(key))
                questionnaire_subcategory.add_questionset(questionset)
            questionnaire_category.add_subcategory(questionnaire_subcategory)
    return questionnaire_category


class QuestionnaireQuestion(object):

    def __init__(self, key):
        self.keyword = key.keyword
        self.label = key.get_translation(LOCALE)  # TODO: locale needed
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


class QuestionnaireQuestionset(object):

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


class QuestionnaireSubcategory(object):

    def __init__(self, subcategory):
        self.keyword = subcategory.keyword
        self.label = subcategory.get_translation(LOCALE)  # TODO: locale needed
        self.questionsets = []

    def add_questionset(self, questionset):
        self.questionsets.append(questionset)

    def get_form(self, data=None):
        """
        Returns:
            ``dict``. A dict with configuration elements, namely ``label``.
            ``list``. A list of formsets of question groups, together
            forming a subcategory.
        """
        questionset_formsets = []
        for questionset in self.questionsets:
            questionset_formsets.append(questionset.get_form(data))
        config = {
            'label': self.label
        }
        return config, questionset_formsets


class QuestionnaireCategory(object):

    def __init__(self, category):
        self.keyword = category.keyword
        self.label = category.get_translation(LOCALE)  # TODO: locale needed
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
