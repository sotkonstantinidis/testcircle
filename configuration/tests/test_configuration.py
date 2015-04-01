from unittest.mock import patch, Mock

from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
    QuestionnaireSubcategory,
    QuestionnaireQuestiongroup,
    QuestionnaireQuestion,
    validate_options,
    validate_type,
)
from configuration.tests.test_models import get_valid_configuration_model
from qcat.errors import (
    ConfigurationErrorInvalidCondition,
    ConfigurationErrorInvalidConfiguration,
    ConfigurationErrorInvalidOption,
    ConfigurationErrorInvalidQuestiongroupCondition,
    ConfigurationErrorNoConfigurationFound,
    ConfigurationErrorNotInDatabase,
    ConfigurationErrorTemplateNotFound,
)
from qcat.tests import TestCase
from questionnaire.models import Questionnaire
from sample.tests.test_views import get_list_data as get_sample_list_data

route_questionnaire_details = 'sample:questionnaire_details'


def get_valid_questionnaire_configuration():
    return QuestionnaireConfiguration('foo')


class QuestionnaireConfigurationTest(TestCase):

    @patch.object(QuestionnaireConfiguration, 'read_configuration')
    def test_QuestionnaireConfiguration_init_calls_read_configuration(
            self, mock_QuestionnaireConfiguration_read_configuration):
        get_valid_questionnaire_configuration()
        mock_QuestionnaireConfiguration_read_configuration.\
            assert_called_once_with()


class QuestionnaireConfigurationGetListDataTest(TestCase):

    fixtures = ['sample.json', 'sample_questionnaires.json']

    def test_returns_list(self):
        questionnaires = Questionnaire.objects.all()
        conf = get_valid_questionnaire_configuration()
        list_data = conf.get_list_data(questionnaires)
        expected = []
        for i in [1, 2]:
            d = get_sample_list_data()
            d.update({'id': i, 'native_configuration': False})
            expected.append(d)
        self.assertEqual(list_data, expected)


class QuestionnaireConfigurationReadConfigurationTest(TestCase):

    def test_raises_error_if_no_configuration_object(self):
        conf = get_valid_questionnaire_configuration()
        with self.assertRaises(ConfigurationErrorNoConfigurationFound):
            conf.read_configuration()

    @patch.object(QuestionnaireConfiguration, 'merge_configurations')
    def test_calls_merge_configurations(
            self, mock_Configuration_merge_configurations):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf.configuration_object = conf_object
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            conf.read_configuration()
        mock_Configuration_merge_configurations.assert_called_once_with(
            {}, conf_object.data)

    @patch('configuration.configuration.validate_options')
    @patch.object(QuestionnaireConfiguration, 'merge_configurations')
    def test_calls_validate_options(
            self, mock_Configuration_merge_configurations,
            mock_validate_options):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf.configuration_object = conf_object
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            conf.read_configuration()
        mock_validate_options.assert_called_once_with(
            mock_Configuration_merge_configurations.return_value,
            ['categories'], QuestionnaireConfiguration)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireConfiguration, 'merge_configurations')
    def test_calls_validate_type(
            self, mock_Configuration_merge_configurations,
            mock_validate_type):
        conf = get_valid_questionnaire_configuration()
        conf_object = get_valid_configuration_model()
        conf.configuration_object = conf_object
        # with self.assertRaises(ConfigurationErrorInvalidConfiguration):
        conf.read_configuration()
        mock_validate_type.assert_called_once_with(
            mock_Configuration_merge_configurations.return_value.get(
                'categories'),
            list, 'categories', 'list of dicts', '-')


