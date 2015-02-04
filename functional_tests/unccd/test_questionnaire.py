from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest
from unittest.mock import patch


questionnaire_route = 'unccd_questionnaire_new'


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
class AdminTest(FunctionalTest):

    fixtures = ['sample.json']

    def test_enter_questionnaire(self, mock_do_auth):

        mock_do_auth.return_value = ('tempsessionid')

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes directly to the UNCCD questionnaire
        self.browser.get(self.live_server_url + reverse(questionnaire_route))

        # She sees the categories but without content, keys are hidden
        # if they are empty.
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 1")]')
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findByNot('xpath', '//*[contains(text(), "Bar")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She tries to submit the form empty and sees an error message
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "info")]')

        # She sees 2 buttons to edit a category and clicks the first
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit")]')
        self.assertEqual(len(edit_buttons), 2)
        edit_buttons[0].click()

        # She sees the form for Category 1
        self.findBy('xpath', '//h3[contains(text(), "Category 1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_2")]')

        # She enters Key 1
        self.findBy('name', 'qg_1-0-key_1').send_keys('Foo')

        # She tries to submit the form and sees an error message saying
        # that Key 3 is also required.
        self.findBy('id', 'button-submit').click()
        error = self.findBy(
            'xpath', '//div[contains(@class, "qg_1")]/ul[contains(@class, '
            '"errorlist")]/li')
        self.assertEqual(error.text, "This field is required.")

        # She enters Key 3 and submits the form again
        self.findBy('name', 'qg_1-0-key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()

        # She sees that she was redirected to the overview page and is
        # shown a success message
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//*[contains(text(), "Key 1")]')
        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Bar")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_2")]')
        self.findBy('xpath', '//*[contains(text(), "Key 4")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She submits the entire questionnaire
        self.findBy('id', 'button-submit').click()

        # She is being redirected to the details page and sees a success
        # message.
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//*[contains(text(), "Key 1")]')
        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Bar")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_2")]')
        self.findBy('xpath', '//*[contains(text(), "Key 4")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She sees that on the detail page, there is only one edit button
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit")]')
        self.assertEqual(len(edit_buttons), 1)

        # If she goes to the questoinnaire overview form again, she sees
        # that the session values are not there anymore.
        self.browser.get(self.live_server_url + reverse(questionnaire_route))
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 1")]')
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findByNot('xpath', '//*[contains(text(), "Bar")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')
