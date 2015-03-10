from django.contrib.auth import get_user_model
User = get_user_model()
from unittest.mock import patch

from accounts.authentication import WocatAuthenticationBackend
from qcat.tests import TestCase


def get_mock_do_auth_return_values(username='test@qcat.com'):
    """
    Returns mock values that correspond to the actual _do_auth function
    in accounts.authentication.
    """
    return (username, '1,2', 'Firstname', 'Lastname')


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
def do_log_in(client, mock_do_auth):
    mock_do_auth.return_value = get_mock_do_auth_return_values()
    client.login(token='foo')


def create_new_user():
    return User.create_new(email='a@b.com', name='foo')


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
class AuthenticateTest(TestCase):

    def setUp(self):
        self.backend = WocatAuthenticationBackend()

    def test_passes_credentials_to_auth_function(self, mock_do_auth):
        self.backend.authenticate(token='foo')
        mock_do_auth.assert_called_once_with('foo')

    def test_returns_none_if_auth_function_returns_none(self, mock_do_auth):
        mock_do_auth.return_value = None
        user = self.backend.authenticate(token='foo')
        self.assertIsNone(user)

    def test_finds_existing_user_with_username(self, mock_do_auth):
        actual_user = User.objects.create(email='test@qcat.com')
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        found_user = self.backend.authenticate(token='foo')
        self.assertEqual(found_user, actual_user)

    def test_creates_new_user_if_necessary(self, mock_do_auth):
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        found_user = self.backend.authenticate(token='foo')
        new_user = User.objects.get(email='test@qcat.com')
        self.assertEqual(found_user, new_user)

    @patch('accounts.models.User.update')
    def test_calls_user_update_function(self, mock_User_update, mock_do_auth):
        mock_do_auth.return_value = get_mock_do_auth_return_values()
        self.backend.authenticate(token='foo')
        mock_User_update.assert_called_once_with(
            name='Firstname Lastname', privileges=['1', '2'])


class DoAuthTest(TestCase):

    def setUp(self):
        self.do_auth = WocatAuthenticationBackend()._do_auth

    def test_returns_none_if_no_token(self):
        ret = self.do_auth(token=None)
        self.assertIsNone(ret)

    def test_returns_none_if_no_user_found(self):
        ret = self.do_auth(token='foo')
        self.assertIsNone(ret)
