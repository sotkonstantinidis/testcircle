import uuid
from django.core.exceptions import ValidationError
from django.utils.translation import activate
from unittest.mock import patch

from accounts.tests.test_models import create_new_user
from configuration.models import Configuration
from qcat.tests import TestCase
from questionnaire.models import (
    Questionnaire,
    QuestionnaireConfiguration,
    QuestionnaireLink,
    QuestionnaireMembership,
    QuestionnaireTranslation,
    File,
)


def get_valid_file():
    return File.create_new(
        content_type='content_type', size=0, thumbnails={
            "header_1": "foo", "header_2": "bar"}, uuid=uuid.uuid4())


def get_valid_questionnaire(user=None):
    """
    Assumes fixture 'sample.json' is loaded
    """
    if user is None:
        user = create_new_user()
    return Questionnaire.create_new(
        configuration_code='sample', data={'foo': 'bar'},
        user=user)


def get_valid_metadata():
    return {
        'created': 'created',
        'updated': 'updated',
        'authors': ['author'],
        'code': 'code',
        'configurations': ['configuration'],
        'translations': ['en']
    }


@patch('questionnaire.models.put_questionnaire_data')
class QuestionnaireModelTest(TestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.user = create_new_user()

    def test_requires_data(self, mock_put_questionnaire_data):
        questionnaire = Questionnaire()
        with self.assertRaises(ValidationError):
            questionnaire.full_clean()

    def test_has_primary_key(self, mock_put_questionnaire_data):
        questionnaire = Questionnaire(data={})
        self.assertTrue(hasattr(questionnaire, 'id'))

    def test_has_uuid(self, mock_put_questionnaire_data):
        questionnaire = Questionnaire(data={})
        self.assertIsInstance(questionnaire.uuid, uuid.UUID)

    def test_create_new_returns_new_object(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        returned = Questionnaire.create_new(
            configuration_code='sample', data={'foo': 'bar'}, user=self.user)
        new_questionnaire = Questionnaire.objects.get(pk=returned.id)
        self.assertEqual(returned, new_questionnaire)

    def test_create_new_sets_data(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        self.assertEqual(questionnaire.data, {})

    def test_create_new_sets_default_status(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user, status=2)
        self.assertEqual(questionnaire.status, 2)

    def test_create_new_sets_status(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.status, 1)

    def test_create_new_sets_code(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.code, 'todo')

    def test_create_new_raises_error_if_invalid_status(
            self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(
                configuration_code='sample', data={}, user=self.user,
                status=-1)

    def test_create_new_sets_default_version(
            self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.version, 1)

    @patch.object(Configuration, 'get_active_by_code')
    @patch.object(QuestionnaireConfiguration.objects, 'create')
    def test_create_new_calls_configuration_get_active_by_code(
            self, mock_create, mock_Configuration_get_active_by_code,
            mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = 1, []
        Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        mock_Configuration_get_active_by_code.assert_called_once_with('sample')

    def test_create_new_raises_error_if_no_active_configuration(
            self, mock_put_questionnaire_data):
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(
                configuration_code='foo', data={}, user=self.user)

    def test_create_new_adds_configuration(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        configuration = Configuration.get_active_by_code('sample')
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_configurations = ret.configurations.all()
        self.assertEqual(len(ret_configurations), 1)
        self.assertEqual(ret_configurations[0].id, configuration.id)

    @patch('questionnaire.models.get_language')
    def test_create_new_calls_get_language(
            self, mock_get_language, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        mock_get_language.assert_called_once_with()

    def test_create_new_adds_language(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        language = 'en'
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_languages = ret.questionnairetranslation_set.all()
        self.assertEqual(len(ret_languages), 1)
        self.assertEqual(ret_languages[0].language, language)

    def test_create_new_adds_language2(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        language = 'es'
        activate('es')
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_languages = ret.questionnairetranslation_set.all()
        self.assertEqual(len(ret_languages), 1)
        self.assertEqual(ret_languages[0].language, language)
        activate('en')

    def test_create_new_adds_membership(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = 1, []
        questionnaire = get_valid_questionnaire(self.user)
        memberships = questionnaire.members.filter(
            questionnairemembership__role='author')
        self.assertEqual(len(memberships), 1)
        self.assertEqual(memberships[0], self.user)

    @patch('questionnaire.models.QuestionnaireMembership')
    @patch.object(Questionnaire.objects, 'create')
    @patch.object(QuestionnaireTranslation.objects, 'create')
    @patch.object(QuestionnaireConfiguration.objects, 'create')
    def test_create_new_calls_put_questionnaire_data(
            self, mock_create_conf_link, mock_create_translation, mock_create,
            mock_QuestionnaireMembership, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = 1, []
        Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        mock_put_questionnaire_data.assert_called_once_with(
            'sample', [mock_create.return_value])

    def test_get_metadata(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        metadata = questionnaire.get_metadata()
        self.assertIsInstance(metadata, dict)
        self.assertEqual(len(metadata), 7)
        self.assertEqual(metadata['created'], questionnaire.created)
        self.assertEqual(metadata['updated'], questionnaire.updated)
        self.assertEqual(
            metadata['authors'],
            [{'id': self.user.id, 'name': str(self.user)}])
        self.assertEqual(metadata['code'], questionnaire.code)
        self.assertEqual(metadata['configurations'], ['sample'])
        self.assertEqual(metadata['translations'], ['en'])
        self.assertEqual(metadata['status'], ('draft', 'Draft'))

    def test_get_metadata_puts_author_first(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        QuestionnaireMembership.objects.create(
            user=create_new_user(id=2, email='foo@bar.com'),
            questionnaire=questionnaire, role='editor')
        metadata = questionnaire.get_metadata()
        authors = metadata['authors']
        self.assertEqual(len(authors), 2)
        self.assertEqual(authors[0]['id'], 1)
        self.assertEqual(authors[1]['id'], 2)

    def test_has_links(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.links.count(), 0)

    def test_add_link_creates_link(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        self.assertEqual(QuestionnaireLink.objects.count(), 0)
        questionnaire_1 = get_valid_questionnaire(self.user)
        questionnaire_2 = get_valid_questionnaire(self.user)
        questionnaire_1.add_link(questionnaire_2)
        self.assertEqual(questionnaire_1.links.count(), 1)
        self.assertEqual(QuestionnaireLink.objects.count(), 2)
        self.assertEqual(questionnaire_1.links.first(), questionnaire_2)
        self.assertEqual(questionnaire_2.links.first(), questionnaire_1)

    def test_remove_link_removes_link(self, mock_put_questionnaire_data):
        mock_put_questionnaire_data.return_value = None, None
        questionnaire_1 = get_valid_questionnaire(self.user)
        questionnaire_2 = get_valid_questionnaire(self.user)
        questionnaire_1.add_link(questionnaire_2)
        self.assertEqual(questionnaire_2.links.count(), 1)
        self.assertEqual(QuestionnaireLink.objects.count(), 2)
        questionnaire_2.remove_link(questionnaire_1)
        self.assertEqual(questionnaire_2.links.count(), 0)
        self.assertEqual(QuestionnaireLink.objects.count(), 0)


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
