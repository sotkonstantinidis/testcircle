from django import forms
from configuration.models import Key


def read_configuration():
    conf = {
        'categories': [
            {
                'keyword': 'cat_1',
                'subcategories': [
                    {
                        'keyword': 'subcat_1',
                        'questiongroups': [
                            {
                                'keyword': 'qg_1',
                                'questions': [
                                    {
                                        'key': 'key_1'
                                    }
                                ]
                            }, {
                                'keyword': 'qg_2',
                                'questions': [
                                    {
                                        'key': 'key_3'
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
        category = Category(cat.get('keyword'))
        for subcat in cat.get('subcategories', []):
            subcategory = Subcategory(subcat.get('keyword'))
            for qgroup in subcat.get('questiongroups', []):
                questionset = Questionset(qgroup.get('keyword'))
                for q in qgroup.get('questions', []):
                    key = Key.objects.get(keyword=q.get('key'))
                    field = Question(key)
                    questionset.add_question(field)
                subcategory.add_questionset(questionset)
            category.add_subcategory(subcategory)
    return category


class Question(object):

    def __init__(self, key):
        self.key = key
        self.keyword = key.keyword
        config = key.data
        self.field_type = config.get('type', 'char')

    def get_form(self):
        if self.field_type == 'char':
            return forms.CharField()
        else:
            raise Exception('To DO')


class Questionset(object):

    def __init__(self, keyword):
        self.keyword = keyword
        self.questions = []

    def add_question(self, question):
        self.questions.append(question)

    def get_form(self, data=None):
        formfields = {}
        for f in self.questions:
            formfields[f.keyword] = f.get_form()
        Form = type('Form', (forms.Form,), formfields)
        FormSet = forms.formset_factory(Form, max_num=1)

        return FormSet(data, prefix=self.keyword)


class Subcategory(object):

    def __init__(self, keyword):
        self.keyword = keyword
        self.questionsets = []

    def add_questionset(self, questionset):
        self.questionsets.append(questionset)


class Category(object):

    def __init__(self, keyword):
        self.keyword = keyword
        self.subcategories = []

    def add_subcategory(self, subcategory):
        self.subcategories.append(subcategory)
