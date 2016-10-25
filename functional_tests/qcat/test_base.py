from unittest.mock import patch

from rest_framework.reverse import reverse

from functional_tests.base import FunctionalTest


@patch('questionnaire.views.generic_questionnaire_list')
class BaseTemplateTest(FunctionalTest):

    def test_warning_is_displayed(self, mock_questionnaire_list):
        mock_questionnaire_list.return_value = {}
        with self.settings(WARN_HEADER='FOO'):
            self.browser.get(self.live_server_url + reverse('about'))
            # Check if the warning box is displayed
            self.assertTrue(self.browser.find_element_by_xpath(
                '//div[contains(@class, "demo-version")]/*[contains(text(), '
                '"FOO")]'
            ).is_displayed())

    def test_warning_is_hidden(self, mock_questionnaire_list):
        mock_questionnaire_list.return_value = {}
        with self.settings(WARN_HEADER=''):
            self.browser.get(self.live_server_url + reverse('home'))
            # Check if the warning box is not displayed
            self.assertFalse(
                self.browser.find_element_by_class_name(
                    'demo-version'
                ).is_displayed()
            )