class QuestionnaireConfigurationMergeConfigurationsTest(TestCase):

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireConfiguration.merge_configurations({}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireCategory, 'merge_configurations')
    def test_calls_validate_type_base_categories(
            self, mock_Category_merge_configurations, mock_validate_type):
        QuestionnaireConfiguration.merge_configurations(
            {"categories": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"categories": [{}]}
        ret = QuestionnaireConfiguration.merge_configurations(base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"categories": [{"foo": "bar"}]}
        ret = QuestionnaireConfiguration.merge_configurations(base, {})
        self.assertEqual(ret, base)

    @patch.object(QuestionnaireCategory, 'merge_configurations')
    def test_calls_category_merge_configurations(
            self, mock_Category_merge_configurations):
        base = {"categories": [{"foo": "bar"}]}
        QuestionnaireConfiguration.merge_configurations(base, {})
        mock_Category_merge_configurations.assert_called_once_with(
            {"foo": "bar"}, {})

    # @patch.object(QuestionnaireCategory, 'merge_configurations')
    def test_merges_with_base_empty(self):
        base = {}
        specific = {
            "categories": [
                {
                    "keyword": "unccd_cat_1",
                    "subcategories": [
                        {
                            "keyword": "unccd_subcat_1_1",
                            "questiongroups": [
                                {
                                    "questions": [
                                        {
                                            "key": "unccd_key_1",
                                            "list_position": 1
                                        }
                                    ],
                                    "keyword": "unccd_qg_1"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        conf = QuestionnaireConfiguration.merge_configurations(base, specific)
        self.assertIn('categories', conf)
        self.assertNotIn('subcategories', conf)
        self.assertNotIn('questions', conf)
        self.assertNotIn('questiongroups', conf)
        self.assertEqual(len(conf['categories']), 1)
        category = conf['categories'][0]
        self.assertIn('subcategories', category)
        self.assertNotIn('questions', category)
        self.assertNotIn('questiongroups', category)
        self.assertIn('keyword', category)
        self.assertEqual(len(category['subcategories']), 1)
        subcategory = category['subcategories'][0]
        self.assertIn('questiongroups', subcategory)
        self.assertNotIn('questions', subcategory)
        self.assertIn('keyword', subcategory)
        questiongroups = subcategory['questiongroups']
        self.assertEqual(len(questiongroups), 1)
        self.assertIn('questions', questiongroups[0])
        questions = questiongroups[0]['questions']
        self.assertEqual(len(questions), 1)

    def test_appends_specific(self):
        base = {"categories": [{"keyword": "foo", "subcategories": []}]}
        specific = {"categories": [{"keyword": "bar", "subcategories": []}]}
        conf = QuestionnaireConfiguration.merge_configurations(base, specific)
        self.assertEqual(len(conf['categories']), 2)
        for cat in conf['categories']:
            self.assertIn(cat['keyword'], ['foo', 'bar'])


class QuestionnaireCategoryTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.configuration = 'sample'

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireCategory(self.configuration, configuration_dict)
        mock_validate_type.assert_called_once_with(
            configuration_dict, dict, 'categories', 'list of dicts', '-')

    @patch('configuration.configuration.validate_options')
    def test_calls_validate_options(self, mock_validate_options):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)
        mock_validate_options.assert_called_once_with(
            configuration_dict, QuestionnaireCategory.valid_options,
            QuestionnaireCategory)

    def test_raises_error_if_keyword_not_found(self):
        configuration_dict = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)

    def test_raises_error_if_keyword_not_string(self):
        configuration_dict = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)

    def test_raises_error_if_not_in_db(self):
        configuration_dict = {
            "keyword": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireCategory(self.configuration, configuration_dict)

    def test_raises_error_if_no_subcategories(self):
        configuration_dict = {
            "keyword": "cat_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)

    def test_raises_error_if_subcategories_not_list(self):
        configuration_dict = {
            "keyword": "cat_1",
            "subcategories": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)


class QuestionnaireCategoryMergeConfigurationsTest(TestCase):

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireCategory.merge_configurations({}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireSubcategory, 'merge_configurations')
    def test_calls_validate_type_base_categories(
            self, mock_Category_merge_configurations, mock_validate_type):
        QuestionnaireCategory.merge_configurations(
            {"subcategories": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"subcategories": [{}]}
        ret = QuestionnaireCategory.merge_configurations(base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"subcategories": [{"foo": "bar"}]}
        ret = QuestionnaireCategory.merge_configurations(base, {})
        self.assertEqual(ret, base)

    @patch.object(QuestionnaireSubcategory, 'merge_configurations')
    def test_calls_category_merge_configurations(
            self, mock_Category_merge_configurations):
        base = {"subcategories": [{"foo": "bar"}]}
        QuestionnaireCategory.merge_configurations(base, {})
        mock_Category_merge_configurations.assert_called_once_with(
            {"foo": "bar"}, {})

    def test_appends_specific(self):
        base = {"subcategories": [{"keyword": "foo", "questiongroups": []}]}
        specific = {
            "subcategories": [{"keyword": "bar", "questiongroups": []}]}
        conf = QuestionnaireCategory.merge_configurations(base, specific)
        self.assertEqual(len(conf['subcategories']), 2)
        for cat in conf['subcategories']:
            self.assertIn(cat['keyword'], ['foo', 'bar'])


class QuestionnaireSubcategoryTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.category = None

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireSubcategory(self.category, configuration_dict)
        mock_validate_type.assert_called_once_with(
            configuration_dict, dict, 'subcategories', 'list of dicts',
            'categories')

    @patch('configuration.configuration.validate_options')
    def test_calls_validate_options(self, mock_validate_options):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)
        mock_validate_options.assert_called_once_with(
            configuration_dict, QuestionnaireSubcategory.valid_options,
            QuestionnaireSubcategory)

    def test_raises_error_if_keyword_not_found(self):
        configuration_dict = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)

    def test_raises_error_if_keyword_not_string(self):
        configuration_dict = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)

    def test_raises_error_if_not_in_db(self):
        configuration_dict = {
            "keyword": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireSubcategory(self.category, configuration_dict)

    def test_raises_error_if_no_questiongroups(self):
        configuration_dict = {
            "keyword": "subcat_1_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)

    def test_raises_error_if_questiongroups_not_list(self):
        configuration_dict = {
            "keyword": "subcat_1_1",
            "questiongroups": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)


class QuestionnaireSubcategoryMergeConfigurationsTest(TestCase):

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireSubcategory.merge_configurations({}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireQuestiongroup, 'merge_configurations')
    def test_calls_validate_type_base_categories(
            self, mock_Category_merge_configurations, mock_validate_type):
        QuestionnaireSubcategory.merge_configurations(
            {"questiongroups": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"questiongroups": [{}]}
        ret = QuestionnaireSubcategory.merge_configurations(base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"questiongroups": [{"foo": "bar"}]}
        ret = QuestionnaireSubcategory.merge_configurations(base, {})
        self.assertEqual(ret, base)

    @patch.object(QuestionnaireQuestiongroup, 'merge_configurations')
    def test_calls_category_merge_configurations(
            self, mock_Category_merge_configurations):
        base = {"questiongroups": [{"foo": "bar"}]}
        QuestionnaireSubcategory.merge_configurations(base, {})
        mock_Category_merge_configurations.assert_called_once_with(
            {"foo": "bar"}, {})

    def test_appends_specific(self):
        base = {"questiongroups": [{"keyword": "foo", "questions": []}]}
        specific = {
            "questiongroups": [{"keyword": "bar", "questions": []}]}
        conf = QuestionnaireSubcategory.merge_configurations(base, specific)
        self.assertEqual(len(conf['questiongroups']), 2)
        for cat in conf['questiongroups']:
            self.assertIn(cat['keyword'], ['foo', 'bar'])


class QuestionnaireQuestiongroupTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.subcategory = None

    @patch('configuration.configuration.validate_options')
    def test_calls_validate_options(self, mock_validate_options):
        configuration_dict = {
            "keyword": "qg_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)
        mock_validate_options.assert_called_once_with(
            configuration_dict, QuestionnaireQuestiongroup.valid_options,
            QuestionnaireQuestiongroup)

    def test_raises_error_if_keyword_not_found(self):
        configuration_dict = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_keyword_not_string(self):
        configuration_dict = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_min_num_not_integer(self):
        configuration_dict = {
            "keyword": "qg_1",
            "min_num": "foo",
            "questions": [{"key": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_min_num_smaller_than_1(self):
        configuration_dict = {
            "keyword": "qg_1",
            "min_num": 0,
            "questions": [{"key": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_max_num_not_integer(self):
        configuration_dict = {
            "keyword": "qg_1",
            "max_num": "foo",
            "questions": [{"key": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_max_num_smaller_than_1(self):
        configuration_dict = {
            "keyword": "qg_1",
            "max_num": -1,
            "questions": [{"key": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    # def test_raises_error_if_helptext_not_found(self):
    #     configuration = {
    #         "keyword": "qg_1",
    #         "helptext": -1,
    #         "questions": [{"key": "key_1"}]
    #     }
    #     with self.assertRaises(ConfigurationErrorInvalidOption):
    #         QuestionnaireQuestiongroup(configuration)

    def test_raises_error_if_no_questions(self):
        configuration_dict = {
            "keyword": "qg_1"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_questions_not_list(self):
        configuration_dict = {
            "keyword": "qg_1",
            "questions": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)


class QuestionnaireQuestiongroupMergeConfigurationsTest(TestCase):

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireQuestiongroup.merge_configurations({}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type_base_categories(
            self, mock_validate_type):
        QuestionnaireQuestiongroup.merge_configurations(
            {"questions": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"questions": [{}]}
        ret = QuestionnaireQuestiongroup.merge_configurations(base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"questions": [{"foo": "bar"}]}
        ret = QuestionnaireQuestiongroup.merge_configurations(base, {})
        self.assertEqual(ret, base)

    def test_merge_configurations_merges_questions(self):
        base = {
            "questions": [
                {
                    "key": "bar_1"
                }, {
                    "key": "bar_2"
                }
            ]
        }
        specific = {
            "questions": [
                {
                    "key": "bar_3"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            base, specific)
        self.assertEqual(len(merged.get('questions', [])), 3)

    def test_merge_configurations_merges_question_if_base_empty(self):
        base = {}
        specific = {
            "questions": [
                {
                    "key": "bar_1"
                }, {
                    "key": "bar_2"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            base, specific)
        self.assertEqual(len(merged.get('questions', [])), 2)

    def test_merge_configurations_overwrites_existing_question(self):
        base = {
            "questions": [
                {
                    "key": "foo",
                    "foo": "bar_1"
                }, {
                    "key": "bar"
                }
            ]
        }
        specific = {
            "questions": [
                {
                    "key": "foo",
                    "foo": "bar_2"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            base, specific)
        self.assertEqual(len(merged.get('questions', [])), 2)
        for q in merged.get('questions', []):
            if q.get('key') == 'foo':
                self.assertEqual(q.get('foo'), 'bar_2')


class QuestionnaireQuestionTest(TestCase):

    fixtures = ['sample.json']

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireQuestion(None, configuration)
        mock_validate_type.assert_called_once_with(
            configuration, dict, 'questions', 'list of dicts',
            'questiongroups')

    @patch('configuration.configuration.validate_options')
    def test_calls_validate_options(self, mock_validate_options):
        configuration = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(None, configuration)
        mock_validate_options.assert_called_once_with(
            configuration, QuestionnaireQuestion.valid_options,
            QuestionnaireQuestion)

    def test_raises_error_if_key_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(None, configuration)

    def test_raises_error_if_key_not_string(self):
        configuration = {
            "key": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(None, configuration)

    def test_raises_error_if_not_in_db(self):
        configuration = {
            "key": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireQuestion(None, configuration)

    def test_raises_error_if_form_template_not_found(self):
        configuration = {
            'key': 'key_14',
            'form_template': 'foo'
        }
        with self.assertRaises(ConfigurationErrorTemplateNotFound):
            QuestionnaireQuestion(None, configuration)

    def test_lookup_choices_lookups_single_choice(self):
        mock_Questiongroup = Mock()
        mock_Questiongroup.configuration_keyword = 'sample'
        q = QuestionnaireQuestion(mock_Questiongroup, {'key': 'key_14'})
        l = q.lookup_choices_labels_by_keywords(['value_14_1'])
        self.assertEqual(l, ['Value 14_1'])

    def test_lookup_choices_lookups_many_choices(self):
        mock_Questiongroup = Mock()
        mock_Questiongroup.configuration_keyword = 'sample'
        q = QuestionnaireQuestion(mock_Questiongroup, {'key': 'key_14'})
        l = q.lookup_choices_labels_by_keywords(['value_14_1', 'value_14_2'])
        self.assertEqual(l, ['Value 14_1', 'Value 14_2'])

    def test_lookup_choices_boolean(self):
        q = QuestionnaireQuestion(None, {'key': 'key_14'})
        q.choices = ((True, 'Yes'), (False, 'No'))
        l = q.lookup_choices_labels_by_keywords([True])
        self.assertEqual(l, ['Yes'])

    def test_lookup_choices_integer(self):
        q = QuestionnaireQuestion(None, {'key': 'key_12'})
        q.choices = ((1, 'Low'), (2, 'High'))
        l = q.lookup_choices_labels_by_keywords([1])
        self.assertEqual(l, ['Low'])

    def test_raises_error_if_condition_wrong_formatted(self):
        condition = 'foo'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                None, {'key': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_value_does_not_exist(self):
        condition = 'foo|True|key_16'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                None, {'key': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_condition_expression_nonsense(self):
        condition = 'value_15_1|;:_|key_16'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                None, {'key': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_questiongroup_condition_wrong_formatted(self):
        qg_condition = 'foo'
        with self.assertRaises(
                ConfigurationErrorInvalidQuestiongroupCondition):
            QuestionnaireQuestion(None, {
                'key': 'key_16', 'questiongroup_conditions': [qg_condition]})

    def test_raises_error_if_questiongroup_condition_expression_nonsense(self):
        qg_condition = ';%.|foo'
        with self.assertRaises(
                ConfigurationErrorInvalidQuestiongroupCondition):
            QuestionnaireQuestion(None, {
                'key': 'key_16', 'questiongroup_conditions': [qg_condition]})


class ValidateOptionsTest(TestCase):

    def test_raises_error_if_invalid_options(self):
        with self.assertRaises(ConfigurationErrorInvalidOption):
            validate_options(
                {"foo": "bar"}, ['bar'], QuestionnaireConfiguration)

    def test_raises_error_if_some_invalid_options(self):
        with self.assertRaises(ConfigurationErrorInvalidOption):
            validate_options(
                {"foo": "bar", "bar": "faz"}, ["foo"],
                QuestionnaireConfiguration)

    def test_passes_if_all_valid_options(self):
        validate_options(
            {"foo": "bar", "bar": "faz"}, ["foo", "bar"],
            QuestionnaireConfiguration)

    def test_passes_if_some_valid_options(self):
        validate_options(
            {"foo": "bar", "bar": "faz"}, ["foo", "bar", "faz"],
            QuestionnaireConfiguration)


class ValidateTypeTest(TestCase):

    def test_raises_error_if_invalid_type(self):
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            validate_type({}, list, 'foo', 'bar', 'faz')

    def test_passes_if_valid_type(self):
        validate_type({}, dict, 'foo', 'bar', 'faz')
