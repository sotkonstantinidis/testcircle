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
from questionnaire.views import ESQuestionnaireQueryMixin

from .index import (
    create_or_update_index,
    delete_all_indices,
    delete_single_index,
    get_elasticsearch,
    get_mappings,
    put_questionnaire_data,
)
from .search import simple_search, get_aggregated_values
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
    for configuration in Configuration.objects.all().distinct('code'):
        db_count = Questionnaire.with_status.public().filter(
            configuration__code=configuration.code
        ).count()
        try:
            index_count = es.count(
                index=get_alias([configuration.code])).get('count')
        except TransportError:
            index_count = None
        config_entry = {
            'object': configuration,
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

    # TODO: This should probably not always be the latest configuraion?
    # Instead, maybe an index for each edition of a configuration?
    edition = Configuration.latest_by_code(configuration).edition
    questionnaire_configuration = get_configuration(
        code=configuration, edition=edition)
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

    # TODO: This should probably not always be the latest configuraion?
    # Instead, maybe an index for each edition of a configuration?

    processed, errors = put_questionnaire_data(
        Questionnaire.with_status.public().filter(
            configuration__code=configuration
        )
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


class FilterValueView(TemplateView, ESQuestionnaireQueryMixin):
    """
    Get the available values and operator types for a given configuration and 
    key
    """
    http_method_names = ['get']
    template_name = 'search/partial/filter_value.html'

    configuration = None
    configuration_code = None

    def dispatch(self, request, *args, **kwargs):
        self.configuration_code = self.request.GET.get('type')
        self.set_attributes()

        key_path = request.GET.get('key_path', '')
        key_path_parts = key_path.split('__')

        if len(key_path_parts) != 2:
            return self.render_to_response(context={})

        questiongroup, key = key_path_parts

        # Query ES to see how many results are available for each option
        aggregated_values = get_aggregated_values(
            questiongroup, key, **self.get_filter_params())

        question = None
        if len(key_path_parts) == 2:
            question = self.configuration.get_question_by_keyword(
                key_path_parts[0], key_path_parts[1])

        counted_choices = []
        for c in question.choices:
            counted_choices.append((c[0], c[1], aggregated_values.get(c[0], 0)))

        context = {
            'choices': counted_choices,
            'key_path': key_path,
        }

        return self.render_to_response(context=context)
