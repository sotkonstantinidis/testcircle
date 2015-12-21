import uuid
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import activate
from unittest.mock import patch

from accounts.tests.test_models import create_new_user
from configuration.models import Configuration
from qcat.tests import TestCase
from questionnaire.models import (
    Questionnaire,
    QuestionnaireLink,
    QuestionnaireMembership,
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


class QuestionnaireModelTest(TestCase):

    fixtures = ['sample.json', 'sample_global_key_values.json']

    def setUp(self):
        self.user = create_new_user()

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
            configuration_code='sample', data={'foo': 'bar'}, user=self.user)
        new_questionnaire = Questionnaire.objects.get(pk=returned.id)
        self.assertEqual(returned, new_questionnaire)

    def test_create_new_sets_data(self):
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        self.assertEqual(questionnaire.data, {})

    def test_create_new_sets_status(self):
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user, status=2)
        self.assertEqual(questionnaire.status, 2)

    def test_create_new_sets_default_status(self):
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.status, 1)

    def test_create_new_sets_default_created(self):
        questionnaire = get_valid_questionnaire(self.user)
        self.assertIsNotNone(questionnaire.created)

    def test_create_new_sets_created(self):
        date = datetime.now()
        questionnaire = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user, created=date)
        self.assertEqual(questionnaire.created, date)

    def test_previous_version_only_allows_certain_status(self):
        previous = Questionnaire(status=2)
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(
                configuration_code='sample', data={}, user=self.user,
                previous_version=previous)

    def test_previous_version_pending_updates_same_questionnaire(self):
        previous = get_valid_questionnaire(self.user)
        previous.status = 1
        q = Questionnaire.create_new(
            configuration_code='sample', data={'faz': 'taz'}, user=self.user,
            previous_version=previous)
        self.assertEqual(q, previous)
        self.assertEqual(previous.data, {'faz': 'taz'})

    def test_previous_version_public_keeps_same_code(self):
        previous = get_valid_questionnaire(self.user)
        previous.status = 3
        q = Questionnaire.create_new(
            configuration_code='sample', data={'faz': 'taz'}, user=self.user,
            previous_version=previous)
        self.assertNotEqual(q, previous)
        self.assertEqual(q.code, previous.code)
        self.assertEqual(q.version, previous.version + 1)

    @patch('configuration.utils.create_new_code')
    def test_create_new_calls_create_code(self, mock_create_new_code):
        get_valid_questionnaire(self.user)
        mock_create_new_code.assert_called_once_with('sample', {'foo': 'bar'})

    def test_create_new_raises_error_if_invalid_status(self):
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(
                configuration_code='sample', data={}, user=self.user,
                status=-1)

    def test_create_new_sets_default_version(self):
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.version, 1)

    def test_create_new_raises_error_if_no_active_configuration(self):
        with self.assertRaises(ValidationError):
            Questionnaire.create_new(
                configuration_code='foo', data={}, user=self.user)

    def test_create_new_adds_configuration(self):
        configuration = Configuration.get_active_by_code('sample')
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_configurations = ret.configurations.all()
        self.assertEqual(len(ret_configurations), 1)
        self.assertEqual(ret_configurations[0].id, configuration.id)

    @patch('questionnaire.models.get_language')
    def test_create_new_calls_get_language(self, mock_get_language):
        Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        mock_get_language.assert_called_once_with()

    def test_create_new_adds_language(self):
        language = 'en'
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_languages = ret.questionnairetranslation_set.all()
        self.assertEqual(len(ret_languages), 1)
        self.assertEqual(ret_languages[0].language, language)

    def test_create_new_adds_language2(self):
        language = 'es'
        activate('es')
        ret = Questionnaire.create_new(
            configuration_code='sample', data={}, user=self.user)
        ret_languages = ret.questionnairetranslation_set.all()
        self.assertEqual(len(ret_languages), 1)
        self.assertEqual(ret_languages[0].language, language)
        activate('en')

    @patch.object(Questionnaire, 'update_users_from_data')
    def test_create_new_calls_update_users_from_data(self, mock_foo):
        get_valid_questionnaire(self.user)
        mock_foo.assert_called_once_with('sample', self.user)

    def test_get_users_returns_tuples(self):
        questionnaire = get_valid_questionnaire(self.user)
        users = questionnaire.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][0], 'author')
        self.assertEqual(users[0][1], self.user)

    def test_add_user_adds_user(self):
        questionnaire = get_valid_questionnaire(self.user)
        questionnaire.add_user(self.user, 'landuser')
        users = questionnaire.get_users()
        self.assertEqual(len(users), 2)
        for role, user in users:
            self.assertIn(role, ['author', 'landuser'])
            self.assertIn(user, [self.user])

    def test_remove_user_removes_user(self):
        questionnaire = get_valid_questionnaire(self.user)
        questionnaire.remove_user(self.user, 'author')
        users = questionnaire.get_users()
        self.assertEqual(len(users), 0)

    def test_update_users_from_data_adds_author(self):
        questionnaire = get_valid_questionnaire(self.user)
        questionnaire.remove_user(self.user, 'author')
        questionnaire.update_users_from_data('sample', self.user)
        users = questionnaire.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][0], 'author')
        self.assertEqual(users[0][1], self.user)

    def test_update_users_from_data_adds_user_from_data(self):
        questionnaire = get_valid_questionnaire(self.user)
        user_2 = create_new_user(id=2, email='foo@bar.com')
        questionnaire.data = {'qg_31': [{'key_39': '2', 'key_40': 'Foo Bar'}]}
        questionnaire.update_users_from_data('sample', self.user)
        users = questionnaire.get_users()
        self.assertEqual(len(users), 2)
        for role, user in users:
            self.assertIn(role, ['author', 'landuser'])
            self.assertIn(user, [self.user, user_2])

    def test_update_users_from_data_removes_user_from_data(self):
        questionnaire = get_valid_questionnaire(self.user)
        user_2 = create_new_user(id=2, email='foo@bar.com')
        questionnaire.add_user(user_2, 'landuser')
        questionnaire.update_users_from_data('sample', self.user)
        users = questionnaire.get_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0][0], 'author')
        self.assertEqual(users[0][1], self.user)

    def test_update_users_in_data_updates_name(self):
        questionnaire = get_valid_questionnaire(self.user)
        user_2 = create_new_user(
            id=2, email='foo@bar.com', firstname='Faz', lastname='Taz')
        questionnaire.data = {'qg_31': [{'key_39': '2', 'key_40': 'Foo Bar'}]}
        questionnaire.update_users_from_data('sample', self.user)
        users = questionnaire.get_users()
        self.assertEqual(len(users), 2)
        questionnaire.update_users_in_data(user_2)
        self.assertEqual(
            questionnaire.data,
            {'qg_31': [{'key_39': '2', 'key_40': 'Faz Taz'}]})

    def test_get_metadata(self):
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

    def test_get_metadata_puts_author_first(self):
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

    def test_has_links(self):
        questionnaire = get_valid_questionnaire(self.user)
        self.assertEqual(questionnaire.links.count(), 0)

    def test_add_link_creates_link(self):
        self.assertEqual(QuestionnaireLink.objects.count(), 0)
        questionnaire_1 = get_valid_questionnaire(self.user)
        questionnaire_2 = get_valid_questionnaire(self.user)
        questionnaire_1.add_link(questionnaire_2)
        self.assertEqual(questionnaire_1.links.count(), 1)
        self.assertEqual(QuestionnaireLink.objects.count(), 2)
        self.assertEqual(questionnaire_1.links.first(), questionnaire_2)
        self.assertEqual(questionnaire_2.links.first(), questionnaire_1)

    def test_remove_link_removes_link(self):
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
