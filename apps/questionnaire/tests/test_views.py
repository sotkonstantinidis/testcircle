import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.client import RequestFactory
from unittest.mock import patch, Mock, MagicMock

from accounts.tests.test_models import create_new_user
from configuration.configuration import (
    QuestionnaireConfiguration,
)
from qcat.tests import TestCase
from questionnaire.models import File, Questionnaire
from questionnaire.views import (
    generic_file_upload,
    generic_questionnaire_details,
    generic_questionnaire_link_search,
    generic_questionnaire_list,
    GenericQuestionnaireView,
    GenericQuestionnaireStepView)
from questionnaire.tests.test_view_utils import get_valid_pagination_parameters
from sample.tests.test_views import (
    get_valid_details_values,
    get_valid_list_values,
    route_questionnaire_details,
    route_questionnaire_list,
    route_questionnaire_link_search,
)

file_upload_route = 'file_upload'
file_display_route = 'file_serve'
valid_file = 'static/assets/img/img01.jpg'
invalid_file = 'bower.json'  # Needs to exist but not valid file type


class GenericQuestionnaireLinkSearchTest(TestCase):

    fixtures = [
        'sample_global_key_values.json', 'sample.json',
        'sample_questionnaires.json']

    @patch('questionnaire.views.get_configuration')
    def test_calls_get_configuration(self, mock_get_configuration):
        mock = Mock()
        mock.get_name_keywords.return_value = None, None
        mock_get_configuration.return_value = mock
        generic_questionnaire_link_search(Mock(), 'sample')
        mock_get_configuration.assert_called_once_with('sample')

    @patch('questionnaire.views.get_configuration')
    @patch('questionnaire.views.query_questionnaires_for_link')
    def test_calls_query_questionnaires_for_link(
            self, mock_query, mock_get_configuration):
        mock_get_configuration.get_list_data.return_value = []
        mock_query.return_value = 0, []
        mock_request = Mock()
        generic_questionnaire_link_search(mock_request, 'sample')
        mock_query.assert_called_once_with(
            mock_request, mock_get_configuration(), mock_request.GET.get())

    def test_returns_empty_if_no_q(self):
        req = RequestFactory().get(reverse(route_questionnaire_link_search))
        ret = generic_questionnaire_link_search(req, 'sample')
        j = json.loads(ret.content.decode('utf-8'))
        self.assertEqual(j, {})

    def test_returns_empty_if_no_results(self):
        req = RequestFactory().get(reverse(route_questionnaire_link_search))
        req.GET = {'q': 'foo'}
        user = Mock()
        user.is_authenticated.return_value = False
        req.user = user
        ret = generic_questionnaire_link_search(req, 'sample')
        j = json.loads(ret.content.decode('utf-8'))
        self.assertEqual(j, {"total": 0, "data": []})

    def test_returns_results(self):
        req = RequestFactory().get(reverse(route_questionnaire_link_search))
        req.GET = {'q': 'key'}
        user = Mock()
        user.is_authenticated.return_value = False
        req.user = user
        ret = generic_questionnaire_link_search(req, 'sample')
        j = json.loads(ret.content.decode('utf-8'))
        self.assertEqual(j.get('total'), 2)
        data = j.get('data')
        self.assertEqual(len(data), 2)
        self.assertEqual(len(data[0]), 5)
        self.assertEqual(data[0].get('code'), 'sample_1')
        self.assertIn('display', data[0])
        self.assertEqual(data[0].get('id'), 1)
        self.assertEqual(data[0].get('name'), 'Sample Key 1a')
        self.assertEqual(data[0].get('value'), 1)
        self.assertEqual(len(data[1]), 5)
        self.assertEqual(data[1].get('code'), 'sample_2')
        self.assertIn('display', data[1])
        self.assertEqual(data[1].get('id'), 2)
        self.assertEqual(data[1].get('name'), 'Sample Key 1b')
        self.assertEqual(data[1].get('value'), 2)


class GenericQuestionnaireNewStepTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'sample_global_key_values.json',
        'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/sample/new/cat_1')
        self.request.user = create_new_user()
        self.request.session = {}

    # @patch('questionnaire.views.get_configuration')
    # def test_calls_get_configuration(self, mock_get_configuration):
    #     mock_get_configuration.return_value.get_category.return_value.\
    #         get_form.return_value = {}, []
    #     generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     mock_get_configuration.assert_called_once_with('sample')
    #
    # @patch.object(QuestionnaireConfiguration, 'get_category')
    # def test_gets_category(self, mock_get_category):
    #     mock_get_category.return_value = None
    #     with self.assertRaises(Http404):
    #         generic_questionnaire_new_step(
    #             self.request, 'cat_1', 'sample', 'template', 'route')
    #     mock_get_category.assert_called_once_with('cat_1')
    #
    # @patch('questionnaire.views.get_session_questionnaire')
    # def test_calls_get_session_questionnaire(
    #         self, mock_get_session_questionnaire):
    #     mock_get_session_questionnaire.return_value = {}
    #     generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     mock_get_session_questionnaire.assert_called_once_with(
    #         self.request, 'sample', None)
    #
    # @patch('questionnaire.views.get_questionnaire_data_for_translation_form')
    # def test_calls_get_questionnaire_data_for_translation_form(
    #         self, mock_get_questionnaire_data):
    #     generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     mock_get_questionnaire_data.assert_called_once_with({}, 'en', None)
    #
    # @patch.object(QuestionnaireCategory, 'get_form')
    # def test_calls_category_get_form(self, mock_get_form):
    #     mock_get_form.return_value = {}, []
    #     generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     mock_get_form.assert_called_once_with(
    #         post_data=None, show_translation=False, initial_data={},
    #         edit_mode='edit', edited_questiongroups=[], initial_links={})
    #
    # @patch.object(messages, 'success')
    # @patch.object(QuestionnaireCategory, 'get_form')
    # @patch('questionnaire.views.save_session_questionnaire')
    # def test_form_submission_saves_form(
    #         self, mock_save_session_questionnaire, mock_get_form,
    #         mock_messages):
    #     mock_get_form.return_value = None, []
    #     r = self.request
    #     r.method = 'POST'
    #     generic_questionnaire_new_step(
    #         r, *get_valid_new_step_values()[0])
    #     mock_save_session_questionnaire.assert_called_once_with(
    #         self.request, 'sample', None, questionnaire_data={},
    #         questionnaire_links={}, edited_questiongroups=[])
    #
    # @patch.object(QuestionnaireCategory, 'get_form')
    # @patch('questionnaire.views.render')
    # def test_calls_render(self, mock_render, mock_get_form):
    #     mock_get_form.return_value = {}, []
    #     generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     mock_render.assert_called_once_with(
    #         self.request, 'form/category.html', {
    #             'subcategories': [],
    #             'config': {},
    #             'title': 'QCAT Form',
    #             'overview_url': '/en/sample/edit/new/#cat_0',
    #             'valid': True,
    #             'configuration_name': 'sample',
    #             'edit_mode': 'edit',
    #             'view_url': '',
    #             'content_subcategories_count': 0,
    #             'toc_content': [],
    #         })
    #
    # def test_returns_rendered_response(self):
    #     ret = generic_questionnaire_new_step(
    #         self.request, *get_valid_new_step_values()[0])
    #     self.assertIsInstance(ret, HttpResponse)


