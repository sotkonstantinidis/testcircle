from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

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
def questionnaire_new_step(request, step, questionnaire_id=None):
    """
    View to show the form of a single step of a new WOCAT questionnaire.
    Also handles the form submit of the step along with its validation
    and redirect.

    .. seealso::
        The actual rendering of the form and the form validation is
        handled by the generic questionnaire function
        :func:`questionnaire.views.questionnaire_new_step`.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``step`` (str): The code of the questionnaire category.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_new_step(
        request, step, 'wocat', 'wocat', page_title=_('WOCAT Form'))


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
        request, 'wocat', 'wocat', questionnaire_id=questionnaire_id,
        page_title=_('WOCAT Form Overview'))


def questionnaire_details(request, questionnaire_id):
    """
    View to show the details of an existing WOCAT questionnaire.

    .. seealso::
        The actual rendering of the details is handled by the generic
        questionnaire function
        :func:`questionnaire.views.questionnaire_details`

    Args:
        ``request`` (django.http.HttpResponse): The request object.

        ``questionnaire_id`` (int): The id of the questionnaire.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_details(
        request, questionnaire_id, 'wocat', 'wocat/questionnaire/details.html')


def questionnaire_list(request):
    """
    View to show a list with WOCAT questionnaires.

    .. seealso::
        The actual rendering of the list is handled by the generic
        questionnaire function
        :func:`questionnaire.views.questionnaire_list`

    Args:
        ``request`` (django.http.HttpResponse): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_list(
        request, 'wocat', 'wocat/questionnaire/list.html',
        'wocat:questionnaire_details')
