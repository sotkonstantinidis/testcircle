from django.db.models import Q

from configuration.utils import (
    get_configuration_index_filter,
    get_configuration_query_filter,
)
from qcat.tests import TestCase


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
        self.assertEqual(len(attrs), 2)
        self.assertEqual(attrs[0][0], 'configurations__code')
        self.assertEqual(attrs[0][1], 'wocat')
        self.assertEqual(attrs[1][0], 'configurations__code')
        self.assertEqual(attrs[1][1], 'unccd')
        self.assertEqual(query_filter.connector, 'OR')

    def test_returns_only_current_configuration_if_selected(self):
        query_filter = get_configuration_query_filter(
            'wocat', only_current=True)
        self.assertIsInstance(query_filter, Q)
        attrs = query_filter.children
        self.assertEqual(len(attrs), 1)
        self.assertEqual(attrs[0][0], 'configurations__code')
        self.assertEqual(attrs[0][1], 'wocat')


class GetConfigurationIndexFilter(TestCase):

    def test_returns_single_configuration(self):
        index_filter = get_configuration_index_filter('foo')
        self.assertEqual(index_filter, ['foo'])

    def test_unccd_returns_single_configuration(self):
        index_filter = get_configuration_index_filter('unccd')
        self.assertEqual(index_filter, ['unccd'])

    def test_wocat_returns_multiple_configurations(self):
        index_filter = get_configuration_index_filter('wocat')
        self.assertEqual(index_filter, ['unccd', 'wocat'])

    def test_wocat_with_only_current_returns_only_wocat(self):
        index_filter = get_configuration_index_filter(
            'wocat', only_current=True)
        self.assertEqual(index_filter, ['wocat'])
