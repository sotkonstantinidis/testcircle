from django import forms


class FormPart1(forms.Form):
    subject = forms.CharField(max_length=100)
    sender = forms.EmailField()


class FormPart2(forms.Form):
    message = forms.CharField(widget=forms.Textarea)


QUESTIONNAIRES_LIST = [
    FormPart1,
    FormPart2
]
