from unittest.mock import patch, MagicMock, sentinel

from qcat.tests import TestCase
from summary.parsers import QuestionnaireParser


class SummaryConfigurationTest(TestCase):
    """
    Tests for parsers.ConfiguredQuestionnaireSummary
    """

    def setUp(self):
        self.obj = QuestionnaireParser(
            config=MagicMock(),
            summary_type='full',
            questionnaire=MagicMock(),
        )
        self.child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={'types': ['full'], 'default': {'field_name': 'spam'}}
        )

    def test_put_question_data_omit_unconfigured(self):
        self.assertIsNone(
            self.obj.put_question_data(MagicMock(in_summary={'half': ''}))
        )

    def test_put_questionnaire_field_name(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={'types': ['full'],
                     'default':{'field_name': sentinel.field_name}}
        )
        self.obj.put_question_data(child=child)
        self.assertTrue(
            sentinel.field_name in self.obj.data
        )

    def test_put_questionnaire_multiple_field_names(self):
        child = MagicMock(
            keyword='keyword',
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={
                'types': ['full'],
                'default': {
                    'field_name': {'qg_keyword.keyword': sentinel.field_name}
                }
            }
        )
        self.obj.put_question_data(child=child)
        self.assertTrue(
            sentinel.field_name in self.obj.data
        )

    def test_put_questionnaire_override_function(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={
                'types': ['full'],
                'default':
                    {'field_name': 'spam', 'get_value': {'name': 'foo'}}
            }
        )
        self.obj.foo = MagicMock()
        self.obj.put_question_data(child=child)
        self.obj.foo.assert_called_once_with(child=child)

    def test_put_questionnaire_override_function_config_type(self):
        child = MagicMock(
            questiongroup=MagicMock(keyword='qg_keyword'),
            summary={
                'types': ['full'],
                'default': {'field_name': 'spam', 'get_value': {'name': 'foo'}},
                'full': {'get_value': {'name': 'bar'}}
            }
        )
        self.obj.bar = MagicMock()
        self.obj.put_question_data(child=child)
        self.obj.bar.assert_called_once_with(child=child)

    def test_put_questionnaire_duplicate(self):
        self.obj.get_value = lambda child: sentinel.new_value
        self.obj.put_question_data(child=self.child)
        self.obj.data['spam'] = sentinel.existing_value
        self.assertEqual(
            self.obj.data, {'spam': sentinel.existing_value}
        )

    def test_put_questionnaire(self):
        self.obj.get_value = lambda child: sentinel.some_value
        self.obj.put_question_data(child=self.child)
        self.assertEqual(
            self.obj.data, {'spam': sentinel.some_value}
        )

    def test_get_map_values_no_geom(self):
        obj = QuestionnaireParser(
            config=MagicMock(),
            summary_type='full',
            questionnaire=MagicMock(geom=None),
        )
        self.assertEqual(
            obj.get_map_values(''),
            {'img_url': '', 'coordinates': []}
        )

    @patch('summary.parsers.get_static_map_url')
    def test_get_map_values(self, mock_static_map):
        mock_static_map.return_value = sentinel.map_url
        obj = QuestionnaireParser(
            config=MagicMock(),
            summary_type='full',
            questionnaire=MagicMock(
                geom=MagicMock(coords=[(123.123456789, 456)])
            ),
        )
        self.assertEqual(
            obj.get_map_values(''),
            {'img_url': sentinel.map_url, 'coordinates': ['123.12346, 456']}
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
