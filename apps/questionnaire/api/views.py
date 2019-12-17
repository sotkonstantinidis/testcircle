from collections import OrderedDict
import logging

from django.core.paginator import EmptyPage
from django.http import Http404
from django.utils.translation import get_language
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.utils.urls import remove_query_param, replace_query_param

from api.views import LogUserMixin, PermissionMixin
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from questionnaire.views import ESQuestionnaireQueryMixin
from search.search import get_element
from ..conf import settings
from ..models import Questionnaire
from ..utils import get_list_values, get_questionnaire_data_in_single_language

logger = logging.getLogger(__name__)


class QuestionnaireAPIMixin(PermissionMixin, LogUserMixin, GenericAPIView):
    """
    Shared functionality for list and detail view.
    """
    add_detail_url = False

    def update_dict_keys(self, es_hits: list):
        """
        Some keys need to be updated (e.g. description has a different key
        depending on the config) for a more consistent behavior of the APIs
        data.
        This cannot be done when indexing (elasticsearch) the data, as the
        templates expect the variable names in the 'original' format.
        After discussion with the people consuming the api, the language of
        the content is used as key, i.e.: 'unccd_description': 'a title' becomes
        'definition: {'en': 'a title'}
        """
        for es_hit in es_hits:
            yield self.replace_keys(es_hit)

    def language_text_mapping(self, **item) -> list:
        """
        The consumers of the API require the text values in the format:
        {
            'language': 'en',
            'text': 'my text'
        }
        """
        return [{'language': key, 'text': value} for key, value in item.items()]

    def replace_keys(self, es_hit: dict) -> dict:
        """
        Replace all keys as defined by the configuration. Also, list all
        translated versions. This was requested by the consumers of the API.
        To access description and name in all versions, the config must be
        loaded again.
        """
        try:
            list_values = get_list_values(es_hits=[es_hit])[0]
        except IndexError:
            # We want to know about these errors.
            raise Exception('Possibly invalid data in ES (unable to serialize)'
                            ': %s' % es_hit)

        # 'name' and 'definition' must include all translations.
        list_values['name'] = es_hit['_source']['list_data']['name']
        list_values['definition'] = es_hit['_source']['list_data']['definition']

        # Restore state of configuration for v1.
        list_values['configurations'] = [list_values['configuration']]
        list_values['native_configuration'] = True

        # Remove keys that are not available on v1.
        delete_keys = ['serializer_config', 'serializer_edition', 'has_new_configuration_edition']
        for key in delete_keys:
            del list_values[key]

        # Add 'full' data, even for the list view.
        list_values['data'] = self.get_object_data(code=list_values['code'])

        if self.add_detail_url:
            list_values['api_url'] = reverse(
                '{api_version}:questionnaires-api-detail'.format(
                    api_version=self.request.version
                ),
                kwargs={'identifier': list_values['code']}
            )

        return list_values

    def get_object_data(self, code: str) -> dict:
        obj = self.object if hasattr(self, 'object') else self.get_current_object(code=code)
        return obj.data

    def filter_dict(self, items: dict):
        """
        Starting with API v2 only name and url to the detail page are displayed.
        """
        for item in items:
            yield {
                'name': item.get('name'),
                'created': item.get('created'),
                'updated': item.get('updated'),
                'compiler': item.get('compilers')[0]['name'],
                'reviewer': [reviewers['name'] for reviewers in item.get('reviewers')],
                'code': item.get('code'),
                'edition': item.get('serializer_edition'),
                'url': reverse(
                    viewname='{configuration}:questionnaire_details'.format(
                        configuration=item['configuration']
                    ),
                    kwargs={'identifier': item['code']}),
                'translations': item.get('translations'),
                'details': reverse(
                    '{api_version}:questionnaires-api-detail'.format(
                        api_version=self.request.version
                    ), kwargs={'identifier': item['code']}
                ),
            }

    def get_current_object(self, code='') -> Questionnaire:
        """
        Check if the model entry is still valid.

        Returns: object (Questionnaire instance)
        """
        return get_object_or_404(
            Questionnaire.with_status.public(), code=self.kwargs.get('identifier', code)
        )


