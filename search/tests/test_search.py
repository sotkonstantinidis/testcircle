# Prevent logging of Elasticsearch queries
import logging
logging.disable(logging.CRITICAL)

import uuid
from django.test.utils import override_settings
from elasticsearch import TransportError
from unittest.mock import patch

from qcat.tests import TestCase
from search.index import (
    create_or_update_index,
    get_elasticsearch,
    put_questionnaire_data,
)
from search.search import simple_search


es = get_elasticsearch()
TEST_INDEX_PREFIX = 'qcat_test_prefix_'
TEST_ALIAS = uuid.uuid4()
TEST_ALIAS_PREFIXED = '{}{}'.format(TEST_INDEX_PREFIX, TEST_ALIAS)
TEST_INDEX = '{}_1'.format(TEST_ALIAS_PREFIXED)


def setup():
    """
    Create a new index with a random name for testing. Will be deleted
    after the tests ran.
    """
    try:
        es.indices.create(index=TEST_INDEX)
        es.indices.put_alias(index=TEST_INDEX, name=TEST_ALIAS_PREFIXED)
    except TransportError:
        raise Exception(
            'No connection to Elasticsearch possible. Make sure it is running '
            'and the configuration is correct.')


def teardown():
    """
    Delete the index used for testing.

    Use the following to delete all test indices::
        curl -XDELETE '[ES_HOST]:[ES_PORT]/[TEST_INDEX_PREFIX]*'

    Example::
        curl -XDELETE 'http://localhost:9200/qcat_test_prefix_*'
    """
    try:
        es.indices.delete(index='{}*'.format(TEST_INDEX_PREFIX))
    except TransportError:
        raise Exception(
            'Index of Elasticsearch could not be deleted, manual cleanup '
            'necessary.')


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class SimpleSearchTest(TestCase):

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_calls_get_alias_with_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_code='code')
        mock_get_alias.assert_called_once_with('code')

    @patch('search.search.es')
    @patch('search.search.get_alias')
    def test_not_calls_get_alias_if_no_code(self, mock_get_alias, mock_es):
        simple_search('key', configuration_code=None)
        self.assertEqual(mock_get_alias.call_count, 0)

    @patch('search.search.es')
    def test_calls_search(self, mock_es):
        simple_search('key')
        mock_es.search.assert_called_once_with(index=None, q='key')

    @patch('search.search.es')
    def test_returns_search(self, mock_es):
        ret = simple_search('key')
        self.assertEqual(ret, mock_es.search())

    def test_returns_hits_with_code(self):
        put_questionnaire_data(TEST_ALIAS, [{"foo": "bar"}])
        search = simple_search('bar', configuration_code=TEST_ALIAS)
        hits = search.get('hits', {}).get('hits', [])
        self.assertEqual(len(hits), 1)

    def test_returns_hits_without_code(self):
        put_questionnaire_data(TEST_ALIAS, [{"foo": "bar"}])
        search = simple_search('bar')
        hits = search.get('hits', {}).get('hits', [])
        self.assertEqual(len(hits), 1)

    def test_returns_all_hits_without_code(self):
        alias = uuid.uuid4()
        index = '{}{}_1'.format(TEST_INDEX_PREFIX, alias)
        create_or_update_index(alias, {})
        put_questionnaire_data(TEST_ALIAS, [{"foo": "bar"}])
        put_questionnaire_data(alias, [{"faz": "bar"}])
        search = simple_search('bar')
        hits = search.get('hits', {}).get('hits', [])
        self.assertEqual(len(hits), 2)
        es.indices.delete(index=index)

    def test_returns_only_hits_from_code_with_code(self):
        alias = uuid.uuid4()
        index = '{}{}_1'.format(TEST_INDEX_PREFIX, alias)
        create_or_update_index(alias, {})
        put_questionnaire_data(TEST_ALIAS, [{"foo": "bar"}])
        put_questionnaire_data(alias, [{"faz": "bar"}])
        search = simple_search('bar', configuration_code=TEST_ALIAS)
        hits = search.get('hits', {}).get('hits', [])
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0].get('_source').get('data'), {'foo': 'bar'})
        es.indices.delete(index=index)
