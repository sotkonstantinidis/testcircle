# Prevent logging of Elasticsearch queries
import logging
logging.disable(logging.CRITICAL)

from django.test.utils import override_settings
from elasticsearch import TransportError

from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from questionnaire.models import Questionnaire
from questionnaire.utils import get_list_values
from search.index import (
    create_or_update_index,
    get_elasticsearch,
    get_mappings,
    put_questionnaire_data,
)
from search.search import (
    advanced_search,
    simple_search,
)

es = get_elasticsearch()
TEST_INDEX_PREFIX = 'qcat_test_prefix_'
TEST_ALIAS_1 = 'sample'
TEST_ALIAS_2 = 'samplemulti'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
def setup():
    """
    Create a new index with a random name for testing. Will be deleted
    after the tests ran.
    """
    from django.core.management import call_command
    for fixture in [
            'global_key_values.json',
            'sample.json', 'samplemulti.json',
            'sample_questionnaires_search.json']:
        call_command('loaddata', fixture)
    sample_configuration = QuestionnaireConfiguration('sample')
    mappings = get_mappings(sample_configuration)
    create_or_update_index(TEST_ALIAS_1, mappings)
    put_questionnaire_data(
        TEST_ALIAS_1,
        Questionnaire.objects.filter(configurations__code='sample'))
    create_or_update_index(TEST_ALIAS_2, mappings)
    put_questionnaire_data(
        TEST_ALIAS_2,
        Questionnaire.objects.filter(configurations__code='samplemulti'))


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
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

    def test_simple_search_returns_results_of_code(self):
        key_search = simple_search('key', configuration_code=TEST_ALIAS_1).get(
            'hits')
        self.assertEqual(key_search.get('total'), 2)

        one_search = simple_search('one', configuration_code=TEST_ALIAS_1).get(
            'hits')
        self.assertEqual(one_search.get('total'), 1)

    def test_simple_search_returns_all_results_if_no_code(self):
        key_search = simple_search('key', configuration_code=None).get('hits')
        self.assertEqual(key_search.get('total'), 3)

        one_search = simple_search('one', configuration_code=None).get('hits')
        self.assertEqual(one_search.get('total'), 1)


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class AdvancedSearchTest(TestCase):

    def test_advanced_search(self):
        key_search = advanced_search(
            [('qg_1', 'key_1', 'key', 'eq')],
            configuration_code=TEST_ALIAS_1).get('hits')
        self.assertEqual(key_search.get('total'), 2)

        one_search = advanced_search(
            [('qg_1', 'key_1', 'one', 'eq')],
            configuration_code=TEST_ALIAS_1).get('hits')
        self.assertEqual(one_search.get('total'), 1)

    def test_advanced_search_multiple_arguments(self):
        search_1 = advanced_search(
            [('qg_1', 'key_1', 'key', 'eq'), ('qg_19', 'key_5', '5', 'eq')],
            configuration_code=TEST_ALIAS_1).get('hits')
        self.assertEqual(search_1.get('total'), 1)


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class GetListValuesTest(TestCase):

    def test_returns_same_result_for_es_search_and_db_objects(self):
        res_1 = get_list_values(
            configuration_code='sample', es_search=simple_search(
                'key', configuration_code='sample'))
        ids = [q.get('id') for q in res_1]
        res_2 = get_list_values(
            configuration_code='sample',
            questionnaire_objects=Questionnaire.objects.filter(pk__in=ids))

        for res in [res_1, res_2]:
            for r in res:
                self.assertEqual(r.get('configuration'), 'sample')
                self.assertEqual(r.get('configurations'), ['sample'])
                self.assertTrue(r.get('native_configuration'))
                self.assertIn('key_1', r)
                self.assertIn('key_5', r)
                self.assertIn('created', r)
                self.assertIn('updated', r)

    def test_returns_results_for_non_native_results(self):
        res = get_list_values(
            configuration_code='sample', es_search=simple_search(
                'key', configuration_code='samplemulti'))
        self.assertEqual(len(res), 1)
        res = res[0]
        self.assertEqual(res.get('configuration'), 'sample')
        self.assertEqual(res.get('configurations'), ['samplemulti'])
        self.assertFalse(res.get('native_configuration'))
        self.assertNotIn('key_1', res)
        self.assertNotIn('key_5', res)
        self.assertIn('created', res)
        self.assertIn('updated', res)
