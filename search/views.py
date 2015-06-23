from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.http import HttpResponseBadRequest

from configuration.configuration import QuestionnaireConfiguration
from .index import (
    get_elasticsearch,
    get_mappings,
    create_or_update_index,
)
from .search import simple_search
from questionnaire.utils import get_list_values

es = get_elasticsearch()


@login_required
def admin(request):
    """
    The search admin overview. Allow superusers to update the indices
    and execute other administrative tasks.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    return render(request, 'search/admin.html')


@login_required
def update(request, configuration):
    """
    Create or update the mapping of an index.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration`` (str): The code of the Questionnaire
        configuration.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    questionnaire_configuration = QuestionnaireConfiguration(configuration)
    if questionnaire_configuration.get_configuration_errors() is not None:
        return HttpResponseBadRequest(
            questionnaire_configuration.configuration_error)

    mappings = get_mappings(questionnaire_configuration)

    success, logs, error_msg = create_or_update_index(configuration, mappings)
    if success is not True:
        return HttpResponseBadRequest(error_msg)

    return render(request, 'search/admin.html')


def search(request):
    """
    Do a full text search.
    """
    search = simple_search(request.GET.get('q', ''))

    list_values = get_list_values(
        configuration_code=None, es_search=search)

    return render(request, 'sample/questionnaire/list.html', {
        'list_values': list_values,
    })
