from django.test.client import RequestFactory
from unittest.mock import patch
from django.core.urlresolvers import reverse

from qcat.tests import TestCase
from unccd.views import (
    questionnaire_details,
    questionnaire_list,
    questionnaire_new,
    questionnaire_new_step,
)

questionnaire_route_details = 'unccd_questionnaire_details'
questionnaire_route_list = 'unccd_questionnaire_list'
questionnaire_route_new = 'unccd_questionnaire_new'
questionnaire_route_new_step = 'unccd_questionnaire_new_step'


def get_valid_new_step_values():
    return (
        'cat_1', 'unccd', 'unccd/questionnaire/new_step.html',
        'unccd_questionnaire_new')


def get_valid_new_values():
    return (
        'unccd', 'unccd/questionnaire/new.html', 'unccd_questionnaire_details')


def get_valid_details_values():
    return (1, 'unccd', 'unccd/questionnaire/details.html')


def get_valid_list_values():
    return (
        'unccd', 'unccd/questionnaire/list.html',
        'unccd_questionnaire_details')


def get_category_count():
    return 3


class QuestionnaireNewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(questionnaire_route_new)

    def test_questionnaire_new_test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/new.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new')
    def test_calls_generic_function(self, mock_questionnaire_new):
        request = self.factory.get(self.url)
        questionnaire_new(request)
        mock_questionnaire_new.assert_called_once_with(
            request, *get_valid_new_values())


class QuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(questionnaire_route_new_step, args=['cat_1'])

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/new_step.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new_step')
    def test_calls_generic_function(self, mock_questionnaire_new_step):
        request = self.factory.get(self.url)
        questionnaire_new_step(request, 'cat_1')
        mock_questionnaire_new_step.assert_called_once_with(
            request, *get_valid_new_step_values())


class QuestionnaireDetailsTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'sample.json', 'sample_questionnaires']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(questionnaire_route_details, args=[1])

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


class QuestionnaireListTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(questionnaire_route_list)

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/list.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_list')
    def test_calls_generic_function(self, mock_questionnaire_list):
        request = self.factory.get(self.url)
        questionnaire_list(request)
        mock_questionnaire_list.assert_called_once_with(
            request, *get_valid_list_values())
