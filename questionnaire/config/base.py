from django import forms
from django.utils.translation import ugettext_lazy as _
from django.forms.formsets import formset_factory


class BaseQuestionnaireField(object):
    """
    The base class of a Questionnaire item.

    Necessary attributes of subclasses:
    - (str) fieldType: One of [text, dropdown].
    - (str) label: The display name of the item.
    - (str) name: The internal name of the item. Must be unique!

    Optional attributes of subclasses:
    - (bool) required: Defaults to false
    """

    fieldType = None
    label = None
    name = None
    required = False

    def getName(self):
        if not self.name:
            raise AttributeError(
                'No name is set for object {}'.format(self.__class__))
        return self.name

    def getFormField(self):
        """
        Returns a form field
        """
        if self.fieldType == 'text':
            """
            CharField
            (int) maxLength - default: 100
            """
            try:
                maxLength = self.maxLength
            except AttributeError:
                maxLength = 100
            return forms.CharField(
                max_length=maxLength,
                label=self.label, required=self.required)
        elif self.fieldType == 'dropdown':
            """
            ChoiceField
            (tuple) choices
            """
            choices = self.choices
            if self.choices[0][0]:
                empty = (None, '-- {} --'.format(_('Select')))
                choices = (empty,) + self.choices
            return forms.ChoiceField(
                choices=choices,
                label=self.label, required=self.required)
        else:
            raise ValueError(
                'Invalid fieldType: Object {} has an invalid fieldType "{}"'
                .format(self.__class__, self.fieldType))


class BaseQuestionSet(object):
    """
    The base class of a Questionset item.

    Necessary attributes of subclasses:
    - (str) name: The internal name of the Questionset. Must be unique!
    - (str) step: The step name of the Questionset. Must be unique!
    - (arr) fields: An array of BaseQuestionnaireField objects.

    Optional attributes of subclasses:
    - (dict) setOptions: options when creating a repeating set of questions.
             These options are passed to the formset_factory function.
    """

    name = None
    step = None
    fields = []
    setOptions = {}

    def getForm(self):
        formfields = {}
        for f in self.fields:
            formfields[f.getName()] = f.getFormField()
        Form = type('Form', (forms.Form,), formfields)
        if self.setOptions:
            return formset_factory(Form, **self.setOptions)
        return Form


class SLMName(BaseQuestionnaireField):

    fieldType = 'text'
    label = _('SLM Name')
    name = 'slmname'


class SomeDropdown(BaseQuestionnaireField):

    fieldType = 'dropdown'
    label = _('Some Dropdown')
    name = 'somedropdown'

    choices = (
        ('1', _('Option 1')),
        ('2', _('Option 2')),
    )


class AnswerA(BaseQuestionnaireField):

    fieldType = 'text'
    label = _('Answer A')
    name = 'answera'


class RemarkA(BaseQuestionnaireField):

    fieldType = 'text'
    label = _('Remark A')
    name = 'remarka'


class Part1(BaseQuestionSet):

    name = 'questionset1'
    step = '1'
    fields = [
        SLMName(),
        SomeDropdown()
    ]
    setOptions = {'max_num': 2}


class Part2(BaseQuestionSet):

    name = 'questionset2'
    step = '2'
    fields = [
        AnswerA(),
        RemarkA()
    ]


class BaseConfig(object):

    _list = [
        Part1(),
        Part2()
    ]

    def __init__(self, *args, **kwargs):
        print ("***")
        super(BaseConfig, self).__init__(*args, **kwargs)

    def getConfigs(self):
        return self._list

    def getFormList(self):
        forms = []
        for l in self.getConfigs():
            forms.append((l.step, l.getForm()))
        return tuple(forms)

    def getConfigByStep(self, step):
        for l in self.getConfigs():
            if l.step == step:
                return l.name
        raise ValueError(
            'Invalid form step: Step {} is not valid according to the '
            'configuration!'
            .format(self.__class__, self.fieldType))
