import json
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
    details,
    login,
    welcome,
    user_search,
    user_update,
)
from django.http import HttpResponseRedirect


accounts_route_login = 'login'
accounts_route_logout = 'logout'
accounts_route_welcome = 'welcome'
accounts_route_user = 'user_details'


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


class UserSearchTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/accounts/search')

    @patch('accounts.views.search_users')
    def test_calls_search_users(self, mock_search_users):
        mock_search_users.return_value = {}
        user_search(self.request)
        mock_search_users.assert_called_once_with(name='')

    @patch('accounts.views.search_users')
    def test_calls_search_users_with_GET_name(self, mock_search_users):
        mock_search_users.return_value = {}
        self.request.GET = {'name': 'foo'}
        user_search(self.request)
        mock_search_users.assert_called_once_with(name='foo')

    @patch('accounts.views.search_users')
    def test_returns_success_false_if_search_users_returns_empty(
            self, mock_search_users):
        mock_search_users.return_value = {}
        ret = user_search(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertFalse(json_ret['success'])
        self.assertIn('message', json_ret)

    @patch('accounts.views.search_users')
    def test_returns_search_result(self, mock_search_users):
        mock_search_users.return_value = {"foo": "bar"}
        ret = user_search(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertEqual(json_ret, mock_search_users.return_value)


class UserUpdateTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/accounts/update')
        self.request.method = 'POST'
        self.request.POST = {'uid': 2}
        self.request.user = create_new_user()

    def test_returns_error_if_no_uid(self):
        self.request.POST = {}
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertFalse(json_ret['success'])
        self.assertIn('message', json_ret)

    @patch('accounts.views.get_user_information')
    def test_calls_get_user_information(self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        user_update(self.request)
        mock_get_user_information.assert_called_once_with(2)

    @patch('accounts.views.get_user_information')
    def test_returns_error_if_no_user_info_found(
            self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertFalse(json_ret['success'])
        self.assertIn('message', json_ret)

    @patch('accounts.views.get_user_information')
    def test_creates_user(self, mock_get_user_information):
        self.assertEqual(User.objects.count(), 1)
        mock_get_user_information.return_value = {'username': 'foo@bar.com'}
        user_update(self.request)
        users = User.objects.all()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[1].email, 'foo@bar.com')

    @patch('accounts.views.get_user_information')
    def test_updates_user(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'username': 'foo@bar.com',
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        self.request.POST = {'uid': 1}
        user_update(self.request)
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'foo@bar.com')
        self.assertEqual(users[0].firstname, 'Faz')
        self.assertEqual(users[0].lastname, 'Taz')

    @patch('accounts.views.get_user_information')
    def test_returns_user_name(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'username': 'foo@bar.com',
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        user = User.objects.get(pk=2)
        self.assertTrue(json_ret['success'])
        self.assertEqual(json_ret['name'], user.get_display_name())


class UserDetailsTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/accounts/user/1')
        self.user = create_new_user()

    @patch('accounts.views.get_object_or_404')
    def test_calls_get_object_or_404(self, mock_get_object_or_404):
        details(self.request, 0)
        mock_get_object_or_404.assert_called_once_with(User, pk=0)

    @patch('accounts.views.get_user_information')
    def test_calls_get_user_information(self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        details(self.request, self.user.id)
        mock_get_user_information.assert_called_once_with(self.user.id)

    @patch('accounts.views.get_user_information')
    def test_updates_user(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        details(self.request, self.user.id)
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'a@b.com')
        self.assertEqual(users[0].firstname, 'Faz')
        self.assertEqual(users[0].lastname, 'Taz')

    @patch('accounts.views.render')
    @patch('accounts.views.get_user_information')
    def test_calls_render(self, mock_get_user_information, mock_render):
        mock_get_user_information.return_value = {}
        details(self.request, self.user.id)
        mock_render.assert_called_once_with(self.request, 'details.html', {
            'detail_user': self.user,
        })
