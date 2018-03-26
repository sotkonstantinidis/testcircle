# Prevent logging of Elasticsearch queries
import logging
logging.disable(logging.CRITICAL)

import collections

from django.db.models import Q
from django.test.utils import override_settings

from qcat.tests import TestCase
from questionnaire.models import Questionnaire
from questionnaire.utils import get_list_values
from search.index import (
    delete_all_indices,
)
from search.search import (
    advanced_search,
    simple_search,
)
from search.tests.test_index import create_temp_indices

TEST_INDEX_PREFIX = 'qcat_test_prefix_'

FilterParam = collections.namedtuple(
            'FilterParam',
            ['questiongroup', 'key', 'values', 'operator', 'type'])


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class SimpleSearchTest(TestCase):

    fixtures = [
        'global_key_values.json', 'sample.json', 'samplemulti.json',
        'sample_questionnaires_search.json']

    def setUp(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)
        create_temp_indices(['sample', 'samplemulti'])

    def tearDown(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)

    def test_simple_search_returns_results_of_code(self):
        key_search = simple_search(
            'key', configuration_codes=['sample']).get('hits')
        self.assertEqual(key_search.get('total'), 2)

        one_search = simple_search(
            'one', configuration_codes=['sample']).get('hits')
        self.assertEqual(one_search.get('total'), 1)

    def test_simple_search_returns_all_results_if_no_code(self):
        """
        Careful: This also returns results from other indices (eg. the
        productive indices)!
        """
        key_search = simple_search('key', configuration_codes=[]).get('hits')
        self.assertEqual(key_search.get('total'), 3)

        one_search = simple_search('one', configuration_codes=[]).get('hits')
        self.assertEqual(one_search.get('total'), 1)


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class AdvancedSearchTest(TestCase):

    fixtures = [
        'global_key_values.json', 'sample.json', 'samplemulti.json',
        'sample_questionnaires_search.json']

    def setUp(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)
        create_temp_indices(['sample', 'samplemulti'])

    def tearDown(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)

    def test_advanced_search(self):
        filter_param = FilterParam(
            questiongroup='qg_1', key='key_1', values=['key'], operator='eq',
            type='char')
        key_search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']).get('hits')
        self.assertEqual(key_search.get('total'), 2)

        filter_param = FilterParam(
            questiongroup='qg_1', key='key_1', values=['one'], operator='eq',
            type='char')
        one_search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']).get('hits')
        self.assertEqual(one_search.get('total'), 1)

    def test_advanced_search_single_filter(self):
        filter_param = FilterParam(
            questiongroup='qg_11', key='key_14', values=['value_14_1'],
            operator='eq', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param], configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 2)

    def test_advanced_search_multiple_arguments(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_1', key='key_1', values=['key'],
            operator='eq', type='char')
        filter_param_2 = FilterParam(
            questiongroup='qg_19', key='key_5', values=['5'],
            operator='eq', type='char')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 1)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['1'])

    def test_advanced_search_multiple_arguments_match_one(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_1', key='key_1', values=['key'],
            operator='eq', type='char')
        filter_param_2 = FilterParam(
            questiongroup='qg_19', key='key_5', values=['5'],
            operator='eq', type='char')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample'],
            match_all=False
        ).get('hits')
        self.assertEqual(search.get('total'), 2)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['1', '2'])

    def test_advanced_search_multiple_arguments_2_match_one(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_1', key='key_1', values=['key'],
            operator='eq', type='char')
        filter_param_2 = FilterParam(
            questiongroup='qg_11', key='key_14', values=['value_14_1'],
            operator='eq', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample'],
            match_all=False
        ).get('hits')
        self.assertEqual(search.get('total'), 3)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['1', '5', '2'])

    def test_advanced_search_multiple_arguments_2(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_1', key='key_1', values=['key'],
            operator='eq', type='char')
        filter_param_2 = FilterParam(
            questiongroup='qg_11', key='key_14', values=['value_14_1'],
            operator='eq', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 1)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['1'])

    def test_advanced_search_multiple_arguments_same_filter(self):
        filter_param = FilterParam(
            questiongroup='qg_11', key='key_14',
            values=['value_14_1', 'value_14_3'],
            operator='eq', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 3)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['4', '1', '5'])

    def test_advanced_search_multiple_arguments_same_filter_2(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_11', key='key_14',
            values=['value_14_1', 'value_14_3'],
            operator='eq', type='image_checkbox')
        filter_param_2 = FilterParam(
            questiongroup='qg_35', key='key_48', values=['value_3'],
            operator='eq', type='radio')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 1)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['4'])

    def test_advanced_search_multiple_arguments_same_filter_2_match_one(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_11', key='key_14',
            values=['value_14_1', 'value_14_3'],
            operator='eq', type='image_checkbox')
        filter_param_2 = FilterParam(
            questiongroup='qg_35', key='key_48', values=['value_2'],
            operator='eq', type='radio')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample'],
            match_all=False,
        ).get('hits')
        self.assertEqual(search.get('total'), 4)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['2', '4', '1', '5'])

    def test_advanced_search_gte(self):
        filter_param = FilterParam(
            questiongroup='qg_11', key='key_14', values=['2'],
            operator='gte', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 2)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['4', '1'])

    def test_advanced_search_lt(self):
        filter_param = FilterParam(
            questiongroup='qg_11', key='key_14', values=['2'],
            operator='lt', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 2)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['5', '1'])

    def test_advanced_search_lte(self):
        filter_param = FilterParam(
            questiongroup='qg_35', key='key_48', values=['2'],
            operator='lte', type='radio')
        search = advanced_search(
            filter_params=[filter_param],
            configuration_codes=['sample']
        ).get('hits')
        self.assertEqual(search.get('total'), 2)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['2', '1'])

    def test_advanced_search_gte_lte(self):
        filter_param_1 = FilterParam(
            questiongroup='qg_11', key='key_14', values=['1'],
            operator='lte', type='image_checkbox')
        filter_param_2 = FilterParam(
            questiongroup='qg_11', key='key_14', values=['3'],
            operator='gte', type='image_checkbox')
        search = advanced_search(
            filter_params=[filter_param_1, filter_param_2],
            configuration_codes=['sample'],
            match_all=False,
        ).get('hits')
        self.assertEqual(search.get('total'), 3)
        hit_ids = [r.get('_id') for r in search.get('hits')]
        self.assertEqual(hit_ids, ['5', '4', '1'])

