import uuid
import logging

from django.conf import settings
from django.test.utils import override_settings
from elasticsearch import TransportError, RequestError
from unittest.mock import patch, Mock

from configuration.cache import get_configuration
from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from questionnaire.models import Questionnaire
from questionnaire.serializers import QuestionnaireSerializer
from questionnaire.tests.test_models import get_valid_questionnaire
from search.index import (
    create_or_update_index,
    delete_all_indices,
    delete_questionnaires_from_es,
    delete_single_index,
    get_elasticsearch,
    get_mappings,
    put_questionnaire_data,
)

# Prevent logging of Elasticsearch queries
logging.disable(logging.CRITICAL)


es = get_elasticsearch()
TEST_INDEX_PREFIX = 'qcat_test_prefix_'
TEST_ALIAS = uuid.uuid4()
TEST_ALIAS_PREFIXED = '{}{}'.format(TEST_INDEX_PREFIX, TEST_ALIAS)
TEST_INDEX = '{}_1'.format(TEST_ALIAS_PREFIXED)


def create_temp_indices(configuration_list: list):
    """
    For each index, create the index and update it with the
    questionnaires of the corresponding configuration as found in the
    database.

    Make sure to override the settings and use a custom prefix for the
    indices.

    Args:
        ``configuration_list`` (list): A list of tuples containing the
            configurations for which a ES index shall be created and consisting
            of
            - [0]: code of the configuration
            - [1]: edition of the configuration
    """
    for code, edition in configuration_list:
        mappings = get_mappings()
        create_or_update_index(
            get_configuration(code=code, edition=edition), mappings)
        put_questionnaire_data(
            Questionnaire.with_status.public().filter(configuration__code=code)
        )


class ESIndexMixin:

    def setUp(self):
        """
        Create a new index with a random name for testing. Will be deleted
        after the tests ran.
        """
        try:
            es.indices.create(index=TEST_INDEX)
            es.indices.put_alias(index=TEST_INDEX, name=TEST_ALIAS_PREFIXED)
        except TransportError:
            raise Exception(
                'No connection to Elasticsearch possible. Make sure it is '
                'running and the configuration is correct.')
        self.default_body = {
            'settings': {
                'index': {
                    'mapping': {
                        'nested_fields': {'limit': 250},
                        'total_fields': {'limit': 6000}
                    }
                }
            }, 'mappings': {}}

    def tearDown(self):
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


