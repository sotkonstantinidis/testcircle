from django.test.utils import override_settings
from unittest.mock import patch, Mock

from configuration.cache import (
    delete_configuration_cache,
    get_configuration,
)
from qcat.tests import TestCase


@patch('configuration.cache.cache')
class GetConfigurationQueryFilterTest(TestCase):

    @override_settings(USE_CACHING=False)
    @patch('configuration.cache.QuestionnaireConfiguration')
    def test_get_configuration_creates_conf_if_use_caching_settings_false(
            self, mock_QuestionnaireConfiguration, mock_cache):
        get_configuration('foo')
        self.assertEqual(mock_cache.call_count, 0)
        mock_QuestionnaireConfiguration.assert_called_once_with('foo')

    @override_settings(USE_CACHING=True)
    def test_returns_cache_if_found(self, mock_cache):
        mock_cache.get.return_value = 'bar'
        ret = get_configuration('foo')
        self.assertEqual(ret, 'bar')

    @override_settings(USE_CACHING=True)
    @patch('configuration.cache.QuestionnaireConfiguration')
    def test_creates_conf_if_not_found(
            self, mock_QuestionnaireConfiguration, mock_cache):
        mock_cache.get.return_value = None
        ret = get_configuration('foo')
        self.assertEqual(ret, mock_QuestionnaireConfiguration.return_value)

    @override_settings(USE_CACHING=True)
    def test_does_not_set_cache_if_found(self, mock_cache):
        mock_cache.get.return_value = 'bar'
        get_configuration('foo')
        self.assertEqual(mock_cache.set.call_count, 0)

    @override_settings(USE_CACHING=True)
    @patch('configuration.cache.QuestionnaireConfiguration')
    def test_sets_cache_if_not_found(
            self, mock_QuestionnaireConfiguration, mock_cache):
        mock_cache.get.return_value = None
        get_configuration('foo')
        mock_cache.set.assert_called_once_with(
            'foo', mock_QuestionnaireConfiguration.return_value)


@patch('configuration.cache.cache')
class DeleteConfigurationCacheTest(TestCase):

    @override_settings(USE_CACHING=True)
    def test_calls_delete_many(self, mock_cache):
        conf = Mock()
        delete_configuration_cache(conf)
        mock_cache.delete_many.assert_called_once_with([conf.code])

    @override_settings(USE_CACHING=False)
    def test_does_not_call_delete_many_if_use_caching_settings_false(
            self, mock_cache):
        conf = Mock()
        delete_configuration_cache(conf)
        self.assertEqual(mock_cache.delete_many.call_count, 0)
