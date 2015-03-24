from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from configuration.configuration import QuestionnaireConfiguration
from questionnaire.views import (
    generic_questionnaire_details,
    generic_questionnaire_list,
    generic_questionnaire_new_step,
    generic_questionnaire_new,
)


def home(request):

    # TODO: Show this warning here? Or in Admin?
    questionnaire_configuration = QuestionnaireConfiguration('wocat')
    if questionnaire_configuration.configuration_error is not None:
        messages.error(
            request, 'WARNING: INVALID CONFIGURATION. {}'.format(
                questionnaire_configuration.configuration_error))

    return render(request, 'wocat/home.html')


@login_required
def questionnaire_new(request, questionnaire_id=None):
    """
    View to show the overview of a new or edited WOCAT questionnaire.
    Also handles the form submit of the entire questionnaire.

    .. seealso::
        The actual rendering of the form and the form validation is
        handled by the generic questionnaire function
        :func:`questionnaire.views.questionnaire_new`.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_new(
        request, 'wocat', 'wocat/questionnaire/new.html',
        'wocat:questionnaire_details', 'wocat:questionnaire_new_step',
        questionnaire_id=questionnaire_id)
