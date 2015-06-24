import datetime
from unittest.mock import patch, Mock

from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
    QuestionnaireSubcategory,
    QuestionnaireQuestiongroup,
    QuestionnaireQuestion,
    QuestionnaireSection,
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
        conf = QuestionnaireConfiguration('sample')
        list_data = conf.get_list_data([q.data for q in questionnaires])
        self.assertEqual(len(list_data), 2)
        for d in list_data:
            self.assertEqual(len(d), 1)
            self.assertIn('key_1', d)


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
            conf, {}, conf_object.data)

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
                'sections'),
            list, 'sections', 'list of dicts', '-')


class QuestionnaireConfigurationMergeConfigurationsTest(TestCase):

    def setUp(self):
        self.obj = Mock()
        self.obj.name_children = 'sections'
        self.obj.Child = QuestionnaireSection

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireConfiguration.merge_configurations(self.obj, {}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireSection, 'merge_configurations')
    def test_calls_validate_type_base_categories(
            self, mock_Category_merge_configurations, mock_validate_type):
        QuestionnaireConfiguration.merge_configurations(
            self.obj, {"sections": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"sections": [{}]}
        ret = QuestionnaireConfiguration.merge_configurations(
            self.obj, base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"sections": [{"foo": "bar"}]}
        ret = QuestionnaireConfiguration.merge_configurations(
            self.obj, base, {})
        self.assertEqual(ret, base)

    @patch.object(QuestionnaireSection, 'merge_configurations')
    def test_calls_category_merge_configurations(
            self, mock_Category_merge_configurations):
        base = {"sections": [{"foo": "bar"}]}
        QuestionnaireConfiguration.merge_configurations(self.obj, base, {})
        mock_Category_merge_configurations.assert_called_once_with(
            self.obj.Child, {"foo": "bar"}, {})

    def test_merges_with_base_empty(self):
        base = {}
        specific = {
            "sections": [
                {
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
            ]
        }
        conf = QuestionnaireConfiguration.merge_configurations(
            self.obj, base, specific)
        self.assertIn('sections', conf)
        self.assertNotIn('categories', conf)
        self.assertNotIn('subcategories', conf)
        self.assertNotIn('questions', conf)
        self.assertNotIn('questiongroups', conf)
        self.assertEqual(len(conf['sections']), 1)
        section = conf['sections'][0]
        self.assertNotIn('sections', section)
        self.assertIn('categories', section)
        self.assertNotIn('subcategories', section)
        self.assertNotIn('questions', section)
        self.assertNotIn('questiongroups', section)
        self.assertEqual(len(section['categories']), 1)
        category = section['categories'][0]
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
        base = {"sections": [{"keyword": "foo", "subcategories": []}]}
        specific = {"sections": [{"keyword": "bar", "subcategories": []}]}
        conf = QuestionnaireConfiguration.merge_configurations(
            self.obj, base, specific)
        self.assertEqual(len(conf['sections']), 2)
        for cat in conf['sections']:
            self.assertIn(cat['keyword'], ['foo', 'bar'])


class QuestionnaireCategoryTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.configuration = Mock()

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidOption):
            QuestionnaireCategory(self.configuration, configuration_dict)
        mock_validate_type.assert_called_once_with(
            configuration_dict, dict, 'categories', 'list of dicts',
            'sections')

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

    def test_raises_error_if_subcategories_not_list(self):
        configuration_dict = {
            "keyword": "cat_1",
            "subcategories": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireCategory(self.configuration, configuration_dict)


class QuestionnaireCategoryMergeConfigurationsTest(TestCase):

    def setUp(self):
        self.obj = Mock()
        self.obj.name_children = 'subcategories'
        self.obj.Child = QuestionnaireSubcategory

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireCategory.merge_configurations(self.obj, {}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    @patch.object(QuestionnaireSubcategory, 'merge_configurations')
    def test_calls_validate_type_base_categories(
            self, mock_Category_merge_configurations, mock_validate_type):
        QuestionnaireCategory.merge_configurations(
            self.obj, {"subcategories": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 4)

    def test_returns_dict(self):
        base = {"subcategories": [{}]}
        ret = QuestionnaireCategory.merge_configurations(self.obj, base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"subcategories": [{"foo": "bar"}]}
        ret = QuestionnaireCategory.merge_configurations(self.obj, base, {})
        self.assertEqual(ret, base)

    @patch.object(QuestionnaireSubcategory, 'merge_configurations')
    def test_calls_category_merge_configurations(
            self, mock_Category_merge_configurations):
        base = {"subcategories": [{"foo": "bar"}]}
        QuestionnaireCategory.merge_configurations(self.obj, base, {})
        mock_Category_merge_configurations.assert_called_once_with(
            self.obj.Child, {"foo": "bar"}, {})

    def test_appends_specific(self):
        base = {"subcategories": [{"keyword": "foo", "questiongroups": []}]}
        specific = {
            "subcategories": [{"keyword": "bar", "questiongroups": []}]}
        conf = QuestionnaireCategory.merge_configurations(
            self.obj, base, specific)
        self.assertEqual(len(conf['subcategories']), 2)
        for cat in conf['subcategories']:
            self.assertIn(cat['keyword'], ['foo', 'bar'])


class QuestionnaireSubcategoryTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.category = Mock()

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

    @patch.object(QuestionnaireSubcategory, 'validate_options')
    def test_calls_validate_options(self, mock_validate_options):
        configuration_dict = {
            "foo": "bar"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)
        mock_validate_options.assert_called_once_with()

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

    # def test_raises_error_if_no_questiongroups(self):
    #     configuration_dict = {
    #         "keyword": "subcat_1_1"
    #     }
    #     with self.assertRaises(ConfigurationErrorInvalidConfiguration):
    #         QuestionnaireSubcategory(self.category, configuration_dict)

    def test_raises_error_if_questiongroups_not_list(self):
        configuration_dict = {
            "keyword": "subcat_1_1",
            "questiongroups": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireSubcategory(self.category, configuration_dict)


class QuestionnaireQuestiongroupTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.subcategory = Mock()
        self.subcategory.name_children = 'questions'

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
            "questions": [{"keyword": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_min_num_smaller_than_1(self):
        configuration_dict = {
            "keyword": "qg_1",
            "min_num": 0,
            "questions": [{"keyword": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_max_num_not_integer(self):
        configuration_dict = {
            "keyword": "qg_1",
            "max_num": "foo",
            "questions": [{"keyword": "key_1"}]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)

    def test_raises_error_if_max_num_smaller_than_1(self):
        configuration_dict = {
            "keyword": "qg_1",
            "max_num": -1,
            "questions": [{"keyword": "key_1"}]
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

    def test_raises_error_if_questions_not_list(self):
        configuration_dict = {
            "keyword": "qg_1",
            "questions": "foo"
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestiongroup(self.subcategory, configuration_dict)


class QuestionnaireQuestiongroupMergeConfigurationsTest(TestCase):

    def setUp(self):
        self.obj = Mock()
        self.obj.name_children = 'questions'
        self.obj.Child = QuestionnaireQuestion

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        QuestionnaireQuestiongroup.merge_configurations(self.obj, {}, {})
        self.assertEqual(mock_validate_type.call_count, 3)

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type_base_categories(
            self, mock_validate_type):
        QuestionnaireQuestiongroup.merge_configurations(
            self.obj, {"questions": [{}]}, {})
        self.assertEqual(mock_validate_type.call_count, 7)

    def test_returns_dict(self):
        base = {"questions": [{}]}
        ret = QuestionnaireQuestiongroup.merge_configurations(
            self.obj, base, {})
        self.assertEqual(ret, base)

    def test_returns_base_dict(self):
        base = {"questions": [{"foo": "bar"}]}
        ret = QuestionnaireQuestiongroup.merge_configurations(
            self.obj, base, {})
        self.assertEqual(ret, base)

    def test_merge_configurations_merges_questions(self):
        base = {
            "questions": [
                {
                    "keyword": "bar_1"
                }, {
                    "keyword": "bar_2"
                }
            ]
        }
        specific = {
            "questions": [
                {
                    "keyword": "bar_3"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            self.obj, base, specific)
        self.assertEqual(len(merged.get('questions', [])), 3)

    def test_merge_configurations_merges_question_if_base_empty(self):
        base = {}
        specific = {
            "questions": [
                {
                    "keyword": "bar_1"
                }, {
                    "keyword": "bar_2"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            self.obj, base, specific)
        self.assertEqual(len(merged.get('questions', [])), 2)

    def test_merge_configurations_overwrites_existing_question(self):
        base = {
            "questions": [
                {
                    "keyword": "foo",
                    "foo": "bar_1"
                }, {
                    "keyword": "bar"
                }
            ]
        }
        specific = {
            "questions": [
                {
                    "keyword": "foo",
                    "foo": "bar_2"
                }
            ]
        }
        merged = QuestionnaireQuestiongroup.merge_configurations(
            self.obj, base, specific)
        self.assertEqual(len(merged.get('questions', [])), 2)
        for q in merged.get('questions', []):
            if q.get('keyword') == 'foo':
                self.assertEqual(q.get('foo'), 'bar_2')


class QuestionnaireQuestionTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.obj = Mock()
        self.obj.name_children = ''
        self.obj.Child = None
        self.parent_obj = Mock()

    def test_raises_error_if_key_not_found(self):
        configuration = {}
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(self.parent_obj, configuration)

    def test_raises_error_if_key_not_string(self):
        configuration = {
            "keyword": ["bar"]
        }
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            QuestionnaireQuestion(self.parent_obj, configuration)

    def test_raises_error_if_not_in_db(self):
        configuration = {
            "keyword": "bar"
        }
        with self.assertRaises(ConfigurationErrorNotInDatabase):
            QuestionnaireQuestion(self.parent_obj, configuration)

    def test_raises_error_if_form_template_not_found(self):
        configuration = {
            'keyword': 'key_14',
            'form_template': 'foo'
        }
        with self.assertRaises(ConfigurationErrorTemplateNotFound):
            QuestionnaireQuestion(self.parent_obj, configuration)

    def test_lookup_choices_lookups_single_choice(self):
        mock_Questiongroup = Mock()
        mock_Questiongroup.configuration_keyword = 'sample'
        q = QuestionnaireQuestion(mock_Questiongroup, {'keyword': 'key_14'})
        l = q.lookup_choices_labels_by_keywords(['value_14_1'])
        self.assertEqual(l, ['Value 14_1'])

    def test_lookup_choices_lookups_many_choices(self):
        mock_Questiongroup = Mock()
        mock_Questiongroup.configuration_keyword = 'sample'
        q = QuestionnaireQuestion(mock_Questiongroup, {'keyword': 'key_14'})
        l = q.lookup_choices_labels_by_keywords(['value_14_1', 'value_14_2'])
        self.assertEqual(l, ['Value 14_1', 'Value 14_2'])

    def test_lookup_choices_boolean(self):
        q = QuestionnaireQuestion(self.parent_obj, {'keyword': 'key_14'})
        q.choices = ((True, 'Yes'), (False, 'No'))
        l = q.lookup_choices_labels_by_keywords([True])
        self.assertEqual(l, ['Yes'])

    def test_lookup_choices_integer(self):
        q = QuestionnaireQuestion(self.parent_obj, {'keyword': 'key_12'})
        q.choices = ((1, 'Low'), (2, 'High'))
        l = q.lookup_choices_labels_by_keywords([1])
        self.assertEqual(l, ['Low'])

    def test_raises_error_if_condition_wrong_formatted(self):
        condition = 'foo'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                self.parent_obj,
                {'keyword': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_value_does_not_exist(self):
        condition = 'foo|True|key_16'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                self.parent_obj,
                {'keyword': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_condition_expression_nonsense(self):
        condition = 'value_15_1|;:_|key_16'
        with self.assertRaises(ConfigurationErrorInvalidCondition):
            QuestionnaireQuestion(
                self.parent_obj,
                {'keyword': 'key_15', 'conditions': [condition]})

    def test_raises_error_if_questiongroup_condition_wrong_formatted(self):
        qg_condition = 'foo'
        with self.assertRaises(
                ConfigurationErrorInvalidQuestiongroupCondition):
            QuestionnaireQuestion(
                self.parent_obj,
                {
                    'keyword': 'key_16',
                    'questiongroup_conditions': [qg_condition]})

    def test_raises_error_if_questiongroup_condition_expression_nonsense(self):
        qg_condition = ';%.|foo'
        with self.assertRaises(
                ConfigurationErrorInvalidQuestiongroupCondition):
            QuestionnaireQuestion(
                self.parent_obj, {
                    'keyword': 'key_16',
                    'questiongroup_conditions': [qg_condition]})


class BaseConfigurationObjectMergeConfigurationTest(TestCase):

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type(self, mock_validate_type):
        conf = get_valid_questionnaire_configuration()
        mock = Mock()
        conf.merge_configurations(mock, {"foo": "base"}, {"foo": "specific"})
        self.assertEqual(mock_validate_type.call_count, 3)
        # mock_validate_type.assert_any_call(
        #     {"foo": "base"}, dict, mock.name_current, dict, mock.name_parent)
        mock_validate_type.assert_any_call(
            {"foo": "specific"}, dict, mock.name_current, dict,
            mock.name_parent)
        mock_validate_type.assert_any_call(
            [], list, mock.name_children, list, mock.name_current)

    @patch('configuration.configuration.validate_type')
    def test_calls_validate_type_with_children(self, mock_validate_type):
        conf = get_valid_questionnaire_configuration()
        mock = Mock()
        mock.name_children = 'foo'
        conf.merge_configurations(
            mock, {"foo": [{"bar": "faz"}]}, {"foo": [{"bar": "fuz"}]})
        self.assertEqual(mock_validate_type.call_count, 4)
        # mock_validate_type.assert_any_call(
        #     {"foo": [{"bar": "faz"}]}, dict, mock.name_current, dict,
        #     mock.name_parent)
        mock_validate_type.assert_any_call(
            {"foo": [{"bar": "fuz"}]}, dict, mock.name_current, dict,
            mock.name_parent)
        mock_validate_type.assert_any_call(
            [{"bar": "faz"}], list, mock.name_children, list,
            mock.name_current)
        mock_validate_type.assert_any_call(
            [{"bar": "fuz"}], list, mock.name_children, list,
            mock.name_current)

    def test_calls_merge_configuration_of_child_obj(self):
        conf = get_valid_questionnaire_configuration()
        mock_child = Mock()
        mock = Mock()
        mock.name_children = 'foo'
        mock.Child = mock_child
        conf.merge_configurations(
            mock, {"foo": [{"bar": "faz"}]}, {"foo": [{"bar": "fuz"}]})
        mock.Child.merge_configurations.assert_called_once_with(
            mock.Child, {'bar': 'faz'}, {})


class BaseConfigurationObjectValidateOptions(TestCase):

    def test_raises_error_if_invalid_options(self):
        conf = get_valid_questionnaire_configuration()
        conf.configuration = {"foo": "bar"}
        conf.valid_options = ["bar"]
        with self.assertRaises(ConfigurationErrorInvalidOption):
            conf.validate_options()

    def test_raises_error_if_some_invalid_options(self):
        conf = get_valid_questionnaire_configuration()
        conf.configuration = {"foo": "bar", "bar": "faz"}
        conf.valid_options = ["foo"]
        with self.assertRaises(ConfigurationErrorInvalidOption):
            conf.validate_options()

    def test_passes_if_all_valid_options(self):
        conf = get_valid_questionnaire_configuration()
        conf.configuration = {"foo": "bar", "bar": "faz"}
        conf.valid_options = ["foo", "bar"]
        conf.validate_options()  # Should not raise

    def test_passes_if_some_valid_options(self):
        conf = get_valid_questionnaire_configuration()
        conf.configuration = {"foo": "bar", "bar": "faz"}
        conf.valid_options = ["foo", "bar", "faz"]
        conf.validate_options()  # Should not raise


class ValidateTypeTest(TestCase):

    def test_raises_error_if_invalid_type(self):
        with self.assertRaises(ConfigurationErrorInvalidConfiguration):
            validate_type({}, list, 'foo', 'bar', 'faz')

    def test_passes_if_valid_type(self):
        validate_type({}, dict, 'foo', 'bar', 'faz')
