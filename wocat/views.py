from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from questionnaire.views import (
    generic_questionnaire_details,
    generic_questionnaire_list,
)


def home(request):
    list_template_values = generic_questionnaire_list(
        request, 'wocat', template=None, only_current=False, limit=3,
        db_query=True)

    return render(request, 'wocat/home.html', {
        'list_values': list_template_values.get('list_values', [])
    })


def questionnaire_details(request, identifier):
    """
    View to show the details of an existing WOCAT questionnaire.

    .. seealso::
        The actual rendering of the details is handled by the generic
        questionnaire function
        :func:`questionnaire.views.questionnaire_details`

    Args:
        ``request`` (django.http.HttpResponse): The request object.

        ``identifier`` (str): The identifier of the Questionnaire
        object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_details(
        request, identifier, 'wocat', 'wocat',
        'wocat/questionnaire/details.html')


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
    list_values = generic_questionnaire_list(request, 'wocat', template=None)

    list_ = render_to_string('wocat/questionnaire/partial/list.html', {
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
        request, 'wocat', template='wocat/questionnaire/list.html',
        filter_url=reverse('wocat:questionnaire_list_partial'))
