import uuid
from django.core.exceptions import ValidationError
from unittest.mock import patch

from configuration.models import Configuration
from qcat.tests import TestCase
from questionnaire.models import Questionnaire


class QuestionnaireModelTest(TestCase):

    fixtures = ['sample.json']

    def test_requires_data(self):
        questionnaire = Questionnaire()
        with self.assertRaises(ValidationError):
            questionnaire.full_clean()

    def test_has_primary_key(self):
        questionnaire = Questionnaire(data={})
        self.assertTrue(hasattr(questionnaire, 'id'))

    def test_has_uuid(self):
        questionnaire = Questionnaire(data={})
        self.assertIsInstance(questionnaire.uuid, uuid.UUID)

    def test_create_new_returns_new_object(self):
        returned = Questionnaire.create_new(
            configuration_code='sample', data={'foo': 'bar'})
        new_questionnaire = Questionnaire.objects.get(pk=returned.id)
        self.assertEqual(returned, new_questionnaire)

    def test_create_new_sets_data(self):
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={})
        self.assertEqual(questionnaire.data, {})

    @patch.object(Configuration, 'get_active_by_code')
    def test_create_new_calls_configuration_get_active_by_code(
            self, mock_Configuration_get_active_by_code):
        Questionnaire.create_new(configuration_code='sample', data={})
        mock_Configuration_get_active_by_code.assert_called_once_with('sample')

    def test_create_new_raises_error_if_no_active_configuration(self):
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(configuration_code='foo', data={})

    def test_create_new_adds_configuration(self):
        configuration = Configuration.get_active_by_code('sample')
        ret = Questionnaire.create_new(configuration_code='sample', data={})
        ret_configurations = ret.configurations.all()
        self.assertEqual(len(ret_configurations), 1)
        self.assertEqual(ret_configurations[0].id, configuration.id)
