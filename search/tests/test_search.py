from django.test.utils import override_settings
from unittest.mock import patch

from qcat.tests import TestCase
from search.search import (
    simple_search,
    advanced_search,
)


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class SimpleSearchTest(TestCase):

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_with_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_code='code')
        mock_get_alias.assert_called_once_with('code')

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_if_no_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_code=None)
        mock_get_alias.assert_called_once_with('*')

    @patch('search.search.es')
    def test_calls_search(self, mock_es):
        simple_search('key')
        mock_es.search.assert_called_once_with(
            index='{}*'.format(TEST_INDEX_PREFIX), q='key')

    @patch('search.search.es')
    def test_returns_search(self, mock_es):
        ret = simple_search('key')
        self.assertEqual(ret, mock_es.search())


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class AdvancedSearchTest(TestCase):

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_with_code(self, mock_get_alias, mock_es):
        advanced_search([], configuration_code='code')
        mock_get_alias.assert_called_once_with('code')

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_if_no_code(self, mock_get_alias, mock_es):
        advanced_search([], configuration_code=None)
        mock_get_alias.assert_called_once_with('*')

    @patch('search.search.es')
    def test_calls_search(self, mock_es):
        advanced_search([])
        mock_es.search.assert_called_once_with(
            index='{}*'.format(TEST_INDEX_PREFIX),
            body={'query': {'bool': {'must': []}}})

    @patch('search.search.es')
    def test_returns_search(self, mock_es):
        ret = advanced_search([])
        self.assertEqual(ret, mock_es.search())
