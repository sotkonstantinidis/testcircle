from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from qcat.tests import TestCase
from questionnaire.api.views import QuestionnaireListView


class ApiViewTest(TestCase):
    """
    The largest part of the API is just configuration.
    """

    def test_permission_required(self):
        # Ensure required authentication.
        settings.DEBUG = False
        permissions = QuestionnaireListView().get_permissions()
        self.assertIsInstance(permissions[0], IsAuthenticated)
