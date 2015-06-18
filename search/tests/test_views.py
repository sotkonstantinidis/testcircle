from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from unittest.mock import patch

from accounts.tests.test_models import create_new_user
from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from search.views import (
    admin,
    update,
    search,
)

route_search_admin = 'search:admin'
route_search_search = 'search:search'
route_search_update = 'search:update'


class AdminTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_search_admin)

    def test_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_requires_superuser_permissions(self):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        with self.assertRaises(PermissionDenied):
            admin(request)

    def test_renders_correct_template(self):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        request.user.is_superuser = True
        res = admin(request)
        self.assertTemplateUsed(res, 'search/admin.html')
        self.assertEqual(res.status_code, 200)


class UpdateTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_search_admin)
        user = create_new_user()
        user.is_superuser = True
        self.request = self.factory.get(self.url)
        self.request.user = user

    def test_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_requires_superuser_permissions(self):
        request = self.factory.get(self.url)
        request.user = create_new_user(id=99, email='foo@bar.com')
        with self.assertRaises(PermissionDenied):
            update(request, 'foo')

    @patch('search.views.QuestionnaireConfiguration')
    def test_calls_QuestionnaireConfiguration(self, mock_Conf):
        update(self.request, 'foo')
        mock_Conf.assert_callert_once_with('foo')

    @patch('search.views.QuestionnaireConfiguration')
    def test_returns_bad_request_if_errors_in_configuration(self, mock_Conf):
        mock_Conf.configuration_error = 'error'
        res = update(self.request, 'foo')
        self.assertEqual(res.status_code, 400)

    @patch('search.views.get_mappings')
    @patch('search.views.create_or_update_index')
    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_configuration_errors')
    def test_calls_get_mappings(
            self, mock_get_conf_errors, mock_Conf, mock_create_index,
            mock_get_mappings):
        mock_Conf.return_value = None
        mock_get_conf_errors.return_value = None
        mock_create_index.return_value = None, None
        update(self.request, 'foo')
        mock_get_mappings.assert_callert_once_with('foo')

    @patch('search.views.get_mappings')
    @patch('search.views.create_or_update_index')
    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_configuration_errors')
    def test_calls_create_or_update_index(
            self, mock_get_conf_errors, mock_Conf, mock_create_index,
            mock_get_mappings):
        mock_Conf.return_value = None
        mock_get_conf_errors.return_value = None
        mock_create_index.return_value = None, None
        update(self.request, 'foo')
        mock_create_index.assert_called_once_with(
            'foo', mock_get_mappings.return_value)

    @patch('search.views.get_mappings')
    @patch('search.views.create_or_update_index')
    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_configuration_errors')
    def test_returns_bad_request_if_create_not_successful(
            self, mock_get_conf_errors, mock_Conf, mock_create_index,
            mock_get_mappings):
        mock_Conf.return_value = None
        mock_get_conf_errors.return_value = None
        mock_create_index.return_value = None, None
        res = update(self.request, 'foo')
        self.assertEqual(res.status_code, 400)

    @patch('search.views.get_mappings')
    @patch('search.views.create_or_update_index')
    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_configuration_errors')
    def test_renders_correct_template(
            self, mock_get_conf_errors, mock_Conf, mock_create_index,
            mock_get_mappings):
        mock_Conf.return_value = None
        mock_get_conf_errors.return_value = None
        mock_create_index.return_value = True, None
        res = update(self.request, 'foo')
        self.assertTemplateUsed(res, 'search/admin.html')
        self.assertEqual(res.status_code, 200)


class SearchTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_search_search)

    @patch('search.views.simple_search')
    def test_calls_simple_search(self, mock_simple_search):
        self.client.get(self.url)
        mock_simple_search.assert_called_once_with('')

    @patch('search.views.simple_search')
    def test_calls_simple_search_with_get_param(self, mock_simple_search):
        request = self.factory.get(self.url)
        request.GET = {'q': 'foo'}
        search(request)
        mock_simple_search.assert_called_once_with('foo')

    def test_renders_correct_template(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'search/admin.html')
        self.assertEqual(res.status_code, 200)
