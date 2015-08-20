from django.db.models import Q

from configuration.models import Configuration
from configuration.utils import (
    create_new_code,
    get_configuration_index_filter,
    get_configuration_query_filter,
)
from qcat.tests import TestCase
from questionnaire.models import Questionnaire
from questionnaire.tests.test_models import get_valid_questionnaire


class GetConfigurationQueryFilterTest(TestCase):

    def test_returns_configuration_query(self):
        query_filter = get_configuration_query_filter('foo')
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0][0], 'configurations__code')
        self.assertEqual(attrs[0][1], 'foo')

    def test_returns_combined_query_for_wocat(self):
        query_filter = get_configuration_query_filter('wocat')
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 3)
        self.assertEqual(attrs[0][0], 'configurations__code')
        self.assertEqual(attrs[0][1], 'technologies')
        self.assertEqual(attrs[1][0], 'configurations__code')
        self.assertEqual(attrs[1][1], 'approaches')
        self.assertEqual(attrs[2][0], 'configurations__code')
        self.assertEqual(attrs[2][1], 'unccd')
        self.assertEqual(query_filter.connector, 'OR')

    def test_returns_only_current_configuration_if_selected(self):
        query_filter = get_configuration_query_filter(
            'wocat', only_current=True)
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0][0], 'configurations__code')
        self.assertEqual(attrs[0][1], 'wocat')


class GetConfigurationIndexFilterTest(TestCase):

    def test_returns_single_configuration(self):
        index_filter = get_configuration_index_filter('foo')
        self.assertEqual(index_filter, ['foo'])

    def test_unccd_returns_single_configuration(self):
        index_filter = get_configuration_index_filter('unccd')
        self.assertEqual(index_filter, ['unccd'])

    def test_wocat_returns_multiple_configurations(self):
        index_filter = get_configuration_index_filter('wocat')
        self.assertEqual(index_filter, ['unccd', 'technologies', 'approaches'])

    def test_wocat_with_only_current_returns_only_wocat(self):
        index_filter = get_configuration_index_filter(
            'wocat', only_current=True)
        self.assertEqual(index_filter, ['wocat'])


class CreateNewCodeTest(TestCase):

    def test_returns_new_code(self):
        code = create_new_code('configuration', {})
        self.assertIsInstance(code, str)

    def test_always_returns_non_existing_code(self):
        Configuration(code='sample', active=True).save()
        questionnaire = get_valid_questionnaire()
        questionnaire.code = 'sample_1'
        questionnaire.save()
        code = create_new_code('sample', {})
        self.assertEqual(Questionnaire.objects.filter(code=code).count(), 0)
