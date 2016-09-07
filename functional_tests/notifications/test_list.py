from unittest.mock import patch

import time
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from model_mommy import mommy
from notifications.models import Log, StatusUpdate, ReadLog
from questionnaire.models import Questionnaire

from functional_tests.base import FunctionalTest


class NotificationSetupMixin:
    """
    Shared setup functionalities
    """

    def setUp(self):
        super().setUp()
        # create some users.
        self.robin = mommy.make(get_user_model(), firstname='robin')
        self.jay = mommy.make(get_user_model(), firstname='jay')

        # and a log that is ready for review.
        questionnaire = mommy.make(
            model=Questionnaire,
            status=settings.QUESTIONNAIRE_SUBMITTED
        )
        self.review_log = mommy.make(
            model=Log,
            questionnaire=questionnaire,
            catalyst=self.jay,
            action=settings.NOTIFICATIONS_CHANGE_STATUS
        )
        mommy.make(
            model=StatusUpdate,
            log=self.review_log,
            status=settings.QUESTIONNAIRE_SUBMITTED
        )

        # helpers
        self.profile_url = '{base}{profile}'.format(
            base=self.live_server_url,
            profile=reverse('account_questionnaires')
        )


class ProfileNotificationsTest(NotificationSetupMixin, FunctionalTest):

    def test_notification_display(self):
        # From a logged in state, open the profile page

        self.doLogin(user=self.robin)
        self.browser.get(self.profile_url)
        # no notifications are available
        self.assertTrue(
            self.findBy('id', 'latest-notification-updates').text.startswith(
                'No notifications.'
            )
        )
        # create a new notification
        mommy.make(model=Log, catalyst=self.robin )

        # After a reload, the notification for robin is shown, displaying one
        # notification log.
        self.browser.get(self.profile_url)
        logs = self.findManyBy('class_name', 'notification-list')
        self.assertEqual(len(logs), 1)
        # and the pagination is available.
        self.findBy('class_name', 'pagination-centered')


    @patch('django.contrib.auth.backends.ModelBackend.get_all_permissions')
    def test_todo_notification(self, mock_permissions):
        # Robin is now also a reviewer and logs in
        mock_permissions.return_value = ['questionnaire.review_questionnaire']
        self.doLogin(user=self.robin)
        self.browser.get(self.profile_url)

        # Exactly one notification and the label for 'pending' is shown.
        logs = self.findManyBy('class_name', 'notification-list')
        self.assertEqual(len(logs), 1)
        self.findBy('class_name', 'is-pending')

        # There is only one checkbox, so click it.
        checkbox = self.findBy("xpath", "//input[@type='checkbox']")
        checkbox.click()
        # After a little processing, the whole row is now marked as read and a
        # model entry is stored
        time.sleep(1)
        self.assertTrue('is-read' in logs[0].get_attribute('class'))
        self.assertTrue(
            ReadLog.objects.filter(
                user=self.robin, log=self.review_log, is_read=True
            )
        )
        # But the click was a mistake, the notification is not done yet, so
        # the checkbox is clicked again - and all is back to normal.
        checkbox.click()
        self.assertTrue('is-read' not in logs[0].get_attribute('class'))
        self.assertTrue(
            ReadLog.objects.filter(
                user=self.robin, log=self.review_log, is_read=False
            )
        )

    def test_no_todo_notification(self):
        # For the compiler of this log, jay, the is-pending label is not shown.
        self.doLogin(user=self.jay)
        self.browser.get(self.profile_url)
        logs = self.findManyBy('class_name', 'notification-list')
        self.assertEqual(len(logs), 1)
        self.findByNot('class_name', 'is-pending')

    def test_pagination(self):
        mommy.make(
            model=Log, _quantity=15, catalyst=self.jay
        )
        # Jay has many notifications, but only a slice is shown.
        self.doLogin(user=self.jay)
        self.browser.get(self.profile_url)
        logs = self.findManyBy('class_name', 'notification-list')
        self.assertEqual(len(logs), settings.NOTIFICATIONS_TEASER_PAGINATE_BY)

        # The other notifications are paginated. The 'previous' button is not
        # available on the first page.
        pagination = self.findBy(
            'id', 'latest-notification-updates'
        ).find_element_by_class_name(
            'pagination'
        )
        pagination_elements = pagination.find_elements_by_tag_name('li')
        self.assertTrue(
            'unavailable' in pagination_elements[0].get_attribute('class')
        )
        # The first page is marked as current page.
        self.assertTrue(
            pagination_elements[1].get_attribute('class') == 'current'
        )
        # When clicking on the next page
        pagination_elements[2].click()
        time.sleep(1)
        pagination = self.findBy(
            'id', 'latest-notification-updates'
        ).find_element_by_class_name(
            'pagination'
        )
        pagination_elements = pagination.find_elements_by_tag_name('li')
        # the second page is 'current'
        self.assertTrue(
            pagination_elements[2].get_attribute('class') == 'current'
        )
        # the 'previous' arrow is available
        self.assertTrue(
            'unavailable' not in pagination_elements[0].get_attribute('class')
        )
        # and new notifications are shown
        self.assertFalse(logs == self.findManyBy('class_name', 'notification-list'))


