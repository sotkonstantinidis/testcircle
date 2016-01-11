from django.contrib.auth import get_user_model
from unittest.mock import patch
from qcat.tests import TestCase
from ..authentication import WocatAuthenticationBackend
from ..client import typo3_client
from .test_models import create_new_user


User = get_user_model()


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


@patch('accounts.client.typo3_client.get_user_id')
class AuthenticateTest(TestCase):

    def setUp(self):
        self.backend = WocatAuthenticationBackend()
        self.user = User.objects.get_or_create(
            id=1, email='foo@bar.com',
            defaults={'lastname': 'Foo', 'firstname': 'Bar'}
        )

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
        # actual_user = User.objects.create(id=1, email='test@qcat.com')
        mock_validate_session.return_value = get_mock_validate_session_values()
        found_user = self.backend.authenticate(token='foo')
        self.assertEqual(found_user, self.user)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_creates_new_user_if_necessary(self, mock_get_user_information,
                                           mock_validate_session):
        mock_get_user_information.return_value = \
            get_mock_user_information_values()
        mock_validate_session.return_value = get_mock_validate_session_values()
        found_user = self.backend.authenticate(token='foo')
        self.assertEqual(found_user, self.user)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_creates_new_user_calls_get_user_information(
            self, mock_get_user_information, mock_validate_session):
        mock_validate_session.return_value = get_mock_validate_session_values()
        self.backend.authenticate(token='foo')
        mock_get_user_information.assert_called_once_with(
            mock_validate_session.return_value)


@patch('accounts.client.typo3_client.remote_login')
class ValidateSessionTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        typo3_client.get_user_id('foo')
        mock_api_login.assert_called_once_with()

    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_id = typo3_client.get_user_id('foo')
        self.assertIsNone(user_id)


@patch('accounts.client.typo3_client.remote_login')
class GetUserInformationTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        typo3_client.get_user_information(1)
        mock_api_login.assert_called_once_with()

    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_info = typo3_client.get_user_information(1)
        self.assertIsNone(user_info)


@patch('accounts.client.typo3_client.remote_login')
class SearchUsersTest(TestCase):

    def test_calls_api_login(self, mock_api_login):
        typo3_client.search_users(name='foo')
        mock_api_login.assert_called_once_with()

    def test_returns_empty_dict_if_api_login_is_not_valid(
            self, mock_api_login):
        mock_api_login.return_value = None
        search_results = typo3_client.search_users(name='foo')
        self.assertEqual(search_results, {})
