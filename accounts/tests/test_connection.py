from django.test import TestCase
from unittest.mock import patch
from pymysql.err import OperationalError

from accounts.connection import get_connection


@patch('accounts.connection.settings')
class ConnectionTest(TestCase):

    def test_get_connection_returns_mysql_connection(self, mock_settings):
        mock_settings.AUTH_DATABASE = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'database',
            'USER': 'user',
            'PASSWORD': 'password',
            'HOST': 'host',
            'PORT': 3306
        }
        with self.assertRaises(OperationalError):
            get_connection()

    def test_get_connection_raises_exception_if_no_auth_database(
            self, mock_settings):
        with self.assertRaises(Exception):
            get_connection()

    def test_get_connection_raises_exception_if_no_mysql_engine(
            self, mock_settings):
        mock_settings.AUTH_DATABASE = {'ENGINE': 'foo'}
        with self.assertRaises(Exception):
            get_connection()