class NotificationsListTest(NotificationSetupMixin, FunctionalTest):
    """
    As most functionality is tested on the profile view, this contains mainly
    tests for the structure of the dedicated notifications page.
    """

    def setUp(self):
        super().setUp()
        self.relative_notifications_url = reverse('notification_list')
        self.notifications_url = '{base}{notifications_list}'.format(
            base=self.live_server_url,
            notifications_list=self.relative_notifications_url
        )

    def test_follow_profile_link(self):
        # After logging in, jay follows the link to view all notifications
        self.doLogin(user=self.jay)
        self.browser.get(self.profile_url)
        link = self.findBy('xpath', '//a[@href="{}"]'.format(self.relative_notifications_url))
        self.assertEqual(
            link.get_attribute('href'), self.notifications_url
        )

    def test_notifications_list(self):
        # Jay logs in and visits the notifications page
        self.doLogin(user=self.jay)
        self.browser.get(self.notifications_url)

        # A box to select only pending notifications is shown
        self.findBy('id', 'is-pending')

        # The actual list conatins one element only
        notifications = self.findBy(
            'id', 'notifications-list'
        ).find_elements_by_class_name(
            'notification-list'
        )
        self.assertEqual(1, len(notifications))

    def test_empty_notifications_list(self):
        # Robin logs in and visits the notifications page
        self.doLogin(user=self.robin)
        self.browser.get(self.notifications_url)
        # but no notifications are shown.
        notifications = self.findBy('id', 'notifications-list')
        self.assertTrue(
            notifications.text.startswith('No notifications.')
        )

    def test_pagination(self):
        mommy.make(
            model=Log, _quantity=21, catalyst=self.jay
        )
        # Jay has many notifications, but only a slice is shown.
        self.doLogin(user=self.jay)
        self.browser.get(self.notifications_url)
        logs = self.findManyBy('class_name', 'notification-list')
        self.assertEqual(len(logs), settings.NOTIFICATIONS_LIST_PAGINATE_BY)

    @patch('django.contrib.auth.backends.ModelBackend.get_all_permissions')
    def test_todo_notifications(self, mock_permissions):
        # Robin is now also a reviewer and logs in
        mommy.make(Log, catalyst=self.robin)
        mock_permissions.return_value = ['questionnaire.review_questionnaire']
        self.doLogin(user=self.robin)
        self.browser.get(self.notifications_url)
        # Initially, a massive amount of two notifications is shown.
        self.assertEqual(
            2, len(self.findManyBy('class_name', 'notification-list'))
        )
        # So Robin clicks the box to filter only 'pending' logs, resulting in
        # one log only.
        self.findBy('id', 'is-pending').click()
        self.assertEqual(
            1, len(self.findManyBy('class_name', 'notification-list'))
        )
        # After clicking the box again, all logs are shown.
        self.findBy('id', 'is-pending').click()
        self.assertEqual(
            2, len(self.findManyBy('class_name', 'notification-list'))
        )

    @patch('django.contrib.auth.backends.ModelBackend.get_all_permissions')
    def test_todo_notifications_get_param(self, mock_permissions):
        # Robin the reviewer visits the page for notifications with the
        # get-parameter to show pending logs only.
        mommy.make(Log, catalyst=self.robin, _quantity=3)
        mock_permissions.return_value = ['questionnaire.review_questionnaire']
        self.doLogin(user=self.robin)
        self.browser.get('{}?is_pending'.format(self.notifications_url))
        # Only the one pending log is shown, and the checkbox is active.
        self.assertEqual(
            1, len(self.findManyBy('class_name', 'notification-list'))
        )
        self.assertEqual(
            'true', self.findBy('id', 'is-pending').get_attribute('checked')
        )

        # After clicking on the checkbox, all notifications are shown.
        self.findBy('id', 'is-pending').click()
        time.sleep(1)
        self.assertEqual(
            4, len(self.findManyBy('class_name', 'notification-list'))
        )
