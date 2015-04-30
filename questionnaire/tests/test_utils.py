from unittest.mock import patch
from django.http import QueryDict

from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from questionnaire.utils import (
    clean_questionnaire_data,
    get_active_filters,
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
    get_questiongroup_data_from_translation_form,
    is_valid_questionnaire_format,
)
from qcat.errors import QuestionnaireFormatError


def get_valid_questionnaire_format():
    return {"foo": [{}]}


def get_valid_questionnaire_content():
    return {
        "qg_1": [{"key_1": {"en": "value_en", "es": "value_es"}}],
        "qg_3": [{"key_11": True}]
    }


class CleanQuestionnaireDataTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.conf = QuestionnaireConfiguration('sample')

    @patch('questionnaire.utils.is_valid_questionnaire_format')
    def test_calls_is_valid_questionnaire_format(
            self, mock_is_valid_questionnaire_format):
        data = get_valid_questionnaire_format()
        clean_questionnaire_data(data, QuestionnaireConfiguration('sample'))
        mock_is_valid_questionnaire_format.assert_called_once_with(data)

    def test_returns_error_list_if_invalid_questionnaire_format(self):
        data = 'foo'
        cleaned, errors = clean_questionnaire_data(data, None)
        self.assertEqual(len(errors), 1)

    def test_adds_error_if_questiongroup_by_keyword_not_found(self):
        data = {
            "foo": [{"key_12": "1"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_adds_error_if_key_not_valid_in_questiongroup(self):
        data = {
            "qg_9": [{"foo": "1"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_parses_measure_values_to_int(self):
        conf = QuestionnaireConfiguration('sample')
        data = {
            "qg_9": [{"key_12": "1"}]
        }
        cleaned, errors = clean_questionnaire_data(data, conf)
        self.assertEqual(cleaned, {"qg_9": [{"key_12": 1}]})
        self.assertEqual(len(errors), 0)

    def test_raises_error_if_measure_values_no_int(self):
        data = {
            "qg_9": [{"key_12": "foo"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_raises_error_if_measure_value_not_in_range(self):
        data = {
            "qg_9": [{"key_12": "0"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_clears_empty_questiongroups(self):
        data = get_valid_questionnaire_content()
        data['qg_9'] = []
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, get_valid_questionnaire_content())
        self.assertEqual(len(errors), 0)

    def test_clears_empty_questions(self):
        data = get_valid_questionnaire_content()
        data['qg_9'] = [{}]
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, get_valid_questionnaire_content())
        self.assertEqual(len(errors), 0)

    def test_clears_empty_values(self):
        data = get_valid_questionnaire_content()
        data['qg_9'] = [{"key_12": ""}]
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, get_valid_questionnaire_content())
        self.assertEqual(len(errors), 0)

    def test_string_values_need_to_be_dicts(self):
        data = {
            "qg_1": [{"key_1": "foo"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_list_values_need_to_be_lists(self):
        data = {
            "qg_10": [{"key_13": "value_13_1"}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_list_values_are_checked_correctly(self):
        data = {
            "qg_10": [{"key_13": ["value_13_1", "value_13_2"]}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_list_values_need_to_match_choices(self):
        data = {
            "qg_10": [{"key_13": ["value_13_1", "foo"]}]
        }
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_passes_if_conditional_question_correct(self):
        data = {
            "qg_12": [{"key_15": ["value_15_1"], "key_16": ["value_16_1"]}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_raises_error_if_conditional_question_not_correct(self):
        data = {
            "qg_12": [{"key_15": ["value_15_2"], "key_16": ["value_16_1"]}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_passes_image_data_as_such(self):
        data = {"qg_14": [{"key_19": "61b51f3c-a3e2-43b7-87eb-42840bda7250"}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 0)
        self.assertEqual(cleaned, data)

    def test_passes_if_conditional_questiongroup_correct(self):
        data = {'qg_17': [{'key_23': {'en': 'Bar'}}], 'qg_16': [{'key_21': 2}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_raises_error_if_conditional_questiongroup_not_correct(self):
        data = {'qg_17': [{'key_23': {'en': 'Bar'}}], 'qg_16': [{'key_21': 1}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_passes_if_conditional_questiongroup_without_data(self):
        data = {'qg_17': [{'key_23': {'en': ''}, 'key_22': []}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, {})
        self.assertEqual(len(errors), 0)

    def test_passes_with_conditional_checkbox_questiongroup(self):
        data = {
            'qg_10': [{'key_13': ['value_13_5']}],
            'qg_18': [{'key_24': {'en': 'Bar'}}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_passes_with_conditional_multiple_checkbox_questiongroup(self):
        data = {
            'qg_10': [{'key_13': ['value_13_5', 'value_13_4']}],
            'qg_18': [{'key_24': {'en': 'Bar'}}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_fails_with_conditional_checkbox_questiongroup(self):
        data = {
            'qg_10': [{'key_13': ['value_13_4']}],
            'qg_18': [{'key_24': {'en': 'Bar'}}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_fails_if_text_length_exceeds_max_length(self):
        data = {'qg_2': [{
            'key_2':
            {'en': 'The limit is 50 chars but this text contains 55 chars.'},
            'key_3': {'en': ''}}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_passes_if_text_length_below_max_length(self):
        data = {'qg_2': [{'key_2': {'en': 'This is short enough.'}}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_passes_with_boolean_True_as_integer(self):
        data = {'qg_3': [{'key_11': 1}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_passes_with_boolean_False_as_integer(self):
        data = {'qg_3': [{'key_11': 0}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_fails_with_boolean_impossible_value_as_integer(self):
        data = {'qg_3': [{'key_11': 99}]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)

    def test_passes_if_num_lower_than_max_num_of_questiongroups(self):
        data = {'qg_6': [
            {'key_8': {'en': 'Key 8 - 1'}},
            {'key_8': {'en': 'Key 8 - 2'}},
            {'key_8': {'en': 'Key 8 - 3'}}
        ]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(cleaned, data)
        self.assertEqual(len(errors), 0)

    def test_raises_error_if_num_higher_than_max_num_of_questiongroups(self):
        data = {'qg_6': [
            {'key_8': {'en': 'Key 8 - 1'}},
            {'key_8': {'en': 'Key 8 - 2'}},
            {'key_8': {'en': 'Key 8 - 3'}},
            {'key_8': {'en': 'Key 8 - 4'}}
        ]}
        cleaned, errors = clean_questionnaire_data(data, self.conf)
        self.assertEqual(len(errors), 1)


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
        self.assertEqual(data_es['qg_3'][0]['key_11'], True)


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
        self.assertEqual(data_trans['qg_3'][0]['key_11'], True)


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

    def test_handles_keys_with_keyword_in_them(self):
        data = {
            "qg_1": [{"wocat_original_landuse": {
                "en": "value_en", "es": "value_es"}}],
        }
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        qg_1_cleaned = get_questiongroup_data_from_translation_form(
            data_trans['qg_1'][0], 'es', 'en')
        self.assertEqual(qg_1_cleaned, data['qg_1'][0])

    def test_returns_non_translated_values(self):
        data = get_valid_questionnaire_content()
        data_trans = get_questionnaire_data_for_translation_form(
            data, current_locale='es', original_locale='en')
        qg_3_cleaned = get_questiongroup_data_from_translation_form(
            data_trans['qg_3'][0], 'es', 'en')
        self.assertEqual(qg_3_cleaned, data['qg_3'][0])


class GetActiveFiltersTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.conf = QuestionnaireConfiguration('sample')

    def test_returns_empty_if_empty_query_dict(self):
        query_dict = QueryDict('')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(filters, [])

    def test_returns_empty_if_no_filter(self):
        query_dict = QueryDict('a=1&b=2')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(filters, [])

    def test_skips_invalid_filters(self):
        query_dict = QueryDict('filter__foo=1&filter__foo__bar__faz=2')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(filters, [])

    def test_skips_filter_with_unknown_questiongroup_or_key(self):
        query_dict = QueryDict(
            'filter__qg_1__unknown_key=1&filter__inv_qg__key_1=2')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(filters, [])

    def test_returns_single_query_dict(self):
        query_dict = QueryDict(
            'filter__qg_11__key_14=value_14_1')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(len(filters), 1)
        filter_1 = filters[0]
        self.assertIsInstance(filter_1, dict)
        self.assertEqual(len(filter_1), 6)
        self.assertEqual(filter_1['questiongroup'], 'qg_11')
        self.assertEqual(filter_1['key'], 'key_14')
        self.assertEqual(filter_1['key_label'], 'Key 14')
        self.assertEqual(filter_1['value'], 'value_14_1')
        self.assertEqual(filter_1['value_label'], 'Value 14_1')
        self.assertEqual(filter_1['type'], 'image_checkbox')

    def test_returns_multiple_filters(self):
        query_dict = QueryDict(
            'filter__qg_11__key_14=value_14_1&filter__qg_19__key_5=Faz')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(len(filters), 2)
        filter_1 = filters[0]
        self.assertIsInstance(filter_1, dict)
        self.assertEqual(len(filter_1), 6)
        self.assertEqual(filter_1['key_label'], 'Key 14')
        self.assertEqual(filter_1['value_label'], 'Value 14_1')
        filter_2 = filters[1]
        self.assertIsInstance(filter_2, dict)
        self.assertEqual(len(filter_2), 6)
        self.assertEqual(filter_2['key_label'], 'Key 5')
        self.assertEqual(filter_2['value_label'], 'Faz')

    def test_returns_duplicate_filter_keys(self):
        query_dict = QueryDict(
            'filter__qg_11__key_14=value_14_1&filter__qg_11__key_14='
            'value_14_2')
        filters = get_active_filters(self.conf, query_dict)
        self.assertEqual(len(filters), 2)
        filter_1 = filters[0]
        self.assertIsInstance(filter_1, dict)
        self.assertEqual(len(filter_1), 6)
        self.assertEqual(filter_1['key_label'], 'Key 14')
        self.assertEqual(filter_1['value_label'], 'Value 14_1')
        filter_2 = filters[1]
        self.assertIsInstance(filter_2, dict)
        self.assertEqual(len(filter_2), 6)
        self.assertEqual(filter_2['key_label'], 'Key 14')
        self.assertEqual(filter_2['value_label'], 'Value 14_2')
