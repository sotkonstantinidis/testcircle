"""
All questionnaire data is on the elasticsearch-index. As of now, the database
is still touched. Efforts to refactor the following are in progress:

- Create new serializer (see stub: questionnaire.serializers)
- Use serializer when putting objects to the index
  (search.index.put_questionnaire_data)
- Put logic of 'get_list_values' to serializer.
- Put logic of new required fields for external API to serializer.
"""
import contextlib

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination

from api.views import LogUserMixin, PermissionMixin
from questionnaire.models import Questionnaire
from search.search import advanced_search
from ..utils import get_list_values


class QuestionnaireListView(PermissionMixin, LogUserMixin, GenericAPIView,
                            PageNumberPagination):
    """
    List view for questionnaires.

    Todo:
    - Refactor serializing / deserializing of indexed questionnaires
    - Add pagination
    - Add detail view
    - Improve docstrings

    """
    url_cache = {}

    def get_elasticsearch_items(self):
        """
        Don't touch the database, but fetch everything from elasticsearch.

        Args:
            page: int For pagination: start at this position
            code: string Code of the questionnaire

        Returns:
            list of questionnaires
        """
        # Blank search returns all items within all indexes.
        es_search_results = advanced_search()
        questionnaires = self.format_es_search_results(es_search_results)
        list_values = get_list_values(
            questionnaire_objects=questionnaires, with_links=False
        )
        for index, questionnaire in enumerate(list_values):
            list_values[index]['url'] = self.request.build_absolute_uri(
                self.url_cache[questionnaire['id']]
            )
        return list_values

    def get(self, request, *args, **kwargs):
        """
        Returns:
            Response: paginated objects.

        """
        items = self.get_elasticsearch_items()
        paginated = self.paginate_queryset(items)
        return self.get_paginated_response(paginated)

    def format_es_search_results(self, results):
        """
        @todo: refactor!
        This is nasty, as it hits the db for each questionnaire. This is
        required beause the method `get_list_values` expects Questionnaire
        objects.
        As the API must be made available for a beta right now, hit the db until
        the refactor is finished.
        """
        results = results.get('hits', {}).get('hits')
        for result in results:
            with contextlib.suppress(ObjectDoesNotExist):
                obj = Questionnaire.objects.get(id=result['_id'])
                self.url_cache[obj.id] = obj.get_absolute_url()
                yield obj
