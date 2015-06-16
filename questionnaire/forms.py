import floppyforms as forms
from django.utils.translation import ugettext as _


class QuestionnaireLinkForm(forms.Form):
    """
    This is the form used for editing links to other Questionnaires.

    .. important::
        The fields of the form are populated by data retrieved from the
        function :func:`questionnaire.utils.get_link_data`, so make sure
        to reflect any changes made to the form in this function.
    """
    id = forms.IntegerField(required=False)
    form_display = forms.CharField(
        required=False, label=_('Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}))
