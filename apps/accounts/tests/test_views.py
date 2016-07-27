import json
from unittest.mock import patch, MagicMock

from braces.views import LoginRequiredMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test.client import RequestFactory
from qcat.tests import TestCase

from ..forms import WocatAuthenticationForm
from ..tests.test_models import create_new_user
from accounts.views import (
    details,
    user_update,
    LoginView,
    ProfileView, QuestionnaireStatusListView
)

User = get_user_model()
accounts_route_login = 'login'
accounts_route_logout = 'logout'
accounts_route_welcome = 'welcome'
accounts_route_questionnaires = 'account_questionnaires'
accounts_route_moderation = 'account_moderation'
accounts_route_user = 'user_details'


class LoginViewTest(TestCase):

    def setUp(self):
        self.invalid_login_credentials = {'username': 'foo', 'password': 'bar'}
        self.factory = RequestFactory()
        self.user = create_new_user()

    def test_form_invalid_credentials(self):
        """Invalid data must return a form with errors"""
        response = self.client.post(
            path=reverse('login'),
            data=self.invalid_login_credentials
        )
        self.assertTrue(hasattr(response.context_data['form'], 'errors'))
        self.assertTemplateUsed(response, 'login.html')

    def test_dispatch(self):
        request = self.factory.get(reverse('login'))
        setattr(request, 'user', self.user)
        request.user.is_authenticated = MagicMock(return_value=True)
        view = self.setup_view(LoginView(), request)
        response = view.dispatch(view.request, *view.args, **view.kwargs)
        self.assertEqual(response.status_code, 302)

    @patch('accounts.forms.WocatAuthenticationForm.get_user')
    @patch('accounts.authentication.WocatAuthenticationBackend.authenticate')
    @patch('accounts.client.typo3_client.remote_login')
    @patch('accounts.client.typo3_client.get_user_id')
    @patch('accounts.client.typo3_client.get_and_update_django_user')
    def test_form_valid(self, mock_get_auth_user, mock_auth, mock_remote_login,
                        mock_get_user_id, mock_get_and_update_user):
        # Fake user and required attributes
        user = self.user
        user.backend = 'accounts.authentication.WocatAuthenticationBackend'
        mock_get_auth_user.return_value = user
        mock_auth.return_value = user

        mock_remote_login.return_value = 1
        mock_get_user_id.return_value = 1
        mock_get_and_update_user.return_value = self.user

        form = WocatAuthenticationForm
        form.get_user = lambda x: user
        # Add message store
        request = RequestFactory().post(
            reverse('login'),
            data={'form': form(initial=self.invalid_login_credentials)}
        )
        request.user = user
        request.session = MagicMock()
        request._messages = FallbackStorage

        view = self.setup_view(LoginView(), request)

        response = view.form_valid(form(initial=self.invalid_login_credentials))

        self.assertEqual(request.user, self.user)
        self.assertEqual(response.url, reverse('home'))

    def setup_view(self, view, request, *args, **kwargs):
        """
        Mimic as_view() returned callable, but returns view instance.

        args and kwargs are the same you would pass to ``reverse()``
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view


class ProfileViewTest(TestCase):
    fixtures = ['sample_global_key_values.json', 'sample.json', 'sample_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        view = ProfileView()
        self.request = self.factory.get(reverse('account_questionnaires'))
        self.user = create_new_user()
        self.request.user = self.user
        self.view = self.setup_view(view, self.request)

    def test_renders_correct_template(self):
        self.assertEqual(self.view.get_template_names(), ['questionnaires.html'])

    @patch('accounts.views.query_questionnaires')
    def test_get_questionnaires(self, mock_query_questionnaires):
        self.view.get(self.request)
        mock_query_questionnaires.assert_called_once_with(
            configuration_code='all', limit=None, only_current=False, request=self.request, user=self.user
        )

    def test_user_required(self):
        self.assertTrue(issubclass(ProfileView, LoginRequiredMixin))

    def test_get_empty_status_list(self):
        self.view.object = self.user
        empty_status_list = self.view.get_status_list()
        self.assertDictEqual(empty_status_list, {})

    def test_get_status_list(self):
        self.view.object = User.objects.get(id=101)
        status_list = self.view.get_status_list()
        self.assertDictEqual(status_list, {4: 'Public'})


class QuestionnaireStatusListViewTest(TestCase):
    # fixtures = ['sample_global_key_values.json', 'sample.json', 'sample_questionnaires.json']

    def setUp(self):
        self.factory = RequestFactory()
        view = QuestionnaireStatusListView()
        self.request = self.factory.get(reverse('questionnaires_status_list'))
        self.valid_request = self.factory.get('{}?status={}'.format(
            reverse('questionnaires_status_list'),
            settings.QUESTIONNAIRE_PUBLIC
        ))
        self.user = create_new_user()
        self.request.user = self.user
        self.view = self.setup_view(view, self.request)

    def test_user_required(self):
        self.assertTrue(issubclass(ProfileView, LoginRequiredMixin))

    def test_get_no_status(self):
        with self.assertRaises(Http404):
            self.view.get_status()

    def test_get_invalid_status(self):
        request = self.factory.get('?status=12345'.format(
            reverse('questionnaires_status_list')
        ))
        view = self.setup_view(QuestionnaireStatusListView(), request)
        with self.assertRaises(Http404):
            view.get_status()

    def test_get_valid_status(self):
        view = self.setup_view(QuestionnaireStatusListView(), self.valid_request)
        self.assertEqual(view.get_status(), settings.QUESTIONNAIRE_PUBLIC)

    @patch('accounts.views.query_questionnaires')
    def test_get_queryset(self, mock_query_questionnaires):
        self.valid_request.user = self.user
        view = self.setup_view(QuestionnaireStatusListView(), self.valid_request)
        view.get_queryset()

        mock_query_questionnaires.assert_called_once_with(
            configuration_code='all', limit=None, only_current=False, request=self.valid_request, user=self.user
        )

    @patch('accounts.views.get_list_values')
    def test_get_context_data(self, mock_get_list_values):
        view = self.setup_view(QuestionnaireStatusListView(), self.valid_request)
        view.object_list = []
        view.get_context_data()
        self.assertTrue(mock_get_list_values.called)


class UserUpdateTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/accounts/update')
        self.request.method = 'POST'
        self.request.POST = {'uid': 1}
        self.request.user = create_new_user()

    def test_returns_error_if_no_uid(self):
        self.request.POST = {}
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertFalse(json_ret['success'])
        self.assertIn('message', json_ret)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_calls_get_user_information(self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        user_update(self.request)
        mock_get_user_information.assert_called_once_with(1)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_returns_error_if_no_user_info_found(
            self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        self.assertFalse(json_ret['success'])
        self.assertIn('message', json_ret)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_creates_user(self, mock_get_user_information):
        self.assertEqual(User.objects.count(), 1)
        mock_get_user_information.return_value = {'username': 'foo@bar.com'}
        user_update(self.request)
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'foo@bar.com')

    @patch('accounts.client.typo3_client.get_user_information')
    def test_updates_user(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'username': 'foo@bar.com',
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        self.request.POST = {'uid': 2}
        user_update(self.request)
        users = User.objects.all()
        self.assertEqual(len(users), 2)
        self.assertEqual(users[1].email, 'foo@bar.com')
        self.assertEqual(users[1].firstname, 'Faz')
        self.assertEqual(users[1].lastname, 'Taz')

    @patch('accounts.client.typo3_client.get_user_information')
    def test_returns_user_name(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'username': 'foo@bar.com',
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        ret = user_update(self.request)
        json_ret = json.loads(str(ret.content, encoding='utf8'))
        user = User.objects.get(pk=1)
        self.assertTrue(json_ret['success'])
        self.assertEqual(json_ret['name'], user.get_display_name())


class UserDetailsTest(TestCase):

    def setUp(self):
        self.request = RequestFactory().get('/en/accounts/user/1')
        self.user = create_new_user()

    @patch('accounts.views.get_object_or_404')
    def test_calls_get_object_or_404(self, mock_get_object_or_404):
        details(self.request, 0)
        mock_get_object_or_404.assert_called_once_with(User, pk=0)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_calls_get_user_information(self, mock_get_user_information):
        mock_get_user_information.return_value = {}
        details(self.request, self.user.id)
        mock_get_user_information.assert_called_once_with(self.user.id)

    @patch('accounts.client.typo3_client.get_user_information')
    def test_updates_user(self, mock_get_user_information):
        mock_get_user_information.return_value = {
            'first_name': 'Faz',
            'last_name': 'Taz',
        }
        details(self.request, self.user.id)
        users = User.objects.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].email, 'a@b.com')
        self.assertEqual(users[0].firstname, 'Faz')
        self.assertEqual(users[0].lastname, 'Taz')

    @patch('accounts.views.render')
    @patch('accounts.client.typo3_client.get_user_information')
    def test_calls_render(self, mock_get_user_information, mock_render):
        mock_get_user_information.return_value = {}
        details(self.request, self.user.id)
        mock_render.assert_called_once_with(self.request, 'details.html', {
            'detail_user': self.user, 'unccd_countries': []
        })
