from django.core.exceptions import ValidationError
from unittest.mock import patch

from configuration.models import Configuration
from qcat.tests import TestCase


def get_valid_configuration_model():
    return Configuration(
        code='sample', name='name', data={"foo": "bar"})


class ConfigurationModelTest(TestCase):

    def test_id_is_primary_key(self):
        conf = get_valid_configuration_model()
        self.assertTrue(hasattr(conf, 'id'))

    def test_data_is_mandatory(self):
        conf = get_valid_configuration_model()
        conf.data = None
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_data_cannot_be_empty(self):
        conf = get_valid_configuration_model()
        conf.data = {}
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_base_code_is_not_mandatory(self):
        conf = get_valid_configuration_model()
        conf.full_clean()  # Should not raise

    def test_base_code_throws_error_if_not_exists(self):
        conf = get_valid_configuration_model()
        conf.base_code = 'foo'
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_base_code_throws_error_if_not_active(self):
        base_conf = get_valid_configuration_model()
        base_conf.save()
        conf = get_valid_configuration_model()
        conf.base_code = 'sample'
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_base_code_is_valid_if_exists_and_active(self):
        base_conf = get_valid_configuration_model()
        base_conf.active = True
        base_conf.save()
        conf = get_valid_configuration_model()
        conf.base_code = 'sample'
        conf.full_clean()  # Should not raise

    def test_name_is_mandatory(self):
        conf = get_valid_configuration_model()
        conf.name = None
        with self.assertRaises(ValidationError):
            conf.full_clean()

    def test_description_is_not_mandatory(self):
        conf = get_valid_configuration_model()
        conf.description = None
        conf.full_clean()  # Should not raise

    def test_created_is_set_on_save(self):
        conf = get_valid_configuration_model()
        self.assertIsNone(conf.created)
        conf.save()
        self.assertIsNotNone(conf.created)

    def test_active_is_set_to_false(self):
        conf = get_valid_configuration_model()
        self.assertFalse(conf.active)

    def test_activated_is_not_set_on_save(self):
        conf = get_valid_configuration_model()
        self.assertIsNone(conf.activated)
        conf.save()
        self.assertIsNone(conf.activated)

    def test_activated_is_set_if_active_is_true(self):
        conf = get_valid_configuration_model()
        conf.active = True
        conf.save()
        self.assertIsNotNone(conf.activated)

    @patch.object(Configuration, 'get_active_by_code')
    def test_clean_calls_get_active_by_code(
            self, mock_Configuration_get_active_by_code):
        conf = get_valid_configuration_model()
        conf.clean()
        mock_Configuration_get_active_by_code.assert_called_once_with('sample')

    def test_get_active_by_code_returns_active(self):
        conf_1 = get_valid_configuration_model()
        conf_1.save()
        conf_2 = get_valid_configuration_model()
        conf_2.active = True
        conf_2.save()
        self.assertEqual(conf_2, Configuration.get_active_by_code('sample'))

    def test_get_active_by_code_returns_None_if_not_found(self):
        conf_1 = get_valid_configuration_model()
        conf_1.save()
        self.assertIsNone(Configuration.get_active_by_code('sample'))


class ConfigurationModelTestFixtures(TestCase):

    fixtures = ['sample.json']

    def test_active_can_only_be_set_once_per_code(self):
        conf_1_ret = Configuration.objects.get(pk=1)
        self.assertTrue(conf_1_ret.active)
        conf_2 = get_valid_configuration_model()
        conf_2.active = True
        conf_2.data = conf_1_ret.data
        conf_2.full_clean()
        conf_1_ret = Configuration.objects.get(pk=1)
        self.assertFalse(conf_1_ret.active)
