from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from unittest.mock import patch, Mock

from qcat.tests import TestCase
from qcat.tests.test_views import (
    qcat_route_home,
)
from accounts.tests.test_authentication import (
    create_new_user,
)
from accounts.views import login
from django.http import HttpResponseRedirect


accounts_route_login = 'login'
accounts_route_logout = 'logout'


class LoginTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/unccd/new/cat_1')
        self.request.user = create_new_user()

    def test_renders_correct_template(self):
        res = self.client.get(reverse(accounts_route_login))
        self.assertTemplateUsed(res, 'login.html')

    def test_redirects_home_if_user_already_logged_in(self):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = True
        self.request.user.is_authenticated = mock_is_authenticated
        res = login(self.request)
        self.assertIsInstance(res, HttpResponseRedirect)
        self.assertEqual(res.url, self.request.build_absolute_uri(reverse(
            qcat_route_home)))

    def test_redirects_to_redirect_if_already_logged_in(self):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = True
        self.request.user.is_authenticated = mock_is_authenticated
        self.request.GET = {'next': 'foo'}
        res = login(self.request)
        self.assertIsInstance(res, HttpResponseRedirect)
        self.assertEqual(res.url, self.request.build_absolute_uri('foo'))

    @patch('accounts.views.django_login')
    @patch('accounts.views.authenticate')
    def test_calls_authenticate_with_ses_id(
            self, mock_authenticate, mock_django_login):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = False
        self.request.user.is_authenticated = mock_is_authenticated
        self.request.COOKIES = {'fe_typo_user': 'foo'}
        login(self.request)
        mock_authenticate.assert_called_once_with(token='foo')

    @patch('accounts.views.django_login')
    @patch('accounts.views.authenticate')
    def test_calls_django_login(
            self, mock_authenticate, mock_django_login):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = False
        mock_authenticate.return_value = self.request.user
        self.request.user.is_authenticated = mock_is_authenticated
        self.request.COOKIES = {'fe_typo_user': 'foo'}
        login(self.request)
        mock_django_login.assert_called_once_with(
            self.request, self.request.user)


class LogoutTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def test_logout_redirects_to_home(self):
        self.client.login(username='a@b.com', password='foo')
        res = self.client.get(reverse(accounts_route_logout), follow=True)
        self.assertRedirects(res, reverse(qcat_route_home))