class GetMappingsTest(TestCase):
    def test_returns_dictionary(self):
        mappings = get_mappings()
        self.assertIsInstance(mappings, dict)
        self.assertIn('questionnaire', mappings)
        self.assertIn('properties', mappings['questionnaire'])
        # 'data' is not part of Elasticsearch index anymore
        self.assertNotIn('data', mappings['questionnaire']['properties'])
        # 'list_data' and 'filter_data' will be added dynamically to the mapping
        self.assertNotIn('list_data', mappings['questionnaire']['properties'])
        self.assertNotIn('filter_data', mappings['questionnaire']['properties'])

    @override_settings(ES_ANALYZERS=(('en', 'english'), ('es', 'spanish')))
    def test_adds_analyzer_for_strings(self):
        mappings = get_mappings()
        name_properties = mappings['questionnaire']['properties']['name'][
            'properties']
        self.assertEqual(
            name_properties['es'],
            {'analyzer': 'spanish', 'type': 'text'}
        )
        self.assertEqual(
            name_properties['en'],
            {'analyzer': 'english', 'type': 'text'}
        )

    def test_adds_basic_mappings(self):
        mappings = get_mappings()
        q_props = mappings.get('questionnaire').get('properties')
        self.assertEqual(len(q_props), 11)
        default_props = {}
        for global_questiongroup in settings.QUESTIONNAIRE_GLOBAL_QUESTIONGROUPS:
            default_props[global_questiongroup] = {'properties': {}, 'type': 'nested'}
            if global_questiongroup == 'qg_location':
                default_props[global_questiongroup]['properties'] = {'country': {'type': 'text'}}

        self.assertEqual(q_props['created'], {'type': 'date'})
        self.assertEqual(q_props['updated'], {'type': 'date'})
        self.assertEqual(q_props['translations'], {'type': 'text'})
        self.assertEqual(q_props['configurations'], {'type': 'text'})
        self.assertEqual(q_props['code'], {'type': 'text'})
        self.assertIn('name', q_props)
        self.assertIn('links', q_props)
        self.assertEqual(
            q_props['compilers'],
            {'type': 'nested', 'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'text'}}})
        self.assertEqual(
            q_props['editors'],
            {'type': 'nested', 'properties': {
                'id': {'type': 'integer'},
                'name': {'type': 'text'}}})


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class CreateOrUpdateIndexTest(ESIndexMixin, TestCase):

    fixtures = ['sample.json', 'sample_global_key_values.json']

    def setUp(self):
        super().setUp()
        self.keyword = 'foo'
        self.edition = '2015'
        self.configuration = Mock(
            spec=QuestionnaireConfiguration, keyword=self.keyword,
            edition=self.edition)

    @patch('search.index.ElasticsearchAlias')
    @patch('search.index.get_alias')
    def test_calls_get_alias(self, mock_get_alias, mock_es_alias):
        with self.assertRaises(RequestError):
            create_or_update_index(self.configuration, {})
        mock_es_alias.from_configuration.assert_called_once_with(
            configuration=self.configuration)
        mock_get_alias.assert_called_once_with(
            mock_es_alias.from_configuration.return_value)

    @patch('search.index.es')
    def test_calls_indices_exists_alias(self, mock_es):
        create_or_update_index(self.configuration, {})
        mock_es.indices.exists_alias.assert_called_once_with(
            name=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}')

    @patch('search.index.es')
    def test_calls_indices_create_if_no_alias(self, mock_es):
        mock_es.indices.exists_alias.return_value = False
        create_or_update_index(self.configuration, {})
        mock_es.indices.create.assert_called_once_with(
            index=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}_1',
            body=self.default_body)

    @patch('search.index.es')
    def test_calls_indices_put_alias_if_no_alias(self, mock_es):
        mock_es.indices.exists_alias.return_value = False
        mock_es.indices.create.return_value = {'acknowledged': True}
        create_or_update_index(self.configuration, {})
        mock_es.indices.put_alias.assert_called_once_with(
            index=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}_1',
            name=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}')

    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_get_current_index_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index):
        mock_es.indices.exists_alias.return_value = True
        mock_get_current_and_next_index.return_value = 'a', 'b'
        create_or_update_index(self.configuration, {})
        mock_get_current_and_next_index.assert_called_once_with(
            f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}')

    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_create_index_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index):
        mock_es.indices.exists_alias.return_value = True
        mock_get_current_and_next_index.return_value = 'a', 'b'
        create_or_update_index(self.configuration, {})
        mock_es.indices.create.assert_called_once_with(
            index='b', body=self.default_body)

    @patch('search.index.reindex')
    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_reindex_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index, mock_reindex):
        mock_es.indices.exists_alias.return_value = True
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_get_current_and_next_index.return_value = 'a', 'b'
        mock_reindex.return_value = 0, []
        create_or_update_index(self.configuration, {})
        mock_reindex.assert_called_once_with(mock_es, 'a', 'b')

    @patch('search.index.reindex')
    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_refresh_indices_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index, mock_reindex):
        mock_es.indices.exists_alias.return_value = True
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_get_current_and_next_index.return_value = 'a', 'b'
        mock_reindex.return_value = 0, []
        create_or_update_index(self.configuration, {})
        mock_es.indices.refresh.assert_called_once_with(index='b')

    @patch('search.index.reindex')
    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_put_alias_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index, mock_reindex):
        mock_es.indices.exists_alias.return_value = True
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_get_current_and_next_index.return_value = 'a', 'b'
        mock_reindex.return_value = 0, []
        create_or_update_index(self.configuration, {})
        mock_es.indices.put_alias.assert_called_once_with(
            index='b', name=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}')

    @patch('search.index.reindex')
    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_delete_alias_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index, mock_reindex):
        mock_es.indices.exists_alias.return_value = True
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_get_current_and_next_index.return_value = 'a', 'b'
        mock_reindex.return_value = 0, []
        mock_es.indices.put_alias.return_value = {'acknowledged': True}
        create_or_update_index(self.configuration, {})
        mock_es.indices.delete_alias.assert_called_once_with(
            index='a', name=f'{TEST_INDEX_PREFIX}{self.keyword}_{self.edition}')

    @patch('search.index.reindex')
    @patch('search.index.get_current_and_next_index')
    @patch('search.index.es')
    def test_calls_delete_if_alias_exists(
            self, mock_es, mock_get_current_and_next_index, mock_reindex):
        mock_es.indices.exists_alias.return_value = True
        mock_es.indices.create.return_value = {'acknowledged': True}
        mock_get_current_and_next_index.return_value = 'a', 'b'
        mock_reindex.return_value = 0, []
        mock_es.indices.put_alias.return_value = {'acknowledged': True}
        mock_es.indices.delete_alias.return_value = {'acknowledged': True}
        create_or_update_index(self.configuration, {})
        mock_es.indices.delete.assert_called_once_with(index='a')

    @patch('search.index.get_alias')
    def test_creates_new_index(self, mock_get_alias):
        alias = uuid.uuid4()
        alias_prefixed = '{}{}'.format(TEST_INDEX_PREFIX, alias)
        mock_get_alias.return_value = alias_prefixed
        index = '{}{}_1'.format(TEST_INDEX_PREFIX, alias)
        self.assertFalse(es.indices.exists_alias(name=alias_prefixed))
        self.assertFalse(es.indices.exists(index=index))
        create_or_update_index(self.configuration, {})
        self.assertTrue(es.indices.exists_alias(name=alias_prefixed))
        self.assertTrue(es.indices.exists(index=index))
        es.indices.delete(index=index)

    # def test_keeps_data(self):
    #     m = get_valid_questionnaire()
    #     put_questionnaire_data([m])
    #     search = simple_search('bar', configuration_codes=['sample'])
    #     hits = search.get('hits', {}).get('hits', [])
    #     self.assertEqual(len(hits), 1)
    #     create_or_update_index(self.configuration, {})
    #     search = simple_search('bar', configuration_codes=['sample'])
    #     hits = search.get('hits', {}).get('hits', [])
    #     self.assertEqual(len(hits), 1)

    def test_returns_correct_values(self):
        success, logs, error_msg = create_or_update_index(self.configuration, {})
        self.assertIsInstance(success, bool)
        self.assertTrue(success)
        self.assertIsInstance(logs, list)
        self.assertEqual(len(logs), 3)
        self.assertEqual(error_msg, '')

    @patch('search.index.force_strings')
    def test_calls_force_string(self, mock_force_strings):
        m = get_valid_questionnaire()
        mock_force_strings.return_value = {}
        put_questionnaire_data([m])
        mock_force_strings.assert_called_once_with({'name': {}, 'definition': {'en': ''}})


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class PutQuestionnaireDataTest(TestCase):

    fixtures = ['sample.json', 'sample_global_key_values.json']

    @patch('search.index.bulk')
    @patch('search.index.es')
    @patch('search.index.get_alias')
    def test_calls_get_alias(self, mock_get_alias, mock_es, mock_bulk):
        mock_get_alias.return_value = ''
        mock_bulk.return_value = None, None
        put_questionnaire_data([get_valid_questionnaire()])
        mock_get_alias.assert_called_once()

    @patch('search.index.es')
    @patch('search.index.bulk')
    def test_calls_bulk(self, mock_bulk, mock_es):
        mock_bulk.return_value = 0, []
        questionnaire = get_valid_questionnaire()
        put_questionnaire_data([questionnaire])
        source = dict(QuestionnaireSerializer(
            questionnaire
        ).data)
        source['filter_data'] = {}
        source['list_data']['country'] = ''
        data = [{
            '_index': '{}sample_2015'.format(TEST_INDEX_PREFIX),
            '_type': 'questionnaire',
            '_id': questionnaire.id,
            '_source': source,
        }]
        mock_bulk.assert_called_once_with(mock_es, data)

    @patch('search.index.es')
    def test_calls_indices_refresh(self, mock_es):
        put_questionnaire_data([])
        mock_es.indices.refresh.assert_called_once_with(index='')

    @patch('search.index.es')
    @patch('search.index.bulk')
    def test_returns_values(self, mock_bulk, mock_es):
        mock_bulk.return_value = 'foo', 'bar'
        actions, errors = put_questionnaire_data([])
        self.assertEqual(actions, 'foo')
        self.assertEqual(errors, 'bar')


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class DeleteQuestionnairesFromEsTest(TestCase):
    def setUp(self):
        self.objects = [Mock()]

    @patch('search.index.es')
    def test_calls_indices_delete(self, mock_es):
        obj = self.objects[0]
        obj_configuration = obj.configuration_object
        delete_questionnaires_from_es(self.objects)
        mock_es.delete.assert_called_once_with(
            index=f'{TEST_INDEX_PREFIX}{obj_configuration.keyword}_'
                  f'{obj_configuration.edition}',
            doc_type='questionnaire', id=obj.id)

    def test_fails_silently_if_no_such_object(self):
        delete_questionnaires_from_es(self.objects)


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class DeleteAllIndicesTest(TestCase):
    @patch('search.index.es')
    def test_calls_indices_delete(self, mock_es):
        delete_all_indices(prefix=TEST_INDEX_PREFIX)
        mock_es.indices.delete.assert_called_once_with(index='{}*'.format(
            TEST_INDEX_PREFIX))

    @patch('search.index.es')
    def test_returns_false_if_no_success(self, mock_es):
        mock_es.indices.delete.return_value = {'acknowledged': False}
        success, error_msg = delete_all_indices(prefix=TEST_INDEX_PREFIX)
        self.assertFalse(success)
        self.assertEqual(error_msg, 'Indices could not be deleted')

    @patch('search.index.es')
    def test_returns_true_if_no_success(self, mock_es):
        mock_es.indices.delete.return_value = {'acknowledged': True}
        success, error_msg = delete_all_indices(prefix=TEST_INDEX_PREFIX)
        self.assertTrue(success)
        self.assertEqual(error_msg, '')


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class DeleteSingleIndexTest(TestCase):
    @patch('search.index.es')
    def test_calls_indices_delete(self, mock_es):
        delete_single_index('index')
        mock_es.indices.delete.assert_called_once_with(
            index='index', ignore=[404])

    @patch('search.index.es')
    def test_returns_false_if_no_success(self, mock_es):
        mock_es.indices.delete.return_value = {'acknowledged': False}
        success, error_msg = delete_single_index('index')
        self.assertFalse(success)
        self.assertEqual(error_msg, 'Index could not be deleted')

    @patch('search.index.es')
    def test_returns_true_if_no_success(self, mock_es):
        mock_es.indices.delete.return_value = {'acknowledged': True}
        success, error_msg = delete_single_index('index')
        self.assertTrue(success)
        self.assertEqual(error_msg, '')
