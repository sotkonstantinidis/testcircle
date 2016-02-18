from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.views import LogUserMixin, PermissionMixin
from .serializers import QuestionnaireSerializer
from ..models import Questionnaire


class QuestionnaireViewSet(LogUserMixin, PermissionMixin, ReadOnlyModelViewSet):
    """
    List and detail view for questionnaires.

    Filters can be passed in the url, e.g. /en/api/v1/questionnaire/?version=1

    No filters are available yet.

    The results are displayed in the same language as the request. The language
    of the results can alternatively be defined with the query string param
    'lang', e.g. ?lang=es

    """
    serializer_class = QuestionnaireSerializer
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('version', )

    def get_queryset(self):
        """
        Display public questionnaires only.
        """
        return Questionnaire.with_status.public()