@patch('questionnaire.views.render')
class GenericQuestionnaireDetailsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(
            route_questionnaire_details, args=[1]))
        self.request.user = Mock()
        self.request.user.is_authenticated.return_value = False

    @patch('questionnaire.views.query_questionnaire')
    def test_calls_query_questionnaire(
            self, mock_query_questionnaire, mock_render):
        mock_query_questionnaire.return_value.first.return_value = None
        with self.assertRaises(Http404):
            generic_questionnaire_details(
                self.request, *get_valid_details_values())
        mock_query_questionnaire.assert_called_once_with(self.request, 'foo')

    @patch('questionnaire.views.query_questionnaire')
    @patch('questionnaire.views.get_configuration')
    def test_calls_get_configuration(
            self, mock_get_configuration, mock_query_questionnaire,
            mock_render):
        mock_query_questionnaire.return_value.first.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_get_configuration.assert_called_once_with('sample')

    @patch('questionnaire.views.get_questionnaire_data_in_single_language')
    @patch('questionnaire.views.query_questionnaire')
    @patch('questionnaire.views.get_configuration')
    def test_calls_get_questionnaire_data_in_single_language(
            self, mock_conf, mock_query_questionnaire,
            mock_get_q_data_in_single_lang, mock_render):
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_q = mock_query_questionnaire.return_value.first.return_value
        mock_get_q_data_in_single_lang.assert_called_once_with(
            mock_q.data, 'en', original_locale=mock_q.original_locale)

    @patch('questionnaire.views.handle_review_actions')
    @patch('questionnaire.views.redirect')
    @patch('questionnaire.views.get_questionnaire_data_in_single_language')
    @patch('questionnaire.views.query_questionnaire')
    @patch('questionnaire.views.get_configuration')
    def test_calls_handle_review_actions_if_post_values(
            self, mock_conf, mock_query_questionnaire,
            mock_get_q_data_in_single_lang, mock_redirect,
            mock_handle_review_actions, mock_render):
        self.request.method = 'POST'
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_handle_review_actions.assert_called_once_with(
            self.request,
            mock_query_questionnaire.return_value.first.return_value, 'sample')

    @patch('questionnaire.views.redirect')
    @patch('questionnaire.views.get_questionnaire_data_in_single_language')
    @patch('questionnaire.views.query_questionnaire')
    @patch('questionnaire.views.get_configuration')
    def test_calls_redirect_if_post_values(
            self, mock_conf, mock_query_questionnaire,
            mock_get_q_data_in_single_lang, mock_redirect, mock_render):
        self.request.method = 'POST'
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_redirect.assert_called_once_with(
            'sample:questionnaire_details',
            mock_query_questionnaire.return_value.first.return_value.code)

    @patch('questionnaire.views.get_query_status_filter')
    @patch.object(QuestionnaireConfiguration, 'get_details')
    @patch('questionnaire.views.query_questionnaire')
    def test_calls_get_details(
            self, mock_query_questionnaire, mock_get_details,
            mock_get_query_status_filter, mock_render):
        mock_query_questionnaire.return_value.first.return_value.data = {}
        self.request.user.is_authenticated.return_value = True
        generic_questionnaire_details(self.request, *get_valid_details_values())
        self.assertTrue(mock_get_details.called)

    @patch('questionnaire.views.get_configuration')
    @patch('questionnaire.views.query_questionnaire')
    def test_calls_get_image_data(
            self, mock_query_questionnaire, mock_conf, mock_render):
        mock_query_questionnaire.return_value.first.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_conf.return_value.get_image_data.assert_called_once_with({})

    @patch('questionnaire.views.get_configuration')
    @patch('questionnaire.views.get_list_values')
    @patch('questionnaire.views.query_questionnaire')
    def test_calls_get_list_values(
            self, mock_query_questionnaire, mock_get_list_values, mock_conf,
            mock_render):
        q = Mock()
        q.data = {}
        link = Mock()
        q.links.filter.return_value = [link]
        q.members.all.return_value = []
        mock_query_questionnaire.return_value.first.return_value = q
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_get_list_values.assert_called_once_with(
            questionnaire_objects=[link], with_links=False,
            configuration_code=link.configurations.first().code)

    @patch('questionnaire.views.get_configuration')
    @patch('questionnaire.views.query_questionnaire')
    def test_calls_render(
            self, mock_query_questionnaire, mock_conf, mock_render):
        mock_q_obj = mock_query_questionnaire.return_value.first.return_value
        mock_q_obj.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        img = mock_conf.return_value.get_image_data.return_value
        mock_render.assert_called_once_with(
            self.request, 'questionnaire/details.html', {
                'sections': mock_conf.return_value.get_details.return_value,
                'questionnaire_identifier': 'foo',
                'images': img.get.return_value,
                'permissions': mock_q_obj.get_roles_permissions.return_value.permissions,
                'view_mode': 'view',
                'toc_content': mock_conf.return_value.get_toc_data.return_value,
                'base_template': 'sample/base.html',
                'review_config': {}
            })