@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class GetListValuesTest(TestCase):

    fixtures = [
        'global_key_values.json', 'sample.json', 'samplemulti.json',
        'sample_questionnaires_search.json']

    def setUp(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)
        create_temp_indices(['sample', 'samplemulti'])

    def tearDown(self):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)

    def test_returns_same_result_for_es_search_and_db_objects(self):
        res_1 = get_list_values(
            configuration_code='sample', es_hits=simple_search(
                'key', configuration_codes=['sample']).get(
                'hits', {}).get('hits', []))
        ids = [q.get('id') for q in res_1]
        res_2 = get_list_values(
            configuration_code='sample',
            questionnaire_objects=Questionnaire.objects.filter(pk__in=ids),
            status_filter=Q())

        for res in [res_1, res_2]:
            for r in res:
                self.assertEqual(r.get('configuration'), 'sample')
                # self.assertEqual(r.get('configurations'), ['sample'])
                self.assertIn('key_1', r)
                self.assertIn('key_5', r)
                self.assertIn('created', r)
                self.assertIn('updated', r)

    def test_returns_results_for_non_native_results(self):
        res = get_list_values(
            configuration_code='sample', es_hits=simple_search(
                'key', configuration_codes=['samplemulti']).get(
                'hits', {}).get('hits', []))

        self.assertEqual(len(res), 1)
        res = res[0]
        self.assertEqual(res.get('configuration'), 'sample')
        # After introduction of versioned configuration, there does not seem to
        # be a way to flag un-native configurations anymore?
        self.assertNotIn('key_1', res)
        self.assertNotIn('key_5', res)
        self.assertIn('created', res)
        self.assertIn('updated', res)
