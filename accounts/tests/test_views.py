from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.urlresolvers import reverse
from unittest.mock import patch

from qcat.tests import TestCase
from qcat.tests.test_views import (
    qcat_route_home,
    qcat_route_about,
)


accounts_route_login = 'login'
accounts_route_logout = 'logout'


class LoginTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def test_login_renders_correct_template(self):
        res = self.client.get(reverse(accounts_route_login))
        self.assertTemplateUsed(res, 'login.html')

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_login_redirects_to_home(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        res = self.client.post(reverse(accounts_route_login), {
            'email': 'a@b.com',
            'password': 'foo'
        }, follow=True)
        self.assertRedirects(res, reverse(qcat_route_home))

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_login_redirects_to_next_page(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        res = self.client.post('%s?next=/about' % reverse(accounts_route_login), {
            'email': 'a@b.com',
            'password': 'foo'
        }, follow=True)
        self.assertRedirects(res, reverse(qcat_route_about))

    def test_login_with_false_credentials_fails_with_error_message(self):
        res = self.client.post(reverse(accounts_route_login), {
            'email': 'wrong@email.com',
            'password': 'foo'
        })
        self.assertTemplateUsed(res, 'login.html')
        self.assertContains(res, 'The username and/or password you entered '
                            'were not correct.')


class LogoutTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_logout_redirects_to_home(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        self.client.login(username='a@b.com', password='foo')
        res = self.client.get(reverse(accounts_route_logout), follow=True)
        self.assertRedirects(res, reverse(qcat_route_home))
