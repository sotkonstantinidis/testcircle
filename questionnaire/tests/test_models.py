import uuid
from django.core.exceptions import ValidationError
from unittest.mock import patch

from configuration.models import Configuration
from qcat.tests import TestCase
from questionnaire.models import (
    Questionnaire,
    File,
)


def get_valid_file():
    return File.create_new(
        content_type='content_type', size=0, thumbnails={
            "header_1": "foo", "header_2": "bar"}, uuid=uuid.uuid4())


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


class FileModelTest(TestCase):

    def test_requires_uuid(self):
        file = File(content_type='foo/bar')
        with self.assertRaises(ValidationError):
            file.full_clean()

    def test_requires_mime_type(self):
        file = File(uuid=uuid.uuid4())
        with self.assertRaises(ValidationError):
            file.full_clean()

    def test_has_primary_key(self):
        file = File()
        self.assertTrue(hasattr(file, 'id'))

    def test_get_valid_file_is_valid(self):
        file = get_valid_file()
        file.full_clean()  # Should not raise

    def test_create_new_returns_new_object(self):
        ret = File.create_new(content_type='foo/bar')
        q = File.objects.get(pk=ret.id)
        self.assertEqual(ret, q)

    def test_create_new_sets_uuid_if_not_set(self):
        file = File.create_new(content_type='foo/bar')
        self.assertIsInstance(file.uuid, uuid.UUID)

    def test_get_url_returns_none_if_thumbnail_not_found(self):
        file = get_valid_file()
        self.assertIsNone(file.get_url('foo'))

    def test_get_url_returns_none_if_file_extension_is_none(self):
        file = get_valid_file()
        file.content_type = 'foo'
        self.assertIsNone(file.get_url())

    def test_get_url_returns_static_url(self):
        file = get_valid_file()
        file.content_type = 'image/jpeg'
        uid = file.uuid
        url = file.get_url()
        self.assertIn('{}.jpg'.format(uid), url)
