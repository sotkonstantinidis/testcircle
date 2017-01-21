from unittest.mock import patch, Mock, MagicMock, sentinel

from django.test import override_settings

from qcat.tests import TestCase
from summary.parsers import ConfiguredQuestionnaireParser
from summary.renderers import GlobalValuesMixin, SummaryRenderer


class SummaryConfigurationTest(TestCase):
    """
    Tests for parsers.ConfiguredQuestionnaireSummary
    """

    def setUp(self):
        self.obj = ConfiguredQuestionnaireParser(
            config=MagicMock(),
            summary_type='full',
            questionnaire=MagicMock(),
        )

    def test_put_question_data_omit_unconfigured(self):
        self.assertIsNone(
            self.obj.put_question_data(MagicMock(in_summary={'half': ''}))
        )

    @override_settings(CONFIGURATION_SUMMARY_OVERRIDE={
        'qg_keyword.field_name': {
            'override_key': sentinel.key,
            'override_fn': lambda self, child: sentinel.func
        }})
    def test_put_questionnaire_override(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={'full': 'field_name'}
        )
        self.obj.put_question_data(child=child)
        self.assertEqual(self.obj.data, {sentinel.key: sentinel.func})

    def test_put_questionnaire_duplicate(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={'full': 'spam'}
        )
        self.obj.get_value = lambda child: sentinel.new_value
        self.obj.put_question_data(child=child)
        self.obj.data['spam'] = sentinel.existing_value
        self.assertEqual(
            self.obj.data, {'spam': sentinel.existing_value}
        )

    def test_put_questionnaire(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={'full': 'spam'}
        )
        self.obj.get_value = lambda child: sentinel.some_value
        self.obj.put_question_data(child=child)
        self.assertEqual(
            self.obj.data, {'spam': sentinel.some_value}
        )

    def test_get_map_values_no_geom(self):
        self.obj.questionnaire.geom = False
        self.assertEqual(
            self.obj.get_map_values(''),
            {'img_url': '', 'coordinates': ''}
        )

    @patch('questionnaire.summary_configuration.get_static_map_url')
    def test_get_map_values(self, mock_static_map):
        mock_static_map.return_value = sentinel.map_url
        self.obj.questionnaire = MagicMock(geom=MagicMock(coords=sentinel.cord))
        self.assertEqual(
            self.obj.get_map_values(''),
            {'img_url': sentinel.map_url, 'coordinates': sentinel.cord}
        )

    def test_get_full_range_values(self):
        # choices as defined in child.choices
        all_choices = [
            ('pricey_key', 'pricey_value'),
            ('cheap_key', 'cheap_value'),
        ]
        self.obj.values['all_choices'] = [{'child_keyword': ['pricey_key']}]
        self.assertListEqual(
            [
                {'highlighted': True, 'text': 'pricey_value'},
                {'highlighted': False, 'text': 'cheap_value'}
            ],
            list(self.obj.get_full_range_values(
                child=MagicMock(
                    parent_object=MagicMock(keyword='all_choices'),
                    choices=all_choices,
                    keyword='child_keyword'
                )
            ))
        )

    # TODO: LV commented this test on Dec 27, 2016 because NotImplemetedError is
    # no longer raised. Please check whether this test can be adapted or
    # deleted.
    # def test_get_full_range_values_invalid(self):
    #     self.obj.values['mana'] = []
    #     with self.assertRaises(NotImplementedError):
    #         list(self.obj.get_full_range_values(
    #             child=MagicMock(parent_object=MagicMock(keyword='mana'))
    #         ))


class SummaryDataProviderTest(TestCase):
    def test_summary_type(self):
        with self.assertRaises(NotImplementedError):
            SummaryRenderer(config='', questionnaire='')

    @patch.object(ConfiguredQuestionnaireParser, '__init__')
    def test_content(self, mock_raw_data):
        mock_raw_data.return_value = {}
        with self.assertRaises(NotImplementedError):
            SummaryRenderer(config='', questionnaire='')


class GlobalValuesMixinTest(TestCase):

    def setUp(self):
        """

        """
        class Tmp(GlobalValuesMixin, SummaryRenderer):
            summary_type = 'type'
            content = ['sample']

            def sample(self):
                return sentinel.sample_value

        self.obj = Tmp(config=MagicMock(), questionnaire='')

    def test_raw_data_getter(self):
        # data as structured by the configured questionnaire summary
        self.obj.raw_data = {'key': [{'value': sentinel.expected}]}
        self.assertEqual(
            self.obj.raw_data_getter('key'),
            sentinel.expected
        )

    def test_raw_data_getter_custom_value(self):
        self.obj.raw_data = {'key': [{'value': sentinel.expected}]}
        self.assertEqual(
            self.obj.raw_data_getter('key', value=''),
            [{'value': sentinel.expected}]
        )

    def test_string_from_list(self):
        self.obj.raw_data = {'key': [{'values': ['will', 'i', 'am']}]}
        self.assertEqual(
            self.obj.string_from_list('key'),
            'will, i, am'
        )

# These lines are commented, as the structure of the summary will change.
#     def test_header_image(self):
#         pass
#
#     def test_title(self):
#         pass
#
#     def test_description(self):
#         pass
#
#     def test_conclusion(self):
#         pass
#
#     def test_references(self):
#         pass
#
#     def test_get_reference_compiler(self):
#         pass
#
#     def test_get_reference_resource_persons(self):
#         pass
#
#     def test_get_reference_links(self):
#         pass
#
#     def test_get_reference_articles(self):
#         pass
#
#
# class TechnologyFullSummaryProviderTest(TestCase):
#     def test_location(self):
#         pass
#
#
# class ApproachesSummaryProviderTest(TestCase):
#     def test_location(self):
#         pass
