import logging

from django.conf import settings
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from .models import RequestLog

logger = logging.getLogger(__name__)


class APIRoot(APIView):
    """
    Welcome to the API provided by WOCAT. This is a list with all endpoints
    that are available.

    This API is intended to be consumed by partners.
    """
    http_method_names = ('get', )
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, )

    def get(self, request, format=None):
        urls = {
            'questionnaires': reverse('questionnaires-api-list',
                                      request=request, format=format),
            'auth token': reverse('obtain-api-token', request=request,
                                  format=format),
            'documentation': reverse('django.swagger.base.view',
                                     request=request, format=format),
        }
        return Response(urls)


class LogUserMixin:
    """
    Log requests that access the API to the database, so usage statistics can
    be created.

    """
    def finalize_response(self, request, response, *args, **kwargs):
        try:
            RequestLog(
                user=request.user,
                resource=request.build_absolute_uri()
            ).save()
        # Catch any exception. Logging errors must not result in application
        # errors.
        except Exception as e:
            logger.error(e)
        return super().finalize_response(request, response, *args, **kwargs)


class PermissionMixin:
    """
    Default permissions for all API views.

    """
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get_permissions(self):
        """
        Don't force permissions for development.
        """
        if settings.DEBUG:
            self.permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES
        return super().get_permissions()
