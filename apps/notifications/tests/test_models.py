from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.test import override_settings
from model_mommy import mommy
from qcat.tests import TestCase

from notifications.models import ActionContextQuerySet, Log


class ActionContextTest(TestCase):

    def make_user(*permissions, **attributes):
        """
        Helper for user creation, as the method 'get_all_permissions' is crucial,
        but creating receipes for permissions is too much overhead.
        """
        user = mommy.make(
            model=get_user_model(),
            **attributes,
        )
        user.get_all_permissions = lambda: permissions
        return user

    def setUp(self):
        self.qs = ActionContextQuerySet()

        change_permissions = 'questionnaire.change_questionnaire'
        review_permissions = 'questionnaire.review_questionnaire'
        publish_permissions = 'questionnaire.publish_questionnaire'

        # Users with all relevant roles
        self.admin = self.make_user(change_permissions, review_permissions, publish_permissions)
        self.catalyst = self.make_user()
        self.subscriber = self.make_user()
        self.reviewer = self.make_user(change_permissions)
        self.reviewer = self.make_user(review_permissions)
        self.publisher = self.make_user(publish_permissions)

        # Notification logs with required statuses
        self.catalyst_change = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_CHANGE_STATUS,
            catalyst=self.catalyst,
        )
        self.catalyst_change.subscribers.add(self.subscriber)

        self.catalyst_edit = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_EDIT_CONTENT,
            catalyst=self.catalyst,
        )

    # assertQuerysetEqual uses the models 'repr' method to check its 'sameness'.
    # However, this seems not stable, so we use the models id.
    transform = lambda self, x: x.id

    @override_settings(NOTIFICATIONS_CHANGE_STATUS='baz')
    @override_settings(NOTIFICATIONS_QUESTIONNAIRE_STATUS_PERMISSIONS={'foo': 'bar'})
    def test_get_questionnaires_for_permissions(self):
        permissions = self.qs.get_questionnaires_for_permissions('foo')
        self.assertEqual(
            permissions,
            [Q(questionnaire__status='bar', action='baz')]
        )

    @override_settings(NOTIFICATIONS_QUESTIONNAIRE_STATUS_PERMISSIONS={'foo': 'bar'})
    def test_get_questionnaires_for_permissions(self):
        permissions = self.qs.get_questionnaires_for_permissions('bar')
        self.assertEqual(permissions, [])

    def test_user_log_list_catalyst(self):
        self.assertQuerysetEqual(
            Log.actions.user_log_list(self.catalyst),
            [self.catalyst_change.id],
            transform=self.transform
        )

    def test_user_log_list_subscriber(self):
        self.assertQuerysetEqual(
            Log.actions.user_log_list(self.subscriber),
            [self.catalyst_change.id],
            transform=self.transform
        )

    def test_user_log_list_admin_permissions(self):
        self.assertQuerysetEqual(
            Log.actions.user_log_list(self.admin),
            [self.catalyst_change.id],
            transform=self.transform
        )

#     def test_user_pending_list(self):
#         pass
#
#     def test_user_log_count(self):
#         pass
#
#     def test_read_logs(self):
#         pass
#
#     def test_read_id_list(self):
#         pass
#
#
# class LogTest(TestCase):
#
#     def test_subject(self):
#         pass
#
#     def test_message(self):
#         pass
#
#     def test_is_content_update(self):
#         pass
#
#     def test_get_linked_subject(self):
#         pass
