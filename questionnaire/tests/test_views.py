from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.response import HttpResponse
from django.test.client import RequestFactory
from unittest.mock import patch, Mock

from accounts.tests.test_authentication import (
    create_new_user,
)
from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
)
from qcat.tests import TestCase
from qcat.utils import session_store
from questionnaire.models import Questionnaire
from questionnaire.views import (
    generic_questionnaire_details,
    generic_questionnaire_list,
    generic_questionnaire_new,
    generic_questionnaire_new_step,
)
from sample.tests.test_views import (
    get_categories,
    get_category_count,
    get_valid_new_step_values,
    get_valid_new_values,
    get_valid_details_values,
    get_valid_list_values,
    questionnaire_route_details,
    questionnaire_route_list,
)


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
            self.request, *get_valid_new_step_values())
        mock_get_session_questionnaire.assert_called_once_with()

    @patch('questionnaire.views.get_questionnaire_data_for_translation_form')
    def test_calls_get_questionnaire_data_for_translation_form(
            self, mock_get_questionnaire_data):
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
        mock_get_questionnaire_data.assert_called_once_with({}, 'en', None)

    @patch.object(QuestionnaireCategory, 'get_form')
    def test_calls_category_get_form(self, mock_get_form):
        mock_get_form.return_value = None, None
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
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
            r, *get_valid_new_step_values())
        mock_save_session_questionnaire.assert_called_once_with({})

    @patch.object(QuestionnaireCategory, 'get_form')
    @patch('questionnaire.views.render')
    def test_calls_render(self, mock_render, mock_get_form):
        mock_get_form.return_value = "foo", "bar"
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/new_step.html', {
                'category_formsets': "bar",
                'category_config': "foo"})

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
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
        with self.assertRaises(AttributeError):
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
        mock_get_session_questionnaire.assert_called_once_with()

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
        mock_clear_session_questionnaire.assert_called_once_with()

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
            'sample_questionnaire_details', 1)

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
        mock_get_details.assert_called_once_with({}, editable=True)

    @patch.object(QuestionnaireCategory, 'get_details')
    @patch('questionnaire.views.render')
    def test_calls_render(self, mock_render, mock_get_details):
        mock_get_details.return_value = "foo"
        generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/new.html', {
                'questionnaire_id': None,
                'category_names': get_categories(),
                'categories': ["foo"]*get_category_count()})

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_new(
            self.request, *get_valid_new_values()[0],
            **get_valid_new_values()[1])
        self.assertIsInstance(ret, HttpResponse)


class GenericQuestionnaireDetailsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(
            questionnaire_route_details, args=[1]))

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
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch.object(QuestionnaireConfiguration, 'get_details')
    @patch('questionnaire.views.get_object_or_404')
    def test_calls_get_details(self, mock_get_object_or_404, mock_get_details):
        mock_get_object_or_404.return_value.data = {}
        generic_questionnaire_details(
            self.request, *get_valid_details_values())
        mock_get_details.assert_called_once_with({})

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
                'categories': [], 'questionnaire_id': 1})

    @patch('questionnaire.views.get_object_or_404')
    def test_returns_rendered_response(self, mock_get_object_or_404):
        mock_get_object_or_404.return_value.data = {}
        ret = generic_questionnaire_details(
            self.request, *get_valid_details_values())
        self.assertIsInstance(ret, HttpResponse)


class GenericQuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get(reverse(questionnaire_route_list))

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'get_list_data')
    def test_creates_questionnaire_configuration(
            self, mock_QuestionnaireConfiguration_get_list_data,
            mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_QuestionnaireConfiguration.assert_called_once_with('sample')

    @patch.object(QuestionnaireConfiguration, 'get_list_data')
    def test_calls_get_list(self, mock_get_list_data):
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_get_list_data.assert_called_once_with(
            [], questionnaire_route_details, 'en')

    @patch.object(QuestionnaireConfiguration, 'get_list_data')
    @patch('questionnaire.views.render')
    def test_calls_render(
            self, mock_render, mock_get_list_data):
        mock_get_list_data.return_value = (("foo",),)
        generic_questionnaire_list(self.request, *get_valid_list_values())
        mock_render.assert_called_once_with(
            self.request, 'sample/questionnaire/list.html', {
                'list_data': (), 'list_header': ('foo',)})

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_list(
            self.request, *get_valid_list_values())
        self.assertIsInstance(ret, HttpResponse)
