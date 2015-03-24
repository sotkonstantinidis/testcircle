from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from unittest.mock import patch

from accounts.tests.test_authentication import (
    create_new_user,
    do_log_in,
)
from qcat.tests import TestCase
from wocat.views import (
    questionnaire_details,
    questionnaire_list,
    questionnaire_new,
    questionnaire_new_step,
)


route_home = 'wocat:home'
route_questionnaire_new = 'wocat:questionnaire_new'
route_questionnaire_new_step = 'wocat:questionnaire_new_step'
route_questionnaire_details = 'wocat:questionnaire_details'
route_questionnaire_list = 'wocat:questionnaire_list'


def get_valid_new_step_values():
    return (
        'wocat_cat_1', 'wocat', 'wocat/questionnaire/new_step.html',
        'wocat:questionnaire_new')


def get_valid_new_values():
    args = (
        'wocat', 'wocat/questionnaire/new.html', 'wocat:questionnaire_details',
        'wocat:questionnaire_new_step')
    kwargs = {'questionnaire_id': None}
    return args, kwargs


def get_valid_details_values():
    return (1, 'wocat', 'wocat/questionnaire/details.html')


def get_valid_list_values():
    return (
        'wocat', 'wocat/questionnaire/list.html',
        'wocat:questionnaire_details')


def get_category_count():
    return len(get_categories())


def get_categories():
    return (
        ('wocat_cat_1', 'WOCAT Category 1'),
    )


class WocatHomeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_home)

    def test_renders_correct_template(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'wocat/home.html')
        self.assertEqual(res.status_code, 200)


class QuestionnaireNewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_new)

    def test_questionnaire_new_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_questionnaire_new_test_renders_correct_template(self):
        do_log_in(self.client)
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'wocat/questionnaire/new.html')
        self.assertEqual(res.status_code, 200)

    @patch('wocat.views.generic_questionnaire_new')
    def test_calls_generic_function(self, mock_questionnaire_new):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new(request)
        mock_questionnaire_new.assert_called_once_with(
            request, *get_valid_new_values()[0], **get_valid_new_values()[1])


class QuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'wocat.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_new_step, args=['wocat_cat_1'])

    def test_questionnaire_new_step_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_renders_correct_template(self):
        do_log_in(self.client)
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'wocat/questionnaire/new_step.html')
        self.assertEqual(res.status_code, 200)

    @patch('wocat.views.generic_questionnaire_new_step')
    def test_calls_generic_function(self, mock_questionnaire_new_step):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new_step(request, 'wocat_cat_1')
        mock_questionnaire_new_step.assert_called_once_with(
            request, *get_valid_new_step_values())


class QuestionnaireDetailsTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'wocat.json', 'wocat_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_details, args=[1])

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'wocat/questionnaire/details.html')
        self.assertEqual(res.status_code, 200)

    @patch('wocat.views.generic_questionnaire_details')
    def test_calls_generic_function(self, mock_questionnaire_details):
        request = self.factory.get(self.url)
        questionnaire_details(request, 1)
        mock_questionnaire_details.assert_called_once_with(
            request, *get_valid_details_values())


class QuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_list)

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'wocat/questionnaire/list.html')
        self.assertEqual(res.status_code, 200)

    @patch('wocat.views.generic_questionnaire_list')
    def test_calls_generic_function(self, mock_questionnaire_list):
        request = self.factory.get(self.url)
        questionnaire_list(request)
        mock_questionnaire_list.assert_called_once_with(
            request, *get_valid_list_values())
