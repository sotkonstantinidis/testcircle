from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from configuration.configuration import QuestionnaireConfiguration
from questionnaire.views import (
    generic_questionnaire_details,
    generic_questionnaire_link_form,
    generic_questionnaire_link_search,
    generic_questionnaire_list,
    generic_questionnaire_new_step,
    generic_questionnaire_new,
)


def home(request):
    # TODO: Show this warning here? Or in Admin?
    questionnaire_configuration = QuestionnaireConfiguration('samplemulti')
    if questionnaire_configuration.configuration_error is not None:
        messages.error(
            request, 'WARNING: INVALID CONFIGURATION. {}'.format(
                questionnaire_configuration.configuration_error))

    list_template_values = generic_questionnaire_list(
        request, 'samplemulti', template=None, only_current=True, limit=3,
        db_query=True)

    return render(request, 'samplemulti/home.html', {
        'list_values': list_template_values.get('list_values', [])
    })


@login_required
def questionnaire_link_form(request):
    """
    View to show the form for linking questionnaires. Also handles the
    form submit along with its validation and redirect.

    .. seealso::
        The actual rendering of the form and the form validation is
        handled by the generic questionnaire function
        :func:`questionnaire.views.generic_questionnaire_new_step`.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_link_form(
        request, 'samplemulti', 'samplemulti', page_title='SAMPLEMULTI Links')


def questionnaire_link_search(request):
    """
    Return the results of the search used for adding linked
    questionnaires. Returns the found Questionnaires in JSON format.

    The search happens in the database as users need to see their own
    pending changes.

    .. seealso::
        The actual rendering of the results is handled by the generic
        questionnaire function
        :func:`questionnaire.views.generic_questionnaire_link_search`

    Args:
        ``request`` (django.http.HttpResponse): The request object. The
        search term is passed as GET parameter ``q`` of the request.

    Returns:
        ``JsonResponse``. A rendered JSON Response.
    """
    return generic_questionnaire_link_search(request, 'samplemulti')


@login_required
def questionnaire_new_step(request, step, questionnaire_id=None):
    """
    View to show the form of a single step of a new SAMPLEMULTI
    questionnaire. Also handles the form submit of the step along with
    its validation and redirect.

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
        request, step, 'samplemulti', 'samplemulti',
        page_title='SAMPLEMULTI Form')


@login_required
def questionnaire_new(request, questionnaire_id=None):
    """
    View to show the overview of a new or edited SAMPLEMULTI questionnaire.
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
        request, 'samplemulti', 'samplemulti/questionnaire/details.html',
        'samplemulti', questionnaire_id=questionnaire_id)


def questionnaire_details(request, questionnaire_id):
    """
    View to show the details of an existing SAMPLEMULTI questionnaire.

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
        request, questionnaire_id, 'samplemulti',
        'samplemulti/questionnaire/details.html')


def questionnaire_list_partial(request):
    """
    View to render the questionnaire list only partially. Returns a JSON
    response with parts of the template. To be used when uploading the
    list through AJAX requests.

    Args:
        ``request`` (django.http.HttpResponse): The request object.

    Returns:
        ``JsonResponse``. A JSON response with the following entries:

        - ``success`` (bool): A boolean indicating whether query was
          performed successfully or not.

        - ``list`` (string): The rendered list template.

        - ``active_filters`` (string): The rendered active filters
          template.
    """
    list_values = generic_questionnaire_list(
        request, 'samplemulti', template=None)

    list_ = render_to_string('samplemulti/questionnaire/partial/list.html', {
        'list_values': list_values['list_values']})
    active_filters = render_to_string('active_filters.html', {
        'active_filters': list_values['active_filters']})

    ret = {
        'success': True,
        'list': list_,
        'active_filters': active_filters,
    }

    return JsonResponse(ret)


def questionnaire_list(request):
    """
    View to show a list with SAMPLEMULTI questionnaires.

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
        request, 'samplemulti', template='samplemulti/questionnaire/list.html',
        filter_url=reverse('samplemulti:questionnaire_list_partial'))