# from django.test.client import RequestFactory
# from unittest.mock import patch
# from django.core.urlresolvers import reverse

# from accounts.tests.test_authentication import (
#     create_new_user,
#     do_log_in,
# )
# from qcat.tests import TestCase
# from unccd.views import (
#     questionnaire_details,
#     questionnaire_list,
#     questionnaire_new,
#     questionnaire_new_step,
# )

# questionnaire_route_details = 'unccd_questionnaire_details'
# questionnaire_route_list = 'unccd_questionnaire_list'
# questionnaire_route_new = 'unccd_questionnaire_new'
# questionnaire_route_new_step = 'unccd_questionnaire_new_step'


# def get_valid_new_step_values():
#     return (
#         'cat_1', 'unccd', 'unccd/questionnaire/new_step.html',
#         'unccd_questionnaire_new')


# def get_valid_new_values():
#     args = (
#         'unccd', 'unccd/questionnaire/new.html', 'unccd_questionnaire_details')
#     kwargs = {'questionnaire_id': None}
#     return args, kwargs


# def get_valid_details_values():
#     return (1, 'unccd', 'unccd/questionnaire/details.html')


# def get_valid_list_values():
#     return (
#         'unccd', 'unccd/questionnaire/list.html',
#         'unccd_questionnaire_details')


# def get_category_count():
#     return len(get_categories())


# def get_categories():
#     return (
#         ('cat_1', 'Category 1'),
#         ('cat_2', 'Category 2'),
#         ('cat_3', 'Category 3'),
#         ('cat_4', 'Category 4'),
#     )


# class QuestionnaireNewTest(TestCase):

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.url = reverse(questionnaire_route_new)

#     def test_questionnaire_new_login_required(self):
#         res = self.client.get(self.url, follow=True)
#         self.assertTemplateUsed(res, 'login.html')

#     def test_questionnaire_new_test_renders_correct_template(self):
#         do_log_in(self.client)
#         res = self.client.get(self.url)
#         self.assertTemplateUsed(res, 'unccd/questionnaire/new.html')
#         self.assertEqual(res.status_code, 200)

#     @patch('unccd.views.generic_questionnaire_new')
#     def test_calls_generic_function(self, mock_questionnaire_new):
#         request = self.factory.get(self.url)
#         request.user = create_new_user()
#         questionnaire_new(request)
#         mock_questionnaire_new.assert_called_once_with(
#             request, *get_valid_new_values()[0], **get_valid_new_values()[1])


# class QuestionnaireNewStepTest(TestCase):

#     fixtures = ['groups_permissions.json', 'sample.json']

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.url = reverse(questionnaire_route_new_step, args=['cat_1'])

#     def test_questionnaire_new_step_login_required(self):
#         res = self.client.get(self.url, follow=True)
#         self.assertTemplateUsed(res, 'login.html')

#     def test_renders_correct_template(self):
#         do_log_in(self.client)
#         res = self.client.get(self.url, follow=True)
#         self.assertTemplateUsed(res, 'unccd/questionnaire/new_step.html')
#         self.assertEqual(res.status_code, 200)

#     @patch('unccd.views.generic_questionnaire_new_step')
#     def test_calls_generic_function(self, mock_questionnaire_new_step):
#         request = self.factory.get(self.url)
#         request.user = create_new_user()
#         questionnaire_new_step(request, 'cat_1')
#         mock_questionnaire_new_step.assert_called_once_with(
#             request, *get_valid_new_step_values())


# class QuestionnaireDetailsTest(TestCase):

#     fixtures = [
#         'groups_permissions.json', 'sample.json', 'sample_questionnaires']

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.url = reverse(questionnaire_route_details, args=[1])

#     def test_renders_correct_template(self):
#         res = self.client.get(self.url, follow=True)
#         self.assertTemplateUsed(res, 'unccd/questionnaire/details.html')
#         self.assertEqual(res.status_code, 200)

#     @patch('unccd.views.generic_questionnaire_details')
#     def test_calls_generic_function(self, mock_questionnaire_details):
#         request = self.factory.get(self.url)
#         questionnaire_details(request, 1)
#         mock_questionnaire_details.assert_called_once_with(
#             request, *get_valid_details_values())


# class QuestionnaireListTest(TestCase):

#     def setUp(self):
#         self.factory = RequestFactory()
#         self.url = reverse(questionnaire_route_list)

#     def test_renders_correct_template(self):
#         res = self.client.get(self.url, follow=True)
#         self.assertTemplateUsed(res, 'unccd/questionnaire/list.html')
#         self.assertEqual(res.status_code, 200)

#     @patch('unccd.views.generic_questionnaire_list')
#     def test_calls_generic_function(self, mock_questionnaire_list):
#         request = self.factory.get(self.url)
#         questionnaire_list(request)
#         mock_questionnaire_list.assert_called_once_with(
#             request, *get_valid_list_values())
