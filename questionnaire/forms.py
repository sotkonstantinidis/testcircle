from django import forms
from django.forms.formsets import formset_factory

from questionnaire.config.base import SLMName, SomeDropdown


class FormPart1(forms.Form):
    slmname = SLMName().getFormField()
    somedropdown = SomeDropdown().getFormField()


class FormPart2(forms.Form):
    answerA = forms.CharField(max_length=100)
    remarkA = forms.CharField(widget=forms.Textarea)


QUESTIONNAIRES_LIST = (
    ('1', formset_factory(FormPart1, max_num=2, validate_max=True)),
    ('2', FormPart2),
)
