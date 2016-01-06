from django.contrib.auth import get_user_model
User = get_user_model()
from unittest.mock import patch

from accounts.authentication import (
    get_user_information,
    search_users,
    validate_session,
    WocatAuthenticationBackend,
)
from accounts.tests.test_models import create_new_user
from qcat.tests import TestCase


def get_mock_validate_session_values():
    """
    Returns mock values that correspond to the actual validate_session
    function in accounts.authentication.
    """
    return 1


def get_mock_user_information_values():
    """
    Returns mock values that correspond to the actual
    get_user_information function in accounts.authentication.
    """
    return {
        'uid': 1,
        'username': 'foo@bar.com',
        'first_name': 'Foo',
        'last_name': 'Bar',
    }


@patch('accounts.authentication.validate_session')
class AuthenticateTest(TestCase):

    def setUp(self):
        self.backend = WocatAuthenticationBackend()

    def test_passes_credentials_to_validate_function(
            self, mock_validate_session):
        self.backend.authenticate(token='foo')
        mock_validate_session.assert_called_once_with('foo')

    def test_returns_none_if_validate_function_returns_none(
            self, mock_validate_session):
        mock_validate_session.return_value = None
        user = self.backend.authenticate(token='foo')
        self.assertIsNone(user)

    def test_returns_current_user_if_session_belongs_to_him(
            self, mock_validate_session):
        mock_validate_session.return_value = 1
        current_user = create_new_user()
        user = self.backend.authenticate(
            token='foo', current_user=current_user)
        self.assertEqual(user, current_user)

    def test_finds_existing_user_with_id(self, mock_validate_session):
        actual_user = User.objects.create(id=1, email='test@qcat.com')
        mock_validate_session.return_value = get_mock_validate_session_values()
        found_user = self.backend.authenticate(token='foo')
        self.assertEqual(found_user, actual_user)

    @patch('accounts.authentication.get_user_information')
    def test_creates_new_user_if_necessary(
            self, mock_get_user_information, mock_validate_session):
        mock_get_user_information.return_value = \
            get_mock_user_information_values()
        mock_validate_session.return_value = get_mock_validate_session_values()
        found_user = self.backend.authenticate(token='foo')
        new_user = User.objects.get(pk=1)
        self.assertEqual(found_user, new_user)

    @patch('accounts.authentication.get_user_information')
    def test_creates_new_user_calls_get_user_information(
            self, mock_get_user_information, mock_validate_session):
        mock_validate_session.return_value = get_mock_validate_session_values()
        self.backend.authenticate(token='foo')
        mock_get_user_information.assert_called_once_with(
            mock_validate_session.return_value)


@patch('accounts.authentication.api_login')
class ValidateSessionTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        validate_session('foo')
        mock_api_login.assert_called_once_with()

    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_id = validate_session('foo')
        self.assertIsNone(user_id)


@patch('accounts.authentication.api_login')
class GetUserInformationTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        get_user_information(1)
        mock_api_login.assert_called_once_with()

    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_info = get_user_information(1)
        self.assertIsNone(user_info)


@patch('accounts.authentication.api_login')
class SearchUsersTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        search_users(name='foo')
        mock_api_login.assert_called_once_with()

    def test_returns_empty_dict_if_api_login_is_not_valid(
            self, mock_api_login):
        mock_api_login.return_value = None
        search_results = search_users(name='foo')
        self.assertEqual(search_results, {})
