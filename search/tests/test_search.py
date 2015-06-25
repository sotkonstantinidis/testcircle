from unittest.mock import patch

from qcat.tests import TestCase
from search.search import (
    simple_search,
    advanced_search,
)


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


class SimpleSearchTest(TestCase):

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_with_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_codes=['code'])
        mock_get_alias.assert_called_once_with(['code'])

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_if_no_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_codes=[])
        mock_get_alias.assert_called_once_with([])

    @patch('search.search.get_alias')
    @patch('search.search.es')
    def test_calls_search(self, mock_es, mock_get_alias):
        simple_search('key')
        mock_es.search.assert_called_once_with(
            index=mock_get_alias.return_value, q='key')

    @patch('search.search.es')
    def test_returns_search(self, mock_es):
        ret = simple_search('key')
        self.assertEqual(ret, mock_es.search())


class AdvancedSearchTest(TestCase):

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_with_code(self, mock_get_alias, mock_es):
        advanced_search(filter_params=[], configuration_codes=['code'])
        mock_get_alias.assert_called_once_with(['code'])

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_if_no_code(self, mock_get_alias, mock_es):
        advanced_search(filter_params=[], configuration_codes=[])
        mock_get_alias.assert_called_once_with([])

    @patch('search.search.get_alias')
    @patch('search.search.es')
    def test_calls_search(self, mock_es, mock_get_alias):
        advanced_search(filter_params=[])
        mock_es.search.assert_called_once_with(
            index=mock_get_alias.return_value,
            body={'query': {'bool': {'must': []}}, 'sort': [
                {'updated': 'desc'}]}, size=10)

    @patch('search.search.es')
    def test_returns_search(self, mock_es):
        ret = advanced_search(filter_params=[])
        self.assertEqual(ret, mock_es.search())
