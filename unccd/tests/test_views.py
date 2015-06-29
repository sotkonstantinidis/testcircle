import json
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from unittest.mock import patch

from accounts.tests.test_authentication import (
    create_new_user,
)
from configuration.configuration import QuestionnaireConfiguration
from qcat.tests import TestCase
from unccd.views import (
    home,
    questionnaire_details,
    questionnaire_list,
    questionnaire_list_partial,
    questionnaire_new,
    questionnaire_new_step,
)

route_home = 'unccd:home'
route_questionnaire_details = 'unccd:questionnaire_details'
route_questionnaire_list = 'unccd:questionnaire_list'
route_questionnaire_list_partial = 'unccd:questionnaire_list_partial'
route_questionnaire_new = 'unccd:questionnaire_new'
route_questionnaire_new_step = 'unccd:questionnaire_new_step'


def get_valid_new_step_values():
    args = (get_categories()[0][0], 'unccd', 'unccd')
    kwargs = {'page_title': 'UNCCD Form'}
    return args, kwargs


def get_valid_new_values():
    args = ('unccd', 'unccd/questionnaire/details.html', 'unccd')
    kwargs = {'questionnaire_id': None}
    return args, kwargs


def get_valid_details_values():
    return (1, 'unccd', 'unccd/questionnaire/details.html')


def get_valid_list_values():
    return ('unccd', 'unccd/questionnaire/list.html')


def get_category_count():
    return len(get_categories())


def get_categories():
    return (
        ('unccd_0_general_information', 'General Information'),
        ('unccd_0_classification', 'Classification'),
        ('unccd_1_context', 'Section 1: ...'),
        ('unccd_2_problems_addressed', 'Section 2: ...'),
        ('unccd_3_activities', 'Section 3: ...'),
        ('unccd_4_actors_involved', 'Section 4: ...'),
        ('unccd_5_impact', 'Section 5: ...'),
        ('unccd_6_adoption_replicability', 'Section 6: ...'),
        ('unccd_7_lessons_learned', 'Section 7: ...'),
    )


class UnccdHomeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_home)

    @patch.object(QuestionnaireConfiguration, '__init__')
    def test_creates_questionnaire_configuration(self, mock_Q_Conf):
        mock_Q_Conf.return_value = None
        with self.assertRaises(AttributeError):
            self.client.get(self.url)
        mock_Q_Conf.assert_called_once_with('unccd')

    @patch('unccd.views.generic_questionnaire_list')
    @patch('unccd.views.messages')
    def test_calls_generic_questionnaire_list(
            self, mock_messages, mock_questionnaire_list):
        request = self.factory.get(self.url)
        home(request)
        mock_questionnaire_list.assert_called_once_with(
            request, 'unccd', template=None, only_current=True, limit=3,
            db_query=True)

    def test_renders_correct_template(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'unccd/home.html')
        self.assertEqual(res.status_code, 200)


class QuestionnaireNewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_new)

    def test_questionnaire_new_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_questionnaire_new_test_renders_correct_template(self):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        res = questionnaire_new(request)
        self.assertTemplateUsed(res, 'unccd/questionnaire/details.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new')
    def test_calls_generic_function(self, mock_questionnaire_new):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new(request)
        mock_questionnaire_new.assert_called_once_with(
            request, *get_valid_new_values()[0], **get_valid_new_values()[1])


class QuestionnaireNewStepTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'global_key_values.json', 'unccd.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(
            route_questionnaire_new_step, args=[get_categories()[0][0]])

    def test_questionnaire_new_step_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_renders_correct_template(self):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        res = questionnaire_new_step(request, step=get_categories()[0][0])
        self.assertTemplateUsed(res, 'form/category.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new_step')
    def test_calls_generic_function(self, mock_questionnaire_new_step):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new_step(request, get_categories()[0][0])
        mock_questionnaire_new_step.assert_called_once_with(
            request, *get_valid_new_step_values()[0],
            **get_valid_new_step_values()[1])


class QuestionnaireDetailsTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'unccd.json', 'unccd_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_details, args=[201])

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/details.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_details')
    def test_calls_generic_function(self, mock_questionnaire_details):
        request = self.factory.get(self.url)
        questionnaire_details(request, 1)
        mock_questionnaire_details.assert_called_once_with(
            request, *get_valid_details_values())


class QuestionnaireListPartialTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_list_partial)

    @patch('unccd.views.generic_questionnaire_list')
    def test_calls_generic_questionnaire_list(self, mock_questionnaire_list):
        request = self.factory.get(self.url)
        questionnaire_list_partial(request)
        mock_questionnaire_list.assert_called_once_with(
            request, 'unccd', template=None)

    @patch('unccd.views.render_to_string')
    @patch('unccd.views.generic_questionnaire_list')
    def test_calls_render_to_string_with_list_template(
            self, mock_questionnaire_list, mock_render_to_string):
        mock_questionnaire_list.return_value = {
            'list_values': 'foo',
            'active_filters': 'bar'
        }
        mock_render_to_string.return_value = ''
        self.client.get(self.url)
        mock_render_to_string.assert_any_call(
            'unccd/questionnaire/partial/list.html',
            {'list_values': 'foo'})

    @patch('unccd.views.render_to_string')
    @patch('unccd.views.generic_questionnaire_list')
    def test_calls_render_to_string_with_active_filters(
            self, mock_questionnaire_list, mock_render_to_string):
        mock_questionnaire_list.return_value = {
            'list_values': 'foo',
            'active_filters': 'bar'
        }
        mock_render_to_string.return_value = ''
        self.client.get(self.url)
        mock_render_to_string.assert_any_call(
            'active_filters.html', {'active_filters': 'bar'})

    def test_renders_json_response(self):
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        content = json.loads(res.content.decode('utf-8'))
        self.assertEqual(len(content), 3)
        self.assertTrue(content.get('success'))
        self.assertIn('list', content)
        self.assertIn('active_filters', content)


class QuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_list)

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/list.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_list')
    def test_calls_generic_function(self, mock_questionnaire_list):
        request = self.factory.get(self.url)
        questionnaire_list(request)
        mock_questionnaire_list.assert_called_once_with(
            request, 'unccd', template='unccd/questionnaire/list.html',
            filter_url='/en/unccd/list_partial/')
