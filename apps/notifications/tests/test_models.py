from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
from django.test import override_settings
from model_mommy import mommy
from qcat.tests import TestCase

from notifications.models import ActionContextQuerySet, Log, StatusUpdate, \
    ReadLog, ContentUpdate
from questionnaire.models import Questionnaire


class ActionContextTest(TestCase):

    def make_user(*permissions, **attributes):
        """
        Helper for user creation, as the method 'get_all_permissions' is crucial,
        but creating groups and permissions is too much overhead.
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

        self.questionnaire = mommy.make(
            Questionnaire,
            status=settings.QUESTIONNAIRE_SUBMITTED
        )

        # Notification for a submitted questionnaire
        self.catalyst_change = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_CHANGE_STATUS,
            catalyst=self.catalyst,
            questionnaire=self.questionnaire
        )
        self.catalyst_change.subscribers.add(self.subscriber)
        mommy.make(
            StatusUpdate,
            log=self.catalyst_change,
            status=settings.QUESTIONNAIRE_SUBMITTED
        )

        # Notification the should not be listed
        self.catalyst_edit = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_EDIT_CONTENT,
            catalyst=self.catalyst,
            questionnaire=self.questionnaire
        )

        self.admin_read_log = mommy.make(
            ReadLog,
            user=self.admin,
            log=self.catalyst_change,
            is_read=True
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

    def test_user_log_list_reviewer_permissions(self):
        self.assertQuerysetEqual(
            Log.actions.user_log_list(self.reviewer),
            [self.catalyst_change.id],
            transform=self.transform
        )

    def test_user_log_list_publisher_permissions(self):
        self.assertFalse(
            Log.actions.user_log_list(self.publisher).exists()
        )

    def test_user_pending_list_reviewer_has_log(self):
        self.assertQuerysetEqual(
            Log.actions.user_pending_list(self.reviewer),
            [self.catalyst_change.id],
            transform=self.transform
        )

    def test_user_pending_list_admin_has_no_logs(self):
        # admin has read the notification
        self.assertFalse(
            Log.actions.user_pending_list(self.admin).exists()
        )

    def test_user_pending_list_publisher_has_no_logs(self):
        self.assertFalse(
            Log.actions.user_pending_list(self.publisher).exists()
        )

    def test_user_log_count(self):
        # Old notification for same questionnaire
        catalyst_change_old = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_CHANGE_STATUS,
            catalyst=self.catalyst,
            questionnaire=self.questionnaire
        )
        mommy.make(
            StatusUpdate,
            log=catalyst_change_old,
            status=settings.QUESTIONNAIRE_SUBMITTED
        )
        # both notifications are listed, but only one 'counts', as only one
        # must be worked on (the new one). as the qs is ordered by creation, the
        # old one comes first.
        self.assertQuerysetEqual(
            Log.actions.user_log_list(self.reviewer),
            [catalyst_change_old.id, self.catalyst_change.id],
            transform=self.transform
        )
        self.assertEqual(
            Log.actions.user_log_count(self.reviewer),
            1
        )

    def test_user_log_zero_subscriber(self):
        for role in ['subscriber', 'catalyst', 'publisher']:
            self.assertEqual(
                Log.actions.user_log_count(getattr(self, role)), 0
            )

    def test_read_logs_admin(self):
        self.assertQuerysetEqual(
            Log.actions.read_logs(user=self.admin),
            [self.admin_read_log.id],
            transform=self.transform
        )

    def test_read_logs_subscriber(self):
        self.assertFalse(
            Log.actions.read_logs(self.catalyst).exists()
        )

    def test_read_id_list(self):
        self.assertListEqual(
            list(Log.actions.read_id_list(self.admin)),
            [self.catalyst_change.id]
        )


class LogTest(TestCase):

    def setUp(self):
        self.catalyst = mommy.make(
            model=get_user_model()
        )
        self.status_log = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_CHANGE_STATUS,
            catalyst=self.catalyst
        )
        mommy.make(
            model=StatusUpdate,
            log=self.status_log
        )
        self.content_log = mommy.make(
            model=Log,
            action=settings.NOTIFICATIONS_EDIT_CONTENT
        )
        mommy.make(
            model=ContentUpdate,
            log=self.content_log
        )

    def test_is_content_update(self):
        self.assertTrue(self.content_log.is_content_update)

    def test_is_not_content_update(self):
        self.assertFalse(self.status_log.is_content_update)

    @patch('notifications.models.render_to_string')
    def test_get_linked_subject(self, render_to_string):
        self.status_log.get_linked_subject(self.catalyst)
        render_to_string.assert_called_with(
            'notifications/subject/{}.html'.format(
                settings.NOTIFICATIONS_CHANGE_STATUS
            ), {'log': self.status_log, 'user': self.catalyst}
        )
