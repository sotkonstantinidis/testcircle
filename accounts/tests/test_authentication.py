from django.contrib.auth import get_user_model
User = get_user_model()
from unittest.mock import patch

from accounts.authentication import WocatAuthenticationBackend
from qcat.tests import TestCase


def get_mock_do_auth_return_values():
    """
    Returns mock values that correspond to the actual _do_auth function
    in accounts.authentication.
    """
    return ('tempsessionid', '1,2', 1, 'username', 'Full Name')


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
def do_log_in(client, mock_do_auth):
    mock_do_auth.return_value = get_mock_do_auth_return_values()
    client.login(username='a@b.com', password='foo')


def create_new_user():
    return User.create_new(email='a@b.com', name='foo')


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
class AuthenticateTest(TestCase):

    def setUp(self):
        self.backend = WocatAuthenticationBackend()

    def test_passes_credentials_to_auth_function(self, mock_do_auth):
        self.backend.authenticate(username='test@qcat.com', password='foo')
        mock_do_auth.assert_called_once_with('test@qcat.com', 'foo')

    def test_returns_none_if_auth_function_returns_none(self, mock_do_auth):
        mock_do_auth.return_value = None
        user = self.backend.authenticate(
            username='test@qcat.com', password='foo')
        self.assertIsNone(user)

    def test_finds_existing_user_with_username(self, mock_do_auth):
        actual_user = User.objects.create(email='test@qcat.com')
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        found_user = self.backend.authenticate(
            username='test@qcat.com', password='test_password')
        self.assertEqual(found_user, actual_user)

    def test_creates_new_user_if_necessary(self, mock_do_auth):
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        found_user = self.backend.authenticate(
            username='test@qcat.com', password='test_password')
        new_user = User.objects.get(email='test@qcat.com')
        self.assertEqual(found_user, new_user)

    @patch('accounts.models.User.update')
    def test_calls_user_update_function(self, mock_User_update, mock_do_auth):
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        self.backend.authenticate(
            username='test@qcat.com', password='test_password')
        mock_User_update.assert_called_once_with(
            name='Full Name', privileges=['1', '2'])


class DoAuthTest(TestCase):

    def setUp(self):
        self.do_auth = WocatAuthenticationBackend()._do_auth

    def test_returns_none_if_no_username(self):
        ret = self.do_auth(username=None, password='foo')
        self.assertIsNone(ret)

    def test_returns_none_if_no_password(self):
        ret = self.do_auth(username='user', password=None)
        self.assertIsNone(ret)

    def test_returns_none_if_no_user_found(self):
        ret = self.do_auth(username='non@existing.com', password='foo')
        self.assertIsNone(ret)

    def test_returns_correct_user(self):
        """
        Please note that this test assumes that a user with the email
        address below is logged in at wocat.net
        """
        email = 'lukas.vonlanthen@cde.unibe.ch'
        ret = self.do_auth(
            username=email, password='foo')
        self.assertEqual(len(ret), 5)
        self.assertEqual(ret[3], email)
