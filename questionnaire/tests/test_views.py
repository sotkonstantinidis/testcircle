from django.http import Http404
from django.http.response import HttpResponse
from django.test.client import RequestFactory
from unittest.mock import patch

from configuration.configuration import (
    QuestionnaireConfiguration,
    QuestionnaireCategory,
)
from qcat.tests import TestCase
from qcat.utils import session_store
from questionnaire.views import (
    generic_questionnaire_new_step,
    generic_questionnaire_new,
)
from unccd.tests.test_views import (
    get_valid_new_step_values,
    get_valid_new_values,
)


class GenericQuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/unccd/new/cat_1')
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
                self.request, 'cat_1', 'unccd', 'template', 'route')
        mock_QuestionnaireConfiguration.assert_called_once_with('unccd')

    @patch.object(QuestionnaireConfiguration, 'get_category')
    def test_gets_category(self, mock_get_category):
        mock_get_category.return_value = None
        with self.assertRaises(Http404):
            generic_questionnaire_new_step(
                self.request, 'cat_1', 'unccd', 'template', 'route')
        mock_get_category.assert_called_once_with('cat_1')

    @patch('questionnaire.views.get_session_questionnaire')
    def test_calls_get_session_questionnaire(
            self, mock_get_session_questionnaire):
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
        mock_get_session_questionnaire.assert_called_once_with()

    @patch.object(QuestionnaireCategory, 'get_form')
    def test_calls_category_get_form(self, mock_get_form):
        mock_get_form.return_value = None, None
        generic_questionnaire_new_step(
            self.request, *get_valid_new_step_values())
        mock_get_form.assert_called_once_with(None, initial_data={})

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
            self.request, 'unccd/questionnaire/new_step.html', {
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
        self.request = self.factory.get('/unccd/new')

    @patch.object(QuestionnaireConfiguration, '__init__')
    @patch.object(QuestionnaireConfiguration, 'render_readonly_form')
    def test_creates_questionnaire_configuration(
            self, mock_QuestionnaireConfiguration_get_category,
            mock_QuestionnaireConfiguration):
        mock_QuestionnaireConfiguration.return_value = None
        generic_questionnaire_new(self.request, *get_valid_new_values())
        mock_QuestionnaireConfiguration.assert_called_once_with('unccd')

    @patch('questionnaire.views.get_session_questionnaire')
    def test_calls_get_session_questionnaire(
            self, mock_get_session_questionnaire):
        generic_questionnaire_new(self.request, *get_valid_new_values())
        mock_get_session_questionnaire.assert_called_once_with()

    @patch.object(QuestionnaireConfiguration, 'render_readonly_form')
    def test_calls_render_readonly_form(self, mock_render_readonly_form):
        generic_questionnaire_new(self.request, *get_valid_new_values())
        mock_render_readonly_form.assert_called_once_with({})

    @patch.object(QuestionnaireCategory, 'render_readonly_form')
    @patch('questionnaire.views.render')
    def test_calls_render(self, mock_render, mock_render_readonly_form):
        mock_render_readonly_form.return_value = "foo"
        generic_questionnaire_new(
            self.request, *get_valid_new_values())
        mock_render.assert_called_once_with(
            self.request, 'unccd/questionnaire/new.html', {
                'categories': ["foo", "foo"]})

    def test_returns_rendered_response(self):
        ret = generic_questionnaire_new(
            self.request, *get_valid_new_values())
        self.assertIsInstance(ret, HttpResponse)
