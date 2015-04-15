from django.core.exceptions import ValidationError
from unittest.mock import patch

from configuration.models import (
    Category,
    Configuration,
    Key,
    Questiongroup,
    Translation,
    Value,
)
from qcat.tests import TestCase


def get_valid_configuration_model():
    return Configuration(
        code='sample', name='name', data={"sections": []})


def get_valid_translation_model():
    return Translation(translation_type='key', data={
        "configuration": {"keyword": {"locale": "foo"}}})


def get_valid_questiongroup_model():
    return Questiongroup(keyword='foo', configuration={})


def get_valid_key_model():
    translation = get_valid_translation_model()
    translation.save()
    return Key(
        keyword='foo', translation=translation, configuration={"foo": "bar"})


def get_valid_value_model():
    translation = get_valid_translation_model()
    translation.translation_type = 'value'
    translation.save()
    # key = get_valid_key_model()
    # key.save()
    return Value(
        keyword='foo', translation=translation,
        configuration={"foo": "bar"})


def get_valid_category_model():
    translation = get_valid_translation_model()
    translation.translation_type = 'category'
    translation.save()
    return Category(keyword='foo', translation=translation)


class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = get_valid_category_model()

    def test_get_valid_category_model_is_valid(self):
        self.category.full_clean()  # Should not raise

    def test_id_is_primary_key(self):
        self.assertTrue(hasattr(self.category, 'id'))

    def test_keyword_is_mandatory(self):
        self.category.keyword = None
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    def test_translation_is_mandatory(self):
        with self.assertRaises(ValueError):
            self.category.translation = None

    def test_translation_needs_correct_type(self):
        translation = get_valid_translation_model()
        translation.translation_type = 'foo'
        translation.save()
        self.category.translation = translation
        with self.assertRaises(ValidationError):
            self.category.full_clean()

    @patch.object(Translation, 'get_translation')
    def test_get_translation_calls_translation_function(
            self, mock_Translation_get_translation):
        self.category.get_translation(
            'keyword', configuration='foo', locale='bar')
        mock_Translation_get_translation.assert_called_once_with(
            'keyword', configuration='foo', locale='bar')


class QuestiongroupModelTest(TestCase):

    def setUp(self):
        self.questiongroup = get_valid_questiongroup_model()

    def test_get_valid_questiongroup_model_is_valid(self):
        self.questiongroup.full_clean()  # Should not raise

    def test_id_is_primary_key(self):
        self.assertTrue(hasattr(self.questiongroup, 'id'))

    def test_keyword_is_mandatory(self):
        self.questiongroup.keyword = None
        with self.assertRaises(ValidationError):
            self.questiongroup.full_clean()

    def test_keyword_is_unique(self):
        self.questiongroup.save()
        q2 = get_valid_questiongroup_model()
        with self.assertRaises(ValidationError):
            q2.full_clean()

    def test_translation_is_not_mandatory(self):
        self.questiongroup.translation = None
        self.questiongroup.full_clean()  # Should not raise

    def test_configuration_is_not_mandatory(self):
        self.questiongroup.configuration = {}
        self.questiongroup.full_clean()  # Should not raise


class KeyModelTest(TestCase):

    def setUp(self):
        self.key = get_valid_key_model()

    def test_get_valid_key_model_is_valid(self):
        self.key.full_clean()  # Should not raise

    def test_id_is_primary_key(self):
        self.assertTrue(hasattr(self.key, 'id'))

    def test_keyword_is_mandatory(self):
        self.key.keyword = None
        with self.assertRaises(ValidationError):
            self.key.full_clean()

    def test_translation_is_mandatory(self):
        with self.assertRaises(ValueError):
            self.key.translation = None

    def test_translation_needs_correct_type(self):
        translation = get_valid_translation_model()
        translation.translation_type = 'foo'
        translation.save()
        self.key.translation = translation
        with self.assertRaises(ValidationError):
            self.key.full_clean()

    def test_configuration_is_mandatory(self):
        self.key.configuration = None
        with self.assertRaises(ValidationError):
            self.key.full_clean()

    def test_configuration_cannot_be_empty(self):
        self.key.configuration = {}
        with self.assertRaises(ValidationError):
            self.key.full_clean()

    @patch.object(Translation, 'get_translation')
    def test_get_translation_calls_translation_function(
            self, mock_Translation_get_translation):
        self.key.get_translation('keyword', configuration='foo', locale='bar')
        mock_Translation_get_translation.assert_called_once_with(
            'keyword', configuration='foo', locale='bar')

    def test_type_returns_type(self):
        self.key.configuration = {"type": "foo"}
        self.assertEqual(self.key.type_, 'foo')

    def test_type_returns_None_if_not_found(self):
        self.assertIsNone(self.key.type_)

    def test_can_have_one_value(self):
        self.key.save()
        self.assertEqual(self.key.values.count(), 0)
        value = get_valid_value_model()
        value.save()
        self.key.values.add(value)
        self.assertEqual(self.key.values.count(), 1)

    def test_can_have_multiple_values(self):
        self.key.save()
        value_1 = get_valid_value_model()
        value_1.save()
        self.key.values.add(value_1)
        value_2 = get_valid_value_model()
        value_2.keyword = 'bar'
        value_2.save()
        self.key.values.add(value_2)
        self.assertEqual(self.key.values.count(), 2)


