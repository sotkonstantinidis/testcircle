from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.urlresolvers import reverse
from django.test import TestCase
from unittest.mock import patch

loginRouteName = 'login'
logoutRouteName = 'logout'
homeRouteName = 'home'
aboutRouteName = 'about'


class LoginTest(TestCase):

    fixtures = ['sample.json']

    def test_login_renders_correct_template(self):
        res = self.client.get(reverse(loginRouteName))
        self.assertTemplateUsed(res, 'login.html')

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_login_redirects_to_home(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        res = self.client.post(reverse(loginRouteName), {
            'email': 'a@b.com',
            'password': 'foo'
        }, follow=True)
        self.assertRedirects(res, reverse(homeRouteName))

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_login_redirects_to_next_page(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        res = self.client.post('%s?next=/about' % reverse(loginRouteName), {
            'email': 'a@b.com',
            'password': 'foo'
        }, follow=True)
        self.assertRedirects(res, reverse(aboutRouteName))

    def test_login_with_false_credentials_fails_with_error_message(self):
        res = self.client.post(reverse(loginRouteName), {
            'email': 'wrong@email.com',
            'password': 'foo'
        })
        self.assertTemplateUsed(res, 'login.html')
        self.assertContains(res, 'The username and/or password you entered '
                            'were not correct.')


class LogoutTest(TestCase):

    fixtures = ['sample.json']

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def test_logout_redirects_to_home(self, mock_do_auth):
        mock_do_auth.return_value = ('tempsessionid')
        self.client.login(username='a@b.com', password='foo')
        res = self.client.get(reverse(logoutRouteName), follow=True)
        self.assertRedirects(res, reverse(homeRouteName))
