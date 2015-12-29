from rest_framework import filters
from rest_framework import viewsets
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView

from questionnaire.models import Questionnaire, STATUSES

from .serializers import QuestionnaireSerializer


class APIRoot(APIView):
    """
    Welcome to the API provided by WOCAT.

    This API is intended to be consumed by partners.
    """
    http_method_names = ('get', )

    def get(self, request, format=None):
        urls = {
            'questionnaires': reverse('questionnaires-api-list', request=request, format=format),
        }
        return Response(urls)


class QuestionnaireViewSet(viewsets.ReadOnlyModelViewSet):
    """
    List and detail view for questionnaires.

    Filters can be passed in the url, e.g. /en/api/v1/questionnaire/?version=1

    Following fields can be filtered for:
    - version

    To be defined: Move this view into the questionnaire-app? This would ensure loose coupling.
    """
    serializer_class = QuestionnaireSerializer
    # Discuss: enable filter globally with setting?
    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('version', )

    def get_queryset(self):
        """
        Filter valid questionnaires; Status "3" is public.
        """
        return Questionnaire.objects.filter(
            blocked=False, status=STATUSES[3][0]
        )
