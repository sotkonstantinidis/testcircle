from collections import OrderedDict

from django.core.paginator import EmptyPage
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param, replace_query_param

from api.views import LogUserMixin, PermissionMixin
from questionnaire.models import Questionnaire
from questionnaire.view_utils import ESPagination, get_paginator, get_page_parameter
from search.search import advanced_search, get_element

from ..utils import get_list_values
from ..conf import settings


class QuestionnaireAPIMixin(PermissionMixin, LogUserMixin, GenericAPIView):

    def get_elasticsearch_items(self):
        raise NotImplementedError()

    def update_dict_keys(self, items):
        """
        Some keys need to be updated (e.g. description has a different key depending on the config) for a more
        consistent behavior of the APIs data.
        This cannot be done when indexing (elasticsearch) the data, as the templates expect the variable names in
        the 'original' format.
        """
        setting_keys = set(settings.QUESTIONNAIRE_API_CHANGE_KEYS.keys())
        for item in items:
            matching_keys = setting_keys.intersection(item.keys())
            if matching_keys:
                for key in matching_keys:
                    item[settings.QUESTIONNAIRE_API_CHANGE_KEYS[key]] = item.pop(key)

            yield item


class QuestionnaireListView(QuestionnaireAPIMixin):
    """
    List view for questionnaires.

    @todo: Add detail view

    """
    page_size = settings.API_PAGE_SIZE

    def get(self, request, *args, **kwargs):
        items = self.get_elasticsearch_items()
        return self.get_paginated_response(items)

    def get_elasticsearch_items(self):
        """
        Don't touch the database, but fetch everything from elasticsearch.

        Args:
            page: int For pagination: start at this position
            code: string Code of the questionnaire

        Returns:
            list of questionnaires
        """
        self.current_page = get_page_parameter(self.request)
        offset = self.current_page * self.page_size - self.page_size

        es_pagination = self.get_es_paginated_results(offset)

        questionnaires, self.pagination = get_paginator(
            es_pagination, self.current_page, self.page_size
        )

        # Combine configuration and questionnaire values.
        list_values = get_list_values(es_hits=questionnaires)
        return self.update_dict_keys(list_values)

    def get_es_paginated_results(self, offset):
        """
        Args:
            offset: int

        Returns:
            ESPagination

        """
        # Blank search returns all items within all indexes.
        es_search_results = advanced_search(
            limit=self.page_size,
            offset=offset
        )
        # Build a custom paginator.
        es_hits = es_search_results.get('hits', {})
        return ESPagination(es_hits.get('hits', []), es_hits.get('total', 0))

    def get_paginated_response(self, data):
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
            ('results', data)
        ]))

    def _get_paginate_link(self, page_number):
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

    def get_next_link(self):
        return self._get_paginate_link(self.current_page + 1)

    def get_previous_link(self):
        return self._get_paginate_link(self.current_page - 1)


class QuestionnaireDetailView(QuestionnaireAPIMixin):
    """
    Return a single item from elasticsearch, if object is still valid on the model.
    """

    def get(self, request, *args, **kwargs):
        return Response(self.get_elasticsearch_items())

    def get_elasticsearch_items(self):
        """
        Get a single element from elasticsearch. As the _id used for elasticsearch is the actual objects id, and not the
        code, resolve the id first.

        Returns: dict

        """
        obj = self.get_current_object()
        item = get_element(obj.id, obj.configurations.all().first().code)
        return item

    def get_current_object(self):
        """
        Check if the model entry is still valid.

        Returns: object (Questionnaire instance)

        """
        return get_object_or_404(
            Questionnaire.with_status.public(), code=self.kwargs['identifier']
        )