class ValueModelTest(TestCase):

    def setUp(self):
        self.value = get_valid_value_model()

    def test_get_valid_value_model_is_valid(self):
        self.value.full_clean()  # Should not raise

    def test_id_is_primary_key(self):
        self.assertTrue(hasattr(self.value, 'id'))

    def test_keyword_is_mandatory(self):
        self.value.keyword = None
        with self.assertRaises(ValidationError):
            self.value.full_clean()

    def test_translation_is_mandatory(self):
        with self.assertRaises(ValueError):
            self.value.translation = None

    def test_translation_needs_correct_type(self):
        translation = get_valid_translation_model()
        translation.translation_type = 'foo'
        translation.save()
        self.value.translation = translation
        with self.assertRaises(ValidationError):
            self.value.full_clean()

    def test_configuration_is_not_mandatory(self):
        self.value.configuration = None
        self.value.full_clean()  # Should not raise

    def test_configuration_can_be_empty(self):
        self.value.configuration = {}
        self.value.full_clean()  # Should not raise

    @patch.object(Translation, 'get_translation')
    def test_get_translation_calls_translation_function(
            self, mock_Translation_get_translation):
        self.value.get_translation(
            'keyword', configuration='foo', locale='bar')
        mock_Translation_get_translation.assert_called_once_with(
            'keyword', configuration='foo', locale='bar')

    def test_can_have_one_key(self):
        self.value.save()
        self.assertEqual(self.value.key_set.count(), 0)
        key = get_valid_key_model()
        key.save()
        self.value.key_set.add(key)
        self.assertEqual(self.value.key_set.count(), 1)

    def test_can_have_multiple_keys(self):
        self.value.save()
        key_1 = get_valid_key_model()
        key_1.save()
        self.value.key_set.add(key_1)
        key_2 = get_valid_key_model()
        key_2.keyword = 'bar'
        key_2.save()
        self.value.key_set.add(key_2)
        self.assertEqual(self.value.key_set.count(), 2)


class TranslationModelTest(TestCase):

    def setUp(self):
        self.translation = get_valid_translation_model()

    def test_get_valid_translation_model_is_valid(self):
        self.translation.full_clean()  # Should not raise

    def test_id_is_primary_key(self):
        self.assertTrue(hasattr(self.translation, 'id'))

    def test_translation_type_is_mandatory(self):
        self.translation.translation_type = None
        with self.assertRaises(ValidationError):
            self.translation.full_clean()

    def test_translation_type_needs_to_be_valid(self):
        self.translation.translation_type = 'foo'
        with self.assertRaises(ValidationError):
            self.translation.full_clean()

    def test_data_is_mandatory(self):
        self.translation.data = None
        with self.assertRaises(ValidationError):
            self.translation.full_clean()

    def test_data_cannot_be_empty(self):
        self.translation.data = {}
        with self.assertRaises(ValidationError):
            self.translation.full_clean()

    def test_get_translation_types_returns_list(self):
        self.assertIsInstance(self.translation.get_translation_types(), list)

    def test_get_translation_types_returns_valid_types(self):
        valid_types = self.translation.get_translation_types()
        self.assertEqual(len(valid_types), 4)

    @patch('configuration.models.to_locale')
    @patch('configuration.models.get_language')
    def test_get_translation_calls_get_language_if_no_locale_provided(
            self, mock_get_language, mock_to_locale):
        mock_to_locale.return_value = ''
        self.translation.get_translation('keyword')
        mock_get_language.assert_called_once_with()

    @patch('configuration.models.get_language')
    def test_get_translation_does_not_call_get_language_if_locale_provided(
            self, mock_get_language):
        self.translation.get_translation('keyword', locale='locale')
        mock_get_language.assert_not_called()

    def test_get_translation_returns_data_by_configuration_and_locale(self):
        self.assertEqual(self.translation.get_translation(
            'keyword', configuration='configuration', locale='locale'), 'foo')

    def test_get_translation_uses_wocat_configuration_if_not_provided(self):
        self.translation.data = {"wocat": {"keyword": {"locale": "foo"}}}
        self.assertEqual(
            self.translation.get_translation('keyword', locale='locale'),
            'foo')

    def test_get_translation_returns_None_if_locale_not_found(self):
        self.assertIsNone(self.translation.get_translation(
            'keyword', locale='foo'))

    def test_get_translation_returns_None_if_configuration_not_found(self):
        self.assertIsNone(self.translation.get_translation(
            'keyword', configuration='foo'))


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

    def test_active_can_only_be_set_once_per_code(self):
        conf_1_ret = get_valid_configuration_model()
        conf_1_ret.active = True
        conf_1_ret.name = 'conf_1'
        conf_1_ret.save()
        self.assertTrue(conf_1_ret.active)
        conf_2 = get_valid_configuration_model()
        conf_2.active = True
        conf_2.data = conf_1_ret.data
        conf_2.full_clean()
        conf_1_ret = Configuration.objects.get(name='conf_1')
        self.assertFalse(conf_1_ret.active)
        conf_2.save()
        active = Configuration.objects.filter(active=True).all()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0], conf_2)
