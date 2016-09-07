from unittest.mock import patch

from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from wocat.tests.test_views import route_home


class MenuIndicatorTest(FunctionalTest):

    @patch('wocat.views.generic_questionnaire_list')
    def test_indicator(self, mock_list):
        mock_list.return_value = {}

        start_site_url = self.live_server_url + reverse(route_home)
        # Alice goes to the qcat start site
        self.browser.get(start_site_url)

        # Alice is not logged in, so no indicator is loaded.
        self.findByNot('class_name', 'notification-indicator')

        # After the login,
        self.doLogin()
        # there are not logs to be shown.
        self.findByNot('class_name', 'notification-indicator')

        # Someone else triggers an action which creates a new task for Alice
        with patch('notifications.models.Log.actions.user_log_count') as count:
            count.return_value = 42

            # so after loading the page agein, the indicator exists
            self.browser.get(start_site_url)
            link_element = self.findBy('class_name', 'notification-indicator')

            # The proper number is displayed
            self.assertEqual(link_element.text, str(count.return_value))

            # The link points to the notification list view.
            pending_url = '{base}{notification_list}?is_pending'.format(
                base=self.live_server_url,
                notification_list=reverse('notification_list')
            )
            self.assertEqual(
                link_element.get_attribute('href'), pending_url
            )
