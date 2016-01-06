from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.views import APIView


class APIRoot(APIView):
    """
    Welcome to the API provided by WOCAT. This is a list with all endpoints
    that are available.

    This API is intended to be consumed by partners.
    """
    http_method_names = ('get', )

    def get(self, request, format=None):
        urls = {
            'questionnaires': reverse('questionnaires-api-list',
                                      request=request, format=format),
        }
        return Response(urls)
