from unittest.mock import patch, Mock

from django.conf import settings
from django.db.models import Q

from configuration.utils import (
    create_new_code,
    get_configuration_index_filter,
    get_configuration_query_filter,
    get_choices_from_model)
from qcat.tests import TestCase
from search.index import delete_all_indices
from search.tests.test_index import ESIndexMixin, create_temp_indices, TEST_ALIAS_PREFIXED

DEFAULT_WOCAT_CONFIGURATIONS = [
    'unccd', 'technologies', 'approaches', 'watershed']


class GetConfigurationQueryFilterTest(TestCase):

    def test_returns_configuration_query(self):
        query_filter = get_configuration_query_filter('foo')
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0][0], 'configuration__code')
        self.assertEqual(attrs[0][1], 'foo')

    def test_returns_combined_query_for_wocat(self):
        query_filter = get_configuration_query_filter('wocat')
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 0)

    def test_returns_only_current_configuration_if_selected(self):
        query_filter = get_configuration_query_filter(
            'wocat', only_current=True)
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0][0], 'configuration__code')
        self.assertEqual(attrs[0][1], 'wocat')


class GetConfigurationIndexFilterTest(ESIndexMixin, TestCase):

    fixtures = ['sample']

    @property
    def test_alias(self):
        # Replace the 'key_prefix' of the index ('qcat_')
        return TEST_ALIAS_PREFIXED.replace(settings.ES_INDEX_PREFIX, '')

    def setUp(self):
        super().setUp()
        delete_all_indices()
        create_temp_indices(['sample'])

    def tearDown(self):
        super().tearDown()
        delete_all_indices()

    @patch('configuration.utils.check_aliases')
    def test_returns_single_configuration(self, mock_check_aliases):
        mock_check_aliases.return_value = True
        index_filter = get_configuration_index_filter('foo')
        self.assertEqual(index_filter, ['foo'])

    @patch('configuration.utils.check_aliases')
    def test_calls_check_aliases(self, mock_check_aliases):
        get_configuration_index_filter('foo')
        mock_check_aliases.assert_called_once_with(['foo'])

    def test_returns_default_configurations_if_not_valid_alias(self):
        index_filter = get_configuration_index_filter('foo')
        self.assertEqual(index_filter, DEFAULT_WOCAT_CONFIGURATIONS)

    @patch('configuration.utils.check_aliases')
    def test_unccd_returns_single_configuration(self, mock_check_aliases):
        mock_check_aliases.return_value = True
        index_filter = get_configuration_index_filter(self.test_alias)
        self.assertEqual(index_filter, [self.test_alias])

    def test_wocat_returns_multiple_configurations(self):
        index_filter = get_configuration_index_filter('wocat')
        self.assertEqual(index_filter, DEFAULT_WOCAT_CONFIGURATIONS)

    @patch('configuration.utils.check_aliases')
    def test_wocat_with_only_current_returns_only_wocat(self, mock_check_aliases):
        mock_check_aliases.return_value = True
        index_filter = get_configuration_index_filter('wocat', only_current=True)
        self.assertEqual(index_filter, ['wocat'])

    @patch('configuration.utils.check_aliases')
    def test_returns_query_params_lower_case(self, mock_check_aliases):
        mock_check_aliases.return_value = True
        index_filter = get_configuration_index_filter(
            'sample', query_param_filter=(self.test_alias.upper(),))
        self.assertEqual(index_filter, [self.test_alias.lower()])


class CreateNewCodeTest(TestCase):

    def test_returns_string(self):
        obj = Mock()
        code = create_new_code(obj, 'sample')
        self.assertIsInstance(code, str)

    def test_returns_new_code(self):
        obj = Mock()
        obj.id = '99'
        code = create_new_code(obj, 'sample')
        self.assertEqual(code, 'sample_99')


class GetChoicesFromModelTest(TestCase):

    fixtures = ['sample_projects']

    def test_returns_empty_if_model_not_found(self):
        choices = get_choices_from_model('foo')
        self.assertEqual(choices, [])

    def test_filters_active_by_default(self):
        choices = get_choices_from_model('Project')
        self.assertEqual(len(choices), 2)

    def test_active_filter_false(self):
        choices = get_choices_from_model('Project', only_active=False)
        self.assertEqual(len(choices), 3)

    def test_returns_ordered_choices(self):
        choices = get_choices_from_model('Project')
        self.assertEqual(
            choices[0][1],
            'International Project for Collecting Technologies (IPCT)')
        self.assertEqual(
            choices[1][1], 'The first Project (TFP)')

