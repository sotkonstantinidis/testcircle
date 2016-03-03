from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework.permissions import IsAuthenticated

from qcat.tests import TestCase
from accounts.tests.test_models import create_new_user
from questionnaire.api.views import QuestionnaireListView

from api.models import RequestLog, NoteToken


class ApiViewTest(TestCase):
    """
    The largest part of the API are just configuration.
    """
    def setUp(self):
        self.user = create_new_user()
        token, created = NoteToken.objects.get_or_create(user=self.user)
        self.token = token

    def test_logging(self):
        # Set the token in the header for a request to check the logging.
        url = reverse('questionnaires-api-list')
        token = 'Token {}'.format(self.token)
        self.client.get(path=url, HTTP_AUTHORIZATION=token)
        self.assertEqual(
            RequestLog.objects.all().count(), 1
        )

    def test_permission_required(self):
        # Ensure required authentication.
        settings.DEBUG = False
        permissions = QuestionnaireListView().get_permissions()
        self.assertIsInstance(permissions[0], IsAuthenticated)
