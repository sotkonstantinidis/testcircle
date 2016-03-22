from unittest.mock import patch

from configuration.cache import get_configuration
from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from questionnaire.serializers import QuestionnaireSerializer

from .test_models import get_valid_questionnaire


class SerializerTest(TestCase):

    fixtures = ['sample.json', 'sample_global_key_values.json']

    def setUp(self):
        self.questionnaire = get_valid_questionnaire()

    def test_init_with_config(self):
        configuration = QuestionnaireConfiguration(self.questionnaire.code)
        serializer = QuestionnaireSerializer(
            instance=self.questionnaire, config=configuration
        )
        self.assertEqual(serializer.config, configuration)

    def test_init_without_config(self):
        config = self.questionnaire.questionnaireconfiguration_set.filter(
            original_configuration=True
        ).first()
        original_config = get_configuration(config.configuration.code)

        serializer = QuestionnaireSerializer(
            instance=self.questionnaire
        )

        self.assertEqual(serializer.config.keyword, original_config.keyword)

    def test_get_links(self):
        linked_questionnaire = get_valid_questionnaire()
        self.questionnaire.add_link(linked_questionnaire)
        self.questionnaire.save()
        with patch('questionnaire.utils.get_link_display') as get_link_display:
            QuestionnaireSerializer(self.questionnaire).data  # noqa
            get_link_display.assert_called_with(
                'sample', 'Unknown name', 'sample_1'
            )

    def test_complete_serialization(self):
        data = QuestionnaireSerializer(self.questionnaire).data
        expected = {
            'code': 'sample_0',
            'url': '/en/sample/view/sample_0/',
            'compilers': [{'id': 1, 'name': 'bar foo'}],
            'list_data': {},
            'translations': ['en'],
            'name': {'en': 'Unknown name'},
            'data': {"foo": "bar"},
            'editors': [],
            'links': {'en': [], 'es': [], 'fr': []},
            'configurations': ['sample'],
            'status': ('draft', 'Draft'),
            'serializer_config': 'sample'
        }
        # datetimes are not relevant to the structure.
        del data['created']
        del data['updated']

        self.assertDictEqual(data, expected)
