from unittest.mock import patch

from qcat.tests import TestCase
from questionnaire.utils import (
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
    get_questiongroup_data_from_translation_form,
    is_empty_questionnaire,
    is_valid_questionnaire_format,
)
from qcat.errors import QuestionnaireFormatError


def get_valid_questionnaire_format():
    return {"foo": [{}]}


def get_valid_questionnaire_content():
    return {
        "qg_1": [{"key_1": {"en": "value_en", "es": "value_es"}}],
        "qg_2": [{"key_2": 1}]
    }


class IsEmptyQuestionnaireTest(TestCase):

    @patch('questionnaire.utils.is_valid_questionnaire_format')
    def test_calls_is_valid_questionnaire_format(
            self, mock_is_valid_questionnaire_format):
        data = get_valid_questionnaire_format()
        is_empty_questionnaire(data)
        mock_is_valid_questionnaire_format.assert_called_once_with(data)

    def test_returns_true_if_empty_1(self):
        empty = {
            "bar": []
        }
        self.assertTrue(is_empty_questionnaire(empty))

    def test_returns_true_if_empty_2(self):
        empty = {
            "foo": [{}]
        }
        self.assertTrue(is_empty_questionnaire(empty))

    def test_returns_true_if_empty_3(self):
        empty = {}
        self.assertTrue(is_empty_questionnaire(empty))

    def test_returns_false_if_not_empty(self):
        not_empty = {
            "foo": [{"foo": "bar"}],
            "bar": [{"bar": "faz"}]
        }
        self.assertFalse(is_empty_questionnaire(not_empty))

    def test_foo(self):
        empty = {
            'qg_1': [{'key_1': '', 'key_3': ''}],
            'qg_2': [{'key_2': ''}],
            'qg_3': [{'key_6': '', 'key_4': ''}]}
        self.assertTrue(is_empty_questionnaire(empty))


class IsValidQuestionnaireFormatTest(TestCase):

    def test_raises_error_if_invalid_format(self):
        with self.assertRaises(QuestionnaireFormatError):
            is_valid_questionnaire_format("foo")

    def test_raises_error_if_invalid_format2(self):
        with self.assertRaises(QuestionnaireFormatError):
            is_valid_questionnaire_format({"foo": "bar"})

    def test_returns_true_if_valid_format(self):
        self.assertTrue(is_valid_questionnaire_format(
            get_valid_questionnaire_format()))


class GetQuestionnaireDataInSingleLanguageTest(TestCase):

    @patch('questionnaire.utils.is_valid_questionnaire_format')
    def test_calls_is_valid_questionnaire_format(
            self, mock_is_valid_questionnaire_format):
        data = get_valid_questionnaire_format()
        get_questionnaire_data_in_single_language(data, locale='en')
        mock_is_valid_questionnaire_format.assert_called_once_with(data)

    def test_returns_single_value_per_key(self):
        data = get_valid_questionnaire_content()
        data_es = get_questionnaire_data_in_single_language(data, locale='es')
        self.assertEqual(len(data), len(data_es))
        self.assertEqual(len(data['qg_1']), len(data_es['qg_1']))
        self.assertEqual(data_es['qg_1'][0]['key_1'], 'value_es')

    def test_sets_None_if_locale_not_found(self):
        data = get_valid_questionnaire_content()
        data_foo = get_questionnaire_data_in_single_language(
            data, locale='foo')
        self.assertIsNone(data_foo['qg_1'][0]['key_1'])

    def test_also_returns_non_translated_values(self):
        data = get_valid_questionnaire_content()
        data_es = get_questionnaire_data_in_single_language(data, locale='es')
        self.assertEqual(data_es['qg_2'][0]['key_2'], 1)


class GetQuestionnaireDataForTranslationFormTest(TestCase):

    @patch('questionnaire.utils.is_valid_questionnaire_format')
    def test_calls_is_valid_questionnaire_format(
            self, mock_is_valid_questionnaire_format):
        data = get_valid_questionnaire_format()
        get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        mock_is_valid_questionnaire_format.assert_called_once_with(data)

    def test_adds_translation_fields(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        self.assertEqual(len(data), len(data_trans))
        self.assertEqual(len(data['qg_1']), len(data_trans['qg_1']))
        self.assertEqual(
            data_trans['qg_1'][0]['old_key_1'], data['qg_1'][0]['key_1'])
        self.assertEqual(
            data_trans['qg_1'][0]['original_key_1'],
            data['qg_1'][0]['key_1']['en'])
        self.assertEqual(
            data_trans['qg_1'][0]['translation_key_1'],
            data['qg_1'][0]['key_1']['es'])

    def test_uses_current_locale_if_original_is_None(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale=None)
        self.assertEqual(
            data_trans['qg_1'][0]['original_key_1'],
            data['qg_1'][0]['key_1']['es'])
        self.assertEqual(
            data_trans['qg_1'][0]['translation_key_1'],
            data['qg_1'][0]['key_1']['es'])

    def test_also_returns_non_translated_values(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        self.assertEqual(data_trans['qg_2'][0]['key_2'], 1)


class GetQuestiongroupDataFromTranslationFormTest(TestCase):

    def test_uses_current_locale_if_original_is_None(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale=None)
        qg_1_cleaned = get_questiongroup_data_from_translation_form(
            data_trans['qg_1'][0], 'es', None)
        self.assertEqual(qg_1_cleaned, data['qg_1'][0])

    def test_cleans_translation_fields(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        qg_1_cleaned = get_questiongroup_data_from_translation_form(
            data_trans['qg_1'][0], 'es', 'en')
        self.assertEqual(qg_1_cleaned, data['qg_1'][0])

    def test_returns_non_translated_values(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        qg_2_cleaned = get_questiongroup_data_from_translation_form(
            data_trans['qg_2'][0], 'es', 'en')
        self.assertEqual(qg_2_cleaned, data['qg_2'][0])
