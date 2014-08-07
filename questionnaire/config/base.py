from django import forms
from django.utils.translation import ugettext_lazy as _


class BaseQuestionnaireField(object):
    """
    The base class of a Questionnaire item.

    Necessary attributes of subclasses:
    - (str) fieldType: One of [text, dropdown].
    - (str) label: The display name of the item.

    Optional attributes of subclasses:
    - (bool) required: Defaults to false
    """

    fieldType = None
    label = None
    required = False

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


class SLMName(BaseQuestionnaireField):

    fieldType = 'text'
    label = _('SLM Name')


class SomeDropdown(BaseQuestionnaireField):

    fieldType = 'dropdown'
    label = _('Some Dropdown')

    choices = (
        ('1', _('Option 1')),
        ('2', _('Option 2')),
    )
