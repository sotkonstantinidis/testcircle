from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    render,
    redirect,
)
from django.http import HttpResponseBadRequest
from django.views.generic import TemplateView
from elasticsearch import TransportError

from accounts.decorators import force_login_check
from .index import (
    create_or_update_index,
    delete_all_indices,
    delete_single_index,
    get_elasticsearch,
    get_mappings,
    put_questionnaire_data,
)
from .search import simple_search
from .utils import get_alias
from configuration.cache import get_configuration
from configuration.models import Configuration
from questionnaire.models import Questionnaire
from questionnaire.utils import get_list_values

es = get_elasticsearch()


@login_required
@force_login_check
def admin(request, log=''):
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

    configurations = []
    for active_configuration in Configuration.objects.filter(active=True):
        db_count = Questionnaire.with_status.public().filter(
            configurations__code=active_configuration.code).count()
        try:
            index_count = es.count(
                index=get_alias([active_configuration.code])).get('count')
        except TransportError:
            index_count = None
        config_entry = {
            'object': active_configuration,
            'db_count': db_count,
            'index_count': index_count,
        }
        configurations.append(config_entry)

    return render(request, 'search/admin.html', {
        'configurations': configurations,
    })


@login_required
@force_login_check
def index(request, configuration):
    """
    Create or update the mapping of an index.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration`` (str): The code of the Questionnaire
        configuration.

    Returns:
        ``HttpResponse``. A rendered Http Response (redirected to the
        search admin home page).
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    questionnaire_configuration = get_configuration(configuration)
    if questionnaire_configuration.get_configuration_errors() is not None:
        return HttpResponseBadRequest(
            questionnaire_configuration.configuration_error)

    mappings = get_mappings(questionnaire_configuration)

    success, logs, error_msg = create_or_update_index(configuration, mappings)
    if success is not True:
        messages.error(request, 'The following error(s) occured: {}'.format(
            error_msg))
    else:
        messages.success(
            request, 'Index "{}" was created or updated.'.format(
                configuration))

    return redirect('search:admin')


@login_required
@force_login_check
def update(request, configuration):
    """
    Add the questionnaires of a configuration to the index.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration`` (str): The code of the Questionnaire
        configuration.

    Returns:
        ``HttpResponse``. A rendered Http Response (redirected to the
        search admin home page).
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    questionnaire_configuration = get_configuration(configuration)
    if questionnaire_configuration.get_configuration_errors() is not None:
        return HttpResponseBadRequest(
            questionnaire_configuration.configuration_error)

    processed, errors = put_questionnaire_data(
        configuration,
        Questionnaire.with_status.public().filter(
            configurations__code=configuration)
    )

    if len(errors) > 0:
        messages.error(request, 'The following error(s) occured: {}'.format(
            ', '.join(errors)))
    else:
        messages.success(
            request, '{} Questionnaires of configuration "{}" successfully '
            'indexed.'.format(processed, configuration))

    return redirect('search:admin')


@login_required
@force_login_check
def delete_all(request):
    """
    Delete all the indices.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response (redirected to the
        search admin home page).
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    success, error_msg = delete_all_indices()
    if success is not True:
        messages.error(request, 'The following error(s) occured: {}'.format(
            error_msg))
    else:
        messages.success(request, 'All indices successfully deleted.')

    return redirect('search:admin')


@login_required
@force_login_check
def delete_one(request, configuration):
    """
    Delete a single index.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration`` (str): The code of the Questionnaire
        configuration.

    Returns:
        ``HttpResponse``. A rendered Http Response (redirected to the
        search admin home page).
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    success, error_msg = delete_single_index(configuration)
    if success is not True:
        messages.error(request, 'The following error(s) occured: {}'.format(
            error_msg))
    else:
        messages.success(request, 'Index "{}" successfully deleted.'.format(
            configuration))

    return redirect('search:admin')


def search(request):
    """
    Do a full text search.

    Args:
        ``request`` (django.http.HttpRequest): The request object.
    """
    search = simple_search(request.GET.get('q', ''))
    hits = search.get('hits', {}).get('hits', [])

    list_values = get_list_values(configuration_code=None, es_hits=hits)

    return render(request, 'sample/questionnaire/list.html', {
        'list_values': list_values,
    })


class FilterMixin:

    filter_join_char = '__'

    def get_configuration_object(self):
        configuration_code = self.request.GET.get('type')
        return get_configuration(configuration_code)


class FilterKeyView(FilterMixin, TemplateView):
    """
    Get the available filter keys for a given configuration type
    """

    http_method_names = ['get']
    template_name = 'search/partial/filter_key.html'

    def dispatch(self, request, *args, **kwargs):
        configuration = self.get_configuration_object()
        filter_keys = configuration.get_filter_keys()
        filter_keys.insert(0, ('', '---'))
        context = {
            'filter_select': filter_keys,
        }
        return self.render_to_response(context=context)


class FilterValueView(FilterMixin, TemplateView):
    """
    Get the available values and operator types for a given configuration and 
    key
    """
    http_method_names = ['get']
    template_name = 'search/partial/filter_value.html'

    def dispatch(self, request, *args, **kwargs):

        configuration = self.get_configuration_object()

        key_path = request.GET.get('key_path', '')
        key_path_parts = key_path.split(self.filter_join_char)

        question = None
        if len(key_path_parts) == 2:
            question = configuration.get_question_by_keyword(
                key_path_parts[0], key_path_parts[1])

        context = {
            'choices': question.choices,
            'key_path': key_path,
        }

        return self.render_to_response(context=context)