class QuestionnaireListView(QuestionnaireAPIMixin, ESQuestionnaireQueryMixin):
    """
    Get a list of Questionnaires, for v1 and v2

    Return a list of Questionnaires. The same filter parameters as for the list
    view (search/filter in QCAT) can be passed.

    ``page``: Optional page offset.
    """
    page_size = settings.API_PAGE_SIZE
    add_detail_url = True
    configuration_code = 'wocat'

    def get(self, request, *args, **kwargs) -> Response:
        self.set_attributes()
        items = self.get_elasticsearch_items()
        return self.get_paginated_response(items)

    def get_elasticsearch_items(self):
        """
        Don't touch the database, but fetch everything from elasticsearch.

        Returns:
            list of questionnaires
        """
        es_results = self.get_es_results(call_from='api')

        es_pagination = self.get_es_paginated_results(es_results)
        questionnaires, self.pagination = self.get_es_pagination(es_pagination)

        # Combine configuration and questionnaire values.
        if self.request.version == 'v1':
            return self.update_dict_keys(es_hits=questionnaires)
        else:
            return self.filter_dict(
                get_list_values(es_hits=questionnaires)
            )

    def get_paginated_response(self, data) -> Response:
        """
        Build a response as if it were from the django rest framework. This
        will be replaced after the refactor.

        Args:
            data: dict The data which is returned

        Returns:
            Response

        """
        return Response(OrderedDict([
            ('count', self.pagination.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', list(data))
        ]))

    def _get_paginate_link(self, page_number) -> str:
        """
        Args:
            page_number: int

        Returns:
            string: URL of the requested page

        """
        try:
            self.pagination.validate_number(page_number)
        except EmptyPage:
            return ''

        url = self.request.build_absolute_uri()
        if page_number == 1:
            return remove_query_param(url, 'page')
        return replace_query_param(url, 'page', page_number)

    def get_next_link(self) -> str:
        return self._get_paginate_link(self.current_page + 1)

    def get_previous_link(self)  -> str:
        return self._get_paginate_link(self.current_page - 1)


class QuestionnaireDetailView(QuestionnaireAPIMixin):
    """
    Return a single item from elasticsearch, if object is still valid on the
    model.

    Used for API v1 only
    """
    add_detail_url = False

    def get(self, request, *args, **kwargs):
        """
        Set the current object to 'self', so the query is not executed again
        in the method 'replace_keys'.
        """
        self.object = self.get_current_object()
        # Get the single element from ES.
        es_hit = get_element(questionnaire=self.object)
        if not es_hit:
            raise Http404

        return Response(self.replace_keys(es_hit={'_source': es_hit}))


class ConfiguredQuestionnaireDetailView(QuestionnaireDetailView):
    """
    Get a single Questionnaire for API v2.

    Return a single Questionnaire by its code. The returned data contains the
    full configuration (including labels of sections, questiongroups etc.).

    ``identifier``: The identifier / code of the questionnaire.
    """

    def prepare_data(self) -> dict:
        """
        Merge configuration keyword, label and questionnaire data to a dict.
        """
        data = get_questionnaire_data_in_single_language(
            questionnaire_data=self.object.data,
            locale=get_language(),
            original_locale=self.object.original_locale
        )
        # Links are removed from the 'data' dict, but available on the
        # serialized element.
        data['links'] = self.prepare_link_data(
            *self.object.links_property
        )
        return data

    @staticmethod
    def prepare_link_data(*links):
        """
        Get data in current language; see: Questionnaire.links_property
        """
        translate_fields = ['name', 'url']
        for link in links:
            for field in translate_fields:
                link[field] = link[field].get(get_language(), link[field]['default'])
        return links

    def get_configured_questionnaire(self, **data):
        return ConfiguredQuestionnaire(
            config=self.object.configuration_object,
            questionnaire=self.object,
            **data
        ).store

    def get(self, request, *args, **kwargs):
        self.object = self.get_current_object()
        prepared_data = self.prepare_data()
        return Response(self.get_configured_questionnaire(**prepared_data))
