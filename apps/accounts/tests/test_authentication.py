import unittest

from django.contrib.auth import get_user_model
from unittest.mock import patch

from qcat.tests import TestCase
from ..authentication import WocatAuthenticationBackend
from ..client import typo3_client, Typo3Client, WocatWebsiteUserClient

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


def get_mock_user_information_values_cms():
    return {
        'pk': 1,
        'email': 'foo@bar.com',
        'first_name': 'Foo',
        'last_name': 'Bar',
    }


class WOCATCMSAuthenticateTest(TestCase):

    def setUp(self):
        self.typo3_client = WocatWebsiteUserClient()

    def test_existing_user_updates(self):
        # Existing users have their information updated
        user_info = get_mock_user_information_values_cms()
        User.objects.create(id=user_info['pk'], email=user_info['email'])

        user = self.typo3_client.get_and_update_django_user(**user_info)

        self.assertEqual(user.id, user_info['pk'])
        self.assertEqual(user.email, user_info['email'])
        self.assertEqual(user.firstname, user_info['first_name'])
        self.assertEqual(user.lastname, user_info['last_name'])

    def test_new_user_updates(self):
        # New users should also have their information updated
        user_info = get_mock_user_information_values_cms()

        user = self.typo3_client.get_and_update_django_user(**user_info)

        self.assertEqual(user.id, user_info['pk'])
        self.assertEqual(user.email, user_info['email'])
        self.assertEqual(user.firstname, user_info['first_name'])
        self.assertEqual(user.lastname, user_info['last_name'])


@unittest.skip("Temporarily disabled. @Sebastian, please reactivate")
class ValidateSessionTest(TestCase):

    @patch('accounts.client.typo3_client.get_user_id')
    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_id = typo3_client.get_user_id('foo')
        self.assertIsNone(user_id)


@unittest.skip("Temporarily disabled. @Sebastian, please reactivate")
@patch('accounts.client.typo3_client.api_login')
class GetUserInformationTest(TestCase):

    def test_returns_None_if_api_login_is_not_valid(self, mock_api_login):
        mock_api_login.return_value = None
        user_info = typo3_client.get_user_information(1)
        self.assertIsNone(user_info)


@unittest.skip("Temporarily disabled. @Sebastian, please reactivate")
class SearchUsersTest(TestCase):

    @patch.object(Typo3Client, 'api_login')
    def test_returns_empty_dict_if_api_login_is_not_valid(
            self, mock_api_login):
        mock_api_login.return_value = None
        search_results = typo3_client.search_users(name='foo')
        self.assertEqual(search_results, {})
