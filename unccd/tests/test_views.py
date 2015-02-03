from django.test.client import RequestFactory
from unittest.mock import patch

from qcat.tests import TestCase
from unccd.views import (
    questionnaire_new,
    questionnaire_new_step,
)


def get_valid_new_step_values():
    return (
        'cat_1', 'unccd', 'unccd/questionnaire/new_step.html',
        'unccd_questionnaire_new')


def get_valid_new_values():
    return ('unccd', 'unccd/questionnaire/new.html')


class QuestionnaireNewTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_questionnaire_new_test_renders_correct_template(self):
        res = self.client.get('/unccd/new', follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/new.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new')
    def test_questionnaire_new_test_calls_generic_function(
            self, mock_questionnaire_new):
        request = self.factory.get('/unccd/new')
        questionnaire_new(request)
        mock_questionnaire_new.assert_called_once_with(
            request, *get_valid_new_values())


class QuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()

    def test_renders_correct_template(self):
        res = self.client.get('/unccd/new/cat_1', follow=True)
        self.assertTemplateUsed(res, 'unccd/questionnaire/new_step.html')
        self.assertEqual(res.status_code, 200)

    @patch('unccd.views.generic_questionnaire_new_step')
    def test_calls_generic_function(
            self, mock_questionnaire_new_step):
        request = self.factory.get('/unccd/new/cat_1')
        questionnaire_new_step(request, 'cat_1')
        mock_questionnaire_new_step.assert_called_once_with(
            request, *get_valid_new_step_values())
