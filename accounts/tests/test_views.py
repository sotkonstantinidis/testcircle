from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from unittest.mock import patch, Mock

from qcat.tests import TestCase
from qcat.tests.test_views import (
    qcat_route_home,
)
from accounts.tests.test_models import (
    create_new_user,
)
from accounts.views import (
    login,
    welcome,
)
from django.http import HttpResponseRedirect


accounts_route_login = 'login'
accounts_route_logout = 'logout'
accounts_route_welcome = 'welcome'


class WelcomeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/unccd/new/cat_1')
        self.request.user = create_new_user()

    def test_redirects_home_if_user_not_authenticated(self):
        res = welcome(self.request)
        self.assertEqual(res.url, reverse(qcat_route_home))

    def test_redirects_home_if_no_session_id(self):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = True
        self.request.user.is_authenticated = mock_is_authenticated
        res = welcome(self.request)
        self.assertEqual(res.url, reverse(qcat_route_home))


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
        self.assertEqual(res.url, reverse(qcat_route_home))

    def test_redirects_to_redirect_if_already_logged_in(self):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = True
        self.request.user.is_authenticated = mock_is_authenticated
        self.request.GET = {'next': 'foo'}
        res = login(self.request)
        self.assertIsInstance(res, HttpResponseRedirect)
        self.assertEqual(res.url, 'foo')

    @patch('accounts.views.get_login_url')
    @patch('accounts.views.render')
    def test_redirect_url_is_welcome_url(
            self, mock_render, mock_get_login_url):
        mock_is_authenticated = Mock()
        mock_is_authenticated.return_value = False
        self.request.user.is_authenticated = mock_is_authenticated
        login(self.request)
        mock_render.assert_called_once_with(self.request, 'login.html', {
            'redirect_url': 'http://testserver/en/accounts/welcome?next=/',
            'login_url': mock_get_login_url.return_value,
            'show_notice': False,
        })
