from unittest.mock import patch

from qcat.tests import TestCase
from questionnaire.utils import (
    is_empty_questionnaire,
    is_valid_questionnaire_format,
)
from qcat.errors import QuestionnaireFormatError


def get_valid_questionnaire_format():
    return {"foo": [{}]}


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
