from django.http import Http404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.views import PermissionMixin, LogUserMixin
from configuration.structure import ConfigurationStructure


class ConfigurationStructureView(PermissionMixin, LogUserMixin, GenericAPIView):
    """
    Get the structure of the configuration of a questionnaire.

    Return information about the categories, questiongroups and questions that
    build a questionnaire.

    ``code``: The code of the configuration (e.g. "technologies").

    ``edition``: The edition of the configuration (e.g. "2018").

    Optional request params:

    ``flat``: If present, the structure will be a flat list of questions.
    """

    def get(self, request, *args, **kwargs) -> Response:

        flat = request.GET.get('flat', False)

        structure_obj = ConfigurationStructure(
            code=kwargs['code'],
            edition=kwargs['edition'],
            flat=flat,
        )

        if structure_obj.error:
            # No configuration was found for this code and edition.
            raise Http404()

        return Response(structure_obj.structure)
