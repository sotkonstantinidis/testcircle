import json
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http.response import HttpResponse
from django.test.client import RequestFactory
from unittest.mock import patch, Mock

from accounts.tests.test_authentication import (
    create_new_user,
    do_log_in,
)
from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
    QuestionnaireSection,
)
from qcat.tests import TestCase
from qcat.utils import session_store
from questionnaire.models import Questionnaire, File
from questionnaire.views import (
    generic_questionnaire_details,
    generic_questionnaire_list,
    generic_questionnaire_new,
    generic_questionnaire_new_step,
)
from sample.tests.test_views import (
    get_section_count,
    get_valid_new_step_values,
    get_valid_new_values,
    get_valid_details_values,
    get_valid_list_values,
    route_questionnaire_details,
    route_questionnaire_list,
)

file_upload_route = 'file_upload'
file_display_route = 'file_serve'
valid_file = 'static/assets/img/img01.jpg'
invalid_file = 'bower.json'  # Needs to exist but not valid file type


class GenericQuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/sample/new/cat_1')
        self.request.user = create_new_user()
        session_store.clear()

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_category')
    def test_creates_questionnaire_configuration(
            self, mock_QuestionnaireConfiguration_get_category,
            mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        mock_QuestionnaireConfiguration_get_category.return_value = None
        with self.assertRaises(Http404):
            generic_questionnaire_new_step(
                self.request, 'cat_1', 'sample', 'template', 'route')
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch.object(QuestionnaireConfiguration, 'get_category')
    def test_gets_category(self, mock_get_category):
        mock_get_category.return_value = None
        with self.assertRaises(Http404):
            generic_questionnaire_new_step(
                self.request, 'cat_1', 'sample', 'template', 'route')
        mock_get_category.assert_called_once_with('cat_1')

    @patch('questionnaire.views.get_session_questionnaire')
    def test_calls_get_session_questionnaire(
            self, mock_get_session_questionnaire):
        mock_get_session_questionnaire.return_value = {}
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values()[0])
        mock_get_session_questionnaire.assert_called_once_with('sample')

    @patch('questionnaire.views.get_questionnaire_data_for_translation_form')
    def test_calls_get_questionnaire_data_for_translation_form(
            self, mock_get_questionnaire_data):
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values()[0])
        mock_get_questionnaire_data.assert_called_once_with({}, 'en', None)

    @patch.object(QuestionnaireCategory, 'get_form')
    def test_calls_category_get_form(self, mock_get_form):
        mock_get_form.return_value = None, None
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values()[0])
        mock_get_form.assert_called_once_with(
            post_data=None, show_translation=False, initial_data={})

    @patch.object(QuestionnaireCategory, 'get_form')
    @patch('questionnaire.views.save_session_questionnaire')
    def test_form_submission_saves_form(
            self, mock_save_session_questionnaire, mock_get_form):
        mock_get_form.return_value = None, []
        r = self.request
        r.method = 'POST'
        generic_questionnaire_new_step(
            r, *get_valid_new_step_values()[0])
        mock_save_session_questionnaire.assert_called_once_with({}, 'sample')

    @patch.object(QuestionnaireCategory, 'get_form')
    @patch('questionnaire.views.render')
    def test_calls_render(self, mock_render, mock_get_form):
        mock_get_form.return_value = "foo", "bar"
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values()[0])
        mock_render.assert_called_once_with(
            self.request, 'form/category.html', {
                'category_formsets': "bar",
                'category_config': "foo",
                'title': 'QCAT Form',
                'overview_url': '/en/sample/edit/#cat_0',
                'valid': True,
                'configuration_name': 'sample',
            })

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values()[0])
        self.assertIsInstance(ret, HttpResponse)


class GenericQuestionnaireNewTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/sample/new')
        self.request.user = create_new_user()

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_details')
    def test_creates_questionnaire_configuration(
            self, mock_QuestionnaireConfiguration_get_details,
            mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        # with self.assertRaises(AttributeError):
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch('questionnaire.views.get_session_questionnaire')
    def test_calls_get_session_questionnaire(
            self, mock_get_session_questionnaire):
        mock_get_session_questionnaire.return_value = {}
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_get_session_questionnaire.assert_called_once_with('sample')

    @patch('questionnaire.views.QuestionnaireConfiguration')
    @patch('questionnaire.views.clean_questionnaire_data')
    def test_calls_clean_questionnaire_data(
            self, mock_clean_questionnaire_data,
            mock_QuestionnaireConfiguration):
        mock_clean_questionnaire_data.return_value = {"foo": "bar"}, []
        r = self.request
        r.method = 'POST'
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_clean_questionnaire_data.assert_called_once_with(
            {}, mock_QuestionnaireConfiguration())

    @patch.object(messages, 'info')
    def test_adds_message_if_empty(self, mock_messages_info):
        r = self.request
        r.method = 'POST'
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_messages_info.assert_called_once_with(
            r, '[TODO] You cannot submit an empty questionnaire',
            fail_silently=True)

    @patch('questionnaire.views.redirect')
    def test_redirects_to_same_path_if_empty(self, mock_redirect):
        r = self.request
        r.method = 'POST'
        r.path = 'foo'
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_redirect.assert_called_once_with('foo')

    @patch.object(Questionnaire, 'create_new')
    @patch('questionnaire.views.clean_questionnaire_data')
    def test_calls_create_new_questionnaire(
            self, mock_clean_questionnaire_data, mock_create_new):
        r = self.request
        r.method = 'POST'
        mock_clean_questionnaire_data.return_value = {"foo": "bar"}, []
        mock_create_new.return_value = Mock()
        mock_create_new.return_value.id = 1
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_create_new.assert_called_once_with('sample', {})

    @patch('questionnaire.views.clear_session_questionnaire')
    @patch('questionnaire.views.clean_questionnaire_data')
    def test_calls_clear_session_questionnaire(
            self, mock_clean_questionnaire_data,
            mock_clear_session_questionnaire):
        r = self.request
        r.method = 'POST'
        mock_clean_questionnaire_data.return_value = {"foo": "bar"}, []
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_clear_session_questionnaire.assert_called_once_with(
            configuration_code='sample')

    @patch.object(messages, 'success')
    @patch('questionnaire.views.clean_questionnaire_data')
    def test_adds_message(
            self, mock_clean_questionnaire_data, mock_messages_sucess):
        r = self.request
        r.method = 'POST'
        mock_clean_questionnaire_data.return_value = {"foo": "bar"}, []
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_messages_sucess.assert_called_once_with(
            r, '[TODO] The questionnaire was successfully created.',
            fail_silently=True)

    @patch('questionnaire.views.redirect')
    @patch.object(Questionnaire, 'create_new')
    @patch('questionnaire.views.clean_questionnaire_data')
    def test_redirects_to_success_route(
            self, mock_clean_questionnaire_data,
            mock_create_new, mock_redirect):
        r = self.request
        r.method = 'POST'
        mock_clean_questionnaire_data.return_value = {"foo": "bar"}, []
        mock_create_new.return_value = Mock()
        mock_create_new.return_value.id = 1
        generic_questionnaire_new(
            r, *get_valid_new_values()[0], **get_valid_new_values()[1])
        mock_redirect.assert_called_once_with(
            'sample:questionnaire_details', 1)

    @patch('questionnaire.views.get_questionnaire_data_in_single_language')
    def test_calls_get_questionnaire_data_in_single_language(
            self, mock_get_questionnaire_data):
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_get_questionnaire_data.assert_called_once_with({}, 'en')

    @patch.object(QuestionnaireConfiguration, 'get_details')
    def test_calls_get_details(self, mock_get_details):
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_get_details.assert_called_once_with(
            {}, editable=True, edit_step_route='sample:questionnaire_new_step')

    @patch.object(QuestionnaireSection, 'get_details')
    @patch('questionnaire.views.render')
    def test_calls_render(self, mock_render, mock_get_details):
        mock_get_details.return_value = "foo"
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/details.html', {
                'questionnaire_id': None,
                'sections': ["foo"]*get_section_count(),
                'images': [],
                'mode': 'edit',
            })

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        self.assertIsInstance(ret, HttpResponse)


class GenericQuestionnaireDetailsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(
            route_questionnaire_details, args=[1]))

    @patch('questionnaire.views.get_object_or_404')
    def test_calls_get_object_or_404(self, mock_get_object_or_404):
        mock_get_object_or_404.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_get_object_or_404.assert_called_once_with(Questionnaire, pk=1)

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch('questionnaire.views.get_object_or_404')
    @patch.object(QuestionnaireConfiguration, 'get_details')
    def test_creates_questionnaire_configuration(
            self, mock_QuestionnaireConfiguration_get_details,
            mock_get_object_or_404, mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        mock_get_object_or_404.return_value.data = {}
        # with self.assertRaises(Exception):
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch.object(QuestionnaireConfiguration, 'get_details')
    @patch('questionnaire.views.get_object_or_404')
    def test_calls_get_details(self, mock_get_object_or_404, mock_get_details):
        mock_get_object_or_404.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_get_details.assert_called_once_with(
            data={}, questionnaire_object=mock_get_object_or_404.return_value)

    @patch.object(QuestionnaireCategory, 'get_details')
    @patch('questionnaire.views.get_object_or_404')
    @patch('questionnaire.views.render')
    def test_calls_render(
            self, mock_render, mock_get_object_or_404, mock_get_details):
        mock_get_details.return_value = "foo"
        mock_get_object_or_404.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/details.html', {
                'sections': [],
                'questionnaire_id': 1,
                'mode': 'view',
                'images': [],
            })

    @patch('questionnaire.views.get_object_or_404')
    def test_returns_rendered_response(self, mock_get_object_or_404):
        mock_get_object_or_404.return_value.data = {}
        ret = generic_questionnaire_details(
            self.request, *get_valid_details_values())
        self.assertIsInstance(ret, HttpResponse)


class GenericQuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(route_questionnaire_list))

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_list_data')
    @patch.object(QuestionnaireConfiguration, 'get_filter_configuration')
    def test_creates_questionnaire_configuration(
            self, mock_Q_get_filter_configuration,
            mock_QuestionnaireConfiguration_get_list_data,
            mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch('questionnaire.views.get_configuration_query_filter')
    def test_calls_get_configuration_query_filter(
            self, mock_func):
        mock_func.return_value = Q(configurations__code='sample')
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_func.assert_called_once_with('sample', only_current=False)

    # @patch('questionnaire.views.get_active_filters')
    # @patch.object(QuestionnaireConfiguration, '__init__')
    # @patch.object(QuestionnaireConfiguration, 'get_filter_configuration')
    # def test_calls_get_active_filters(
    #         self, mock_Q_get_filter_configuration,
    #         mock_QuestionnaireConfiguration, mock_get_active_filters):
    #     mock_QuestionnaireConfiguration.return_value = None
    #     generic_questionnaire_list(self.request, *get_valid_list_values())
    #     mock_get_active_filters.assert_called_once_with(
    #         mock_QuestionnaireConfiguration.return_value, self.request.GET)

    # @patch.object(QuestionnaireConfiguration, 'get_list_data')
    # def test_calls_get_list_data(self, mock_get_list_data):
    #     f = Questionnaire.objects.none()
    #     generic_questionnaire_list(self.request, *get_valid_list_values())
    #     mock_get_list_data.assert_called_once_with(f)

    @patch.object(QuestionnaireConfiguration, 'get_list_data')
    @patch('questionnaire.views.render')
    def test_calls_render(
            self, mock_render, mock_get_list_data):
        mock_get_list_data.return_value = []
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/list.html', {
                'questionnaire_value_list': [],
                'filter_configuration': (),
                'filter_url': '',
                'active_filters': [],
            })

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_list(
            self.request, *get_valid_list_values())
        self.assertIsInstance(ret, HttpResponse)

    def test_returns_only_template_values_if_no_template(self):
        ret = generic_questionnaire_list(self.request, 'sample', template=None)
        self.assertIsInstance(ret, dict)


class GenericFileUploadTest(TestCase):

    fixtures = ['groups_permissions.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(file_upload_route)
        self.request = self.factory.post(self.url)
        do_log_in(self.client)

    def test_upload_login_required(self):
        self.client.logout()
        res = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_upload_only_post_allowed(self):
        res = self.client.get(self.url, follow=True)
        self.assertEqual(res.status_code, 405)

    def test_handles_post_without_files(self):
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)
        content = json.loads(res.content.decode('utf-8'))
        self.assertFalse(content.get('success'))

    @patch('questionnaire.views.handle_upload')
    def test_calls_handle_upload(self, mock_handle_upload):
        m = Mock()
        m.get_url.return_value = 'foo'
        mock_handle_upload.return_value = m
        with self.assertRaises(Exception):
            with open(valid_file, 'rb') as fp:
                self.client.post(self.url, {'file': fp})
        mock_handle_upload.assert_called_once()

    def test_handles_exception_by_handle_upload(self):
        with open(invalid_file, 'rb') as fp:
            res = self.client.post(self.url, {'file': fp})
        self.assertEqual(res.status_code, 400)
        content = json.loads(res.content.decode('utf-8'))
        self.assertFalse(content.get('success'))

    def test_returns_success_values_if_successful(self):
        with open(valid_file, 'rb') as fp:
            res = self.client.post(self.url, {'file': fp})
        self.assertEqual(res.status_code, 200)
        content = json.loads(res.content.decode('utf-8'))
        self.assertTrue(content.get('success'))
        self.assertIn('url', content)
        self.assertIn('uid', content)
        self.assertNotIn('msg', content)


class GenericFileServeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.file = File.create_new('image/jpeg')
        self.url = reverse(
            file_display_route, args=('display', self.file.uuid))
        self.request = self.factory.get(self.url)

    def test_raises_404_if_invalid_action(self):
        url = reverse(file_display_route, args=('foo', 'uid'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    def test_raises_404_if_file_not_found(self):
        url = reverse(file_display_route, args=('display', 'uid'))
        res = self.client.get(url)
        self.assertEqual(res.status_code, 404)

    @patch('questionnaire.views.retrieve_file')
    def test_calls_retrieve_file(self, mock_retrieve_file):
        self.client.get(self.url)
        mock_retrieve_file.assert_called_once_with(self.file, thumbnail=None)

    @patch('questionnaire.views.retrieve_file')
    def test_calls_retrieve_file_with_thumbnail(self, mock_retrieve_file):
        self.client.get(self.url + '?format=foo')
        mock_retrieve_file.assert_called_once_with(self.file, thumbnail='foo')

    @patch('questionnaire.views.retrieve_file')
    def test_returns_file(self, mock_retrieve_file):
        mock_retrieve_file.return_value = ('file', 'filename')
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    @patch('questionnaire.views.retrieve_file')
    def test_returns_file_download(self, mock_retrieve_file):
        url = reverse(file_display_route, args=('download', self.file.uuid))
        mock_retrieve_file.return_value = ('file', 'filename')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
