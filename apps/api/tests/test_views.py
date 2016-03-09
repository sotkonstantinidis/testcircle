import contextlib
from unittest.mock import MagicMock, patch

from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from accounts.tests.test_models import create_new_user
from api.models import RequestLog, NoteToken
from qcat.tests import TestCase
from questionnaire.api.views import QuestionnaireListView


class ApiViewTest(TestCase):
    """
    The largest part of the API are just configuration.
    """
    def setUp(self):
        self.user = create_new_user()
        token, created = NoteToken.objects.get_or_create(user=self.user)
        self.token = token

    # def test_logging(self):
    #     # Set the token in the header for a request to check the logging.
    #     url = reverse('questionnaires-api-list')
    #     token = 'Token {}'.format(self.token)
    #     with patch('search.search.advanced_search') as advanced_search:
    #         advanced_search.return_value = {}
    #         self.client.get(path=url, HTTP_AUTHORIZATION=token)
    #         self.assertEqual(
    #             RequestLog.objects.all().count(), 1
    #         )

    def test_permission_required(self):
        # Ensure required authentication.
        settings.DEBUG = False
        permissions = QuestionnaireListView().get_permissions()
        self.assertIsInstance(permissions[0], IsAuthenticated)