@patch('questionnaire.views.render')
@patch('questionnaire.views.advanced_search')
class GenericQuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(route_questionnaire_list))
        self.request.user = Mock()
        self.request.user.get_all_permissions.return_value = []

    @patch('questionnaire.views.get_configuration')
    def test_calls_get_configuration(
            self, mock_get_configuration, mock_advanced_search, mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_configuration.assert_called_once_with('sample')

    @patch('questionnaire.views.get_active_filters')
    @patch('questionnaire.views.get_configuration')
    def test_calls_get_active_filters(
            self, mock_conf, mock_get_active_filters, mock_advanced_search,
            mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_active_filters.assert_called_once_with(
            [mock_conf.return_value], self.request.GET)

    @patch('questionnaire.views.get_limit_parameter')
    def test_calls_get_limit_parameter(
            self, mock_get_limit_parameter, mock_advanced_search, mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_limit_parameter.assert_called_once_with(self.request)

    @patch('questionnaire.views.get_page_parameter')
    def test_calls_get_page_parameter(
            self, mock_get_page_parameter, mock_advanced_search, mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_page_parameter.assert_called_once_with(self.request)

    @patch('questionnaire.views.get_list_values')
    def test_db_query_calls_get_list_values(
            self, mock_get_list_values, mock_advanced_search, mock_render):
        self.request.user = Mock()
        self.request.user.is_authenticated.return_value = False
        generic_questionnaire_list(self.request, 'sample')
        self.assertEqual(mock_get_list_values.call_count, 1)

    @patch('questionnaire.views.get_configuration_index_filter')
    def test_es_calls_get_configuration_index_filter(
            self, mock_get_configuration_index_filter, mock_advanced_search,
            mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        self.assertEqual(mock_get_configuration_index_filter.call_count, 2)
        mock_get_configuration_index_filter.assert_any_call(
            'sample', only_current=False, query_param_filter=())
        mock_get_configuration_index_filter.assert_any_call('sample')

    def test_es_calls_advanced_search(self, mock_advanced_search, mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_advanced_search.assert_called_once_with(
            filter_params=[], query_string='', configuration_codes=['sample'],
            limit=10, offset=0)

    @patch('questionnaire.views.get_pagination_parameters')
    @patch('questionnaire.views.get_list_values')
    @patch('questionnaire.views.get_paginator')
    @patch('questionnaire.views.ESPagination')
    def test_es_creates_esPagination(
            self, mock_ESPagination, mock_get_paginator, mock_get_list_values,
            mock_get_pagination_parameters, mock_advanced_search, mock_render):
        mock_get_paginator.return_value = None, None
        generic_questionnaire_list(self.request, *get_valid_list_values())
        self.assertEqual(mock_ESPagination.call_count, 1)

    @patch('questionnaire.views.get_list_values')
    def test_es_calls_get_list_values(
            self, mock_get_list_values, mock_advanced_search, mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        self.assertEqual(mock_get_list_values.call_count, 1)

    @patch.object(QuestionnaireConfiguration, 'get_filter_configuration')
    def test_calls_get_filter_configuration(
            self, mock_get_filter_configuration, mock_advanced_search,
            mock_render):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_filter_configuration.assert_called_once_with()

    @patch('questionnaire.views.get_list_values')
    @patch('questionnaire.views.get_paginator')
    @patch('questionnaire.views.get_pagination_parameters')
    def test_calls_get_pagination_parameters(
            self, mock_get_pagination_parameters, mock_get_paginator,
            mock_get_list_values, mock_advanced_search, mock_render):
        mock_get_paginator.return_value = None, None
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_pagination_parameters.assert_called_once_with(
            self.request, None, None)

    @patch('questionnaire.views.get_filter_configuration')
    def test_calls_render(
            self, mock_filter_conf, mock_advanced_search, mock_render):
        mock_advanced_search.return_value = {}
        generic_questionnaire_list(self.request, *get_valid_list_values())
        ret = {
            'list_values': [],
            'filter_configuration': mock_filter_conf.return_value,
            'filter_url': '',
            'active_filters': [],
        }
        ret.update(get_valid_pagination_parameters())
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/list.html', ret)

    def test_returns_only_template_values_if_no_template(
            self, mock_advanced_search, mock_render):
        ret = generic_questionnaire_list(self.request, 'sample', template=None)
        self.assertIsInstance(ret, dict)


class GenericFileUploadTest(TestCase):

    fixtures = ['groups_permissions.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(file_upload_route)
        self.request = self.factory.post(self.url)
        self.request.user = create_new_user()
        self.request.session = {}
        self.mock_request = Mock()
        self.mock_request.method = 'POST'
        self.mock_request.session = {}
        self.mock_request.user = self.request.user
        self.mock_request.FILES.getlist.return_value = [Mock()]

    def test_upload_login_required(self):
        self.client.logout()
        res = self.client.post(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_upload_only_post_allowed(self):
        res = generic_file_upload(self.request)
        self.assertEqual(res.status_code, 400)

    def test_handles_post_without_files(self):
        res = generic_file_upload(self.request)
        self.assertEqual(res.status_code, 400)
        content = json.loads(res.content.decode('utf-8'))
        self.assertFalse(content.get('success'))

    @patch.object(File, 'get_data')
    @patch.object(File, 'handle_upload')
    def test_calls_handle_upload(self, mock_handle_upload, mock_get_data):
        mock_get_data.return_value = {}
        generic_file_upload(self.mock_request)
        self.assertTrue(mock_handle_upload.called)

    def test_handles_exception_by_handle_upload(self):
        res = generic_file_upload(self.request)
        self.assertEqual(res.status_code, 400)
        content = json.loads(res.content.decode('utf-8'))
        self.assertFalse(content.get('success'))

    @patch.object(File, 'get_data')
    @patch.object(File, 'handle_upload')
    def test_calls_get_data(self, mock_handle_upload, mock_get_data):
        mock_get_data.return_value = {}
        generic_file_upload(self.mock_request)
        mock_get_data.assert_called_once_with(
            file_object=mock_handle_upload.return_value)


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

    @patch.object(File, 'get_data')
    def test_calls_get_data(self, mock_get_data):
        self.client.get(self.url)
        mock_get_data.assert_called_once_with(file_object=self.file)

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


class GenericQuestionnaireViewTest(TestCase):
    fixtures = ['sample_global_key_values.json', 'sample.json', 'sample_questionnaires.json']

    def setUp(self):
        view = GenericQuestionnaireView(url_namespace='sample')
        self.request = RequestFactory().get('/en/sample/view/app_1')
        self.request.user = create_new_user()
        self.request.session = dict()
        self.request._messages = MagicMock()
        self.view = self.setup_view(view, self.request, identifier='sample_1')

    def test_get_obj_raises_404(self):
        view = self.setup_view(self.view, self.request, identifier='404')
        with self.assertRaises(Http404):
            view.get_object()

    def test_get_obj(self):
        self.view.get(self.request)
        self.assertEqual(self.view.object.code, 'sample_1')

    def test_has_object(self):
        self.assertTrue(self.view.has_object)

    def test_has_no_object(self):
        view = self.setup_view(self.view, self.request, identifier='new')
        self.assertFalse(view.has_object)

    def test_new_questionnaire_has_no_release(self):
        view = self.setup_view(self.view, self.request, identifier='new')
        self.assertFalse(view.has_release())

    def test_existing_questionnaire_has_release(self):
        self.view.get(self.request)
        self.assertTrue(self.view.has_release())

    def test_get_template(self):
        self.assertEqual(self.view.get_template_names(), 'questionnaire/details.html')

    def test_configuration_code(self):
        self.view.get(self.request)
        self.assertIsInstance(self.view.questionnaire_configuration, QuestionnaireConfiguration)
        self.assertEqual(self.view.questionnaire_configuration.keyword, 'sample')

    def test_get_detail_url(self):
        self.view.get(self.request)
        self.assertEqual(self.view.get_detail_url(''), '/en/sample/view/sample_1/#top')

    def test_get_steps(self):
        self.assertListEqual(self.view.get_steps(), ['cat_0', 'cat_1', 'cat_2', 'cat_3', 'cat_4', 'cat_5'])

    def test_require_user(self):
        self.request.user = AnonymousUser()
        self.assertEqual(self.view.dispatch(self.request).url, '/en/accounts/login/?next=/en/sample/view/app_1')

    def test_force_login(self):
        self.view.dispatch(self.request)
        self.assertTrue(self.request.session[settings.ACCOUNTS_ENFORCE_LOGIN_NAME])


class GenericQuestionnaireStepViewTest(TestCase):
    fixtures = ['sample_global_key_values.json', 'sample.json', 'sample_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        view = GenericQuestionnaireStepView(url_namespace='sample')
        self.request = self.factory.get('/en/sample/view/app_1/cat_0/')
        self.request.user = create_new_user()
        self.request._messages = MagicMock()
        self.view = self.setup_view(view, self.request, identifier='sample_1', step='cat_0')

    def test_valid_step(self):
        self.view.get(self.request)
        self.assertEqual(self.view.category.keyword, 'cat_0')

    def test_invalid_step(self):
        view = self.setup_view(self.view, self.request, identifier='sample_1', step='cat_666')
        with self.assertRaises(Http404):
            view.get(self.request)

    @patch.object(Questionnaire, 'lock_questionnaire')
    def test_lock_questionnaire(self, lock_questionnaire):
        self.view.get(self.request)
        lock_questionnaire.assert_called_with('sample_1', self.request.user)

    @patch.object(Questionnaire, 'create_new')
    @patch.object(Questionnaire, 'unlock_questionnaire')
    def test_unlock_questionnaire(self, unlock_questionnaire, create_new):
        obj = self.view.get_object()
        self.view.object = obj
        create_new.return_value = obj
        self.view.form_valid({})
        unlock_questionnaire.assert_called_once_with()

    @patch.object(Questionnaire, 'create_new')
    @patch.object(GenericQuestionnaireStepView, 'get_success_url_next_section')
    @patch('questionnaire.signals.change_questionnaire_data.send')
    def test_next_section_route(self, mock_change_data,
                                get_success_url_next_section, create_new):
        request = self.factory.post('/en/sample/view/app_1/cat_0/', identifier='sample_1', step='cat_0')
        request.user = self.request.user
        request._messages = MagicMock()
        request.POST['goto-next-section'] = 'true'
        view = self.setup_view(self.view, request, step='cat_0')
        view.object = MagicMock()
        view.object.code = 'foo'
        create_new.return_value = view.object
        view.form_valid({})
        get_success_url_next_section.assert_called_with('foo', 'cat_0')

    @patch.object(GenericQuestionnaireStepView, 'get_steps')
    def test_next_section_url(self, get_steps):
        get_steps.return_value = ['foo', 'bar']
        response = self.view.get_success_url_next_section('sample_1', 'foo')
        self.assertEqual(response.url, '/en/sample/edit/sample_1/bar/')

    @patch.object(GenericQuestionnaireStepView, 'get_steps')
    def test_next_section_url_no_exception(self, get_steps):
        get_steps.return_value = ['foo', 'bar', 'baz']
        response = self.view.get_success_url_next_section('sample_1', 'abc')
        self.assertIsNone(response)

    @patch.object(Questionnaire, 'create_new')
    @patch('questionnaire.signals.change_questionnaire_data.send')
    def test_success_url(self, mock_change_data, create_new):
        request = self.factory.post('/en/sample/view/app_1/cat_0/', identifier='sample_1', step='cat_0')
        request.user = self.request.user
        request._messages = MagicMock()

        view = self.setup_view(self.view, request, step='cat_0')
        view.object = MagicMock()
        view.object.code = 'bar'
        create_new.return_value = view.object
        response = view.form_valid({})
        self.assertEqual(response.url, "/en/sample/edit/bar/#cat_0")

    def test_get_locale_info(self):
        self.view.set_attributes()
        original_locale, show_translation = self.view.get_locale_info()
        self.assertIsNotNone(original_locale)
        self.assertFalse(show_translation)
