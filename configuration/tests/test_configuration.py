from unittest.mock import patch

from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
    QuestionnaireSubcategory,
    QuestionnaireQuestiongroup,
    QuestionnaireQuestion,
)
from configuration.tests.test_models import get_valid_configuration_model
from qcat.errors import (
    ConfigurationErrorInvalidConfiguration,
    ConfigurationErrorInvalidOption,
    ConfigurationErrorNoConfigurationFound,
    ConfigurationErrorNotInDatabase,
)
from qcat.tests import TestCase


def get_valid_questionnaire_configuration():
    return QuestionnaireConfiguration('foo')


class QuestionnaireConfigurationTest(TestCase):

    @patch.object(QuestionnaireConfiguration, 'read_configuration')
    def test_QuestionnaireConfiguration_init_calls_read_configuration(
            self, mock_QuestionnaireConfiguration_read_configuration):
        get_valid_questionnaire_configuration()
        mock_QuestionnaireConfiguration_read_configuration.\
            assert_called_once_with()


class QuestionnaireConfigurationReadConfigurationTest(TestCase):

    def test_raises_error_if_no_configuration_object(self):
        conf = get_valid_questionnaire_configuration()
        with self.assertRaises(ConfigurationErrorNoConfigurationFound):
            conf.read_configuration()

    def test_raises_error_if_invalid_options(self):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf_object.data = {"foo": "bar"}
        conf.configuration_object = conf_object
        with self.assertRaises(ConfigurationErrorInvalidOption):
            conf.read_configuration()

    def test_raises_error_if_no_categories(self):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf_object.data = {}
        conf.configuration_object = conf_object
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            conf.read_configuration()

    def test_raises_error_if_categories_not_list(self):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf_object.data = {"categories": "foo"}
        conf.configuration_object = conf_object
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            conf.read_configuration()


class QuestionnaireCategoryTest(TestCase):

    fixtures = ['sample.json']

    def test_raises_error_if_configuration_not_dict(self):
        configuration = "foo"
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_invalid_option(self):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_keyword_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_keyword_not_string(self):
        configuration = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_not_in_db(self):
        configuration = {
            "keyword": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_no_subcategories(self):
        configuration = {
            "keyword": "cat_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(configuration)

    def test_raises_error_if_subcategories_not_list(self):
        configuration = {
            "keyword": "cat_1",
            "subcategories": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(configuration)


class QuestionnaireSubcategoryTest(TestCase):

    fixtures = ['sample.json']

    def test_raises_error_if_configuration_not_dicts(self):
        configuration = "foo"
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_invalid_option(self):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_keyword_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_keyword_not_string(self):
        configuration = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_not_in_db(self):
        configuration = {
            "keyword": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_no_questiongroups(self):
        configuration = {
            "keyword": "subcat_1_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(configuration)

    def test_raises_error_if_questiongroups_not_list(self):
        configuration = {
            "keyword": "subcat_1_1",
            "questiongroups": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(configuration)


class QuestionnaireQuestiongroupTest(TestCase):

    fixtures = ['sample.json']

    def test_raises_error_if_configuration_not_dicts(self):
        configuration = "foo"
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_invalid_option(self):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_keyword_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_keyword_not_string(self):
        configuration = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_no_questions(self):
        configuration = {
            "keyword": "qg_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_questions_not_list(self):
        configuration = {
            "keyword": "qg_1",
            "questions": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(configuration)


class QuestionnaireQuestionTest(TestCase):

    fixtures = ['sample.json']

    def test_raises_error_if_configuration_not_dicts(self):
        configuration = "foo"
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(configuration)

    def test_raises_error_if_invalid_option(self):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireQuestion(configuration)

    def test_raises_error_if_key_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(configuration)

    def test_raises_error_if_key_not_string(self):
        configuration = {
            "key": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(configuration)

    def test_raises_error_if_not_in_db(self):
        configuration = {
            "key": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireQuestion(configuration)
