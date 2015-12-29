from rest_framework.generics import ListAPIView
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


class QuestionnairesAPIListView(ListAPIView):
    """
    List all questionnaires; can be filtered.

    To be defined: Move this view into the questionnaire-app? This would ensure loose coupling.
    """
    serializer_class = QuestionnaireSerializer

    def get_queryset(self):
        """
        Filter valid questionnaires; Status "3" is public.
        """
        return Questionnaire.objects.filter(
            blocked=False, status=STATUSES[3][0]
        )