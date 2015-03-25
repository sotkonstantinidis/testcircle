from django.test.client import RequestFactory
from unittest.mock import patch
from django.core.urlresolvers import reverse

from accounts.tests.test_authentication import (
    create_new_user,
    do_log_in,
)
from qcat.tests import TestCase
from sample.views import (
    questionnaire_details,
    questionnaire_list,
    questionnaire_new,
    questionnaire_new_step,
)

route_questionnaire_details = 'sample:questionnaire_details'
route_questionnaire_list = 'sample:questionnaire_list'
route_questionnaire_new = 'sample:questionnaire_new'
route_questionnaire_new_step = 'sample:questionnaire_new_step'


def get_valid_new_step_values():
    args = (get_categories()[0][0], 'sample', 'sample')
    kwargs = {'page_title': 'SAMPLE Form'}
    return args, kwargs


def get_valid_new_values():
    args = ('sample', 'sample')
    kwargs = {'questionnaire_id': None, 'page_title': 'SAMPLE Form Overview'}
    return args, kwargs


def get_valid_details_values():
    return (1, 'sample', 'sample/questionnaire/details.html')


def get_valid_list_values():
    return (
        'sample', 'sample/questionnaire/list.html',
        'sample:questionnaire_details')


def get_category_count():
    return len(get_categories())


def get_categories():
    return (
        ('cat_0', 'Category 0'),
        ('cat_1', 'Category 1'),
        ('cat_2', 'Category 2'),
        ('cat_3', 'Category 3'),
        ('cat_4', 'Category 4'),
    )


def get_position_of_category(category, start0=False):
    for i, cat in enumerate(get_categories()):
        if cat[0] == category:
            if start0 is True:
                return i
            else:
                return i + 1
    return None


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
        self.assertTemplateUsed(res, 'form/overview.html')
        self.assertEqual(res.status_code, 200)

    @patch('sample.views.generic_questionnaire_new')
    def test_calls_generic_function(self, mock_questionnaire_new):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new(request)
        mock_questionnaire_new.assert_called_once_with(
            request, *get_valid_new_values()[0], **get_valid_new_values()[1])


class QuestionnaireNewStepTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(
            route_questionnaire_new_step, args=[get_categories()[0][0]])

    def test_questionnaire_new_step_login_required(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'login.html')

    def test_renders_correct_template(self):
        do_log_in(self.client)
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'form/category.html')
        self.assertEqual(res.status_code, 200)

    @patch('sample.views.generic_questionnaire_new_step')
    def test_calls_generic_function(self, mock_questionnaire_new_step):
        request = self.factory.get(self.url)
        request.user = create_new_user()
        questionnaire_new_step(request, get_categories()[0][0])
        mock_questionnaire_new_step.assert_called_once_with(
            request, *get_valid_new_step_values()[0],
            **get_valid_new_step_values()[1])


class QuestionnaireDetailsTest(TestCase):

    fixtures = [
        'groups_permissions.json', 'sample.json', 'sample_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_questionnaire_details, args=[1])

    def test_renders_correct_template(self):
        res = self.client.get(self.url, follow=True)
        self.assertTemplateUsed(res, 'sample/questionnaire/details.html')
        self.assertEqual(res.status_code, 200)

    @patch('sample.views.generic_questionnaire_details')
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
        self.assertTemplateUsed(res, 'sample/questionnaire/list.html')
        self.assertEqual(res.status_code, 200)

    @patch('sample.views.generic_questionnaire_list')
    def test_calls_generic_function(self, mock_questionnaire_list):
        request = self.factory.get(self.url)
        questionnaire_list(request)
        mock_questionnaire_list.assert_called_once_with(
            request, *get_valid_list_values())
