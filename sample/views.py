from django.contrib import messages
from django.shortcuts import render

from configuration.configuration import QuestionnaireConfiguration


def home(request):
    # TODO: Show this warning here? Or in Admin?
    questionnaire_configuration = QuestionnaireConfiguration('sample')
    if questionnaire_configuration.configuration_error is not None:
        messages.error(
            request, 'WARNING: INVALID CONFIGURATION. {}'.format(
                questionnaire_configuration.configuration_error))

    return render(request, 'sample/home.html')
