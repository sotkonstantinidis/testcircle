from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest
from unittest.mock import patch

from unccd.tests.test_views import (
    questionnaire_route_list,
    questionnaire_route_new,
    questionnaire_route_new_step,
    get_category_count,
)


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
class QuestionnaireTest(FunctionalTest):

    fixtures = ['sample.json']

    def test_navigate_questionnaire(self, mock_do_auth):

        mock_do_auth.return_value = ('tempsessionid')

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new_step, args=['cat_1']))

        # She sees that the first question is active, the second not
        self.findBy(
            'xpath',
            '//a[@data-magellan-destination="question1" and @class="active"]')
        self.findByNot(
            'xpath',
            '//a[@data-magellan-destination="question2" and @class="active"]')

        # She clicks the button to go to the next question
        self.findBy('xpath', '//a[@data-magellan-step="next"]').click()
        self.browser.implicitly_wait(5)

        # Now the first question is inactive, the second is active
        self.findBy(
            'xpath',
            '//a[@data-magellan-destination="question2" and @class="active"]')
        self.findByNot(
            'xpath',
            '//a[@data-magellan-destination="question1" and @class="active"]')

        # A click on the other button goes up one question
        self.findBy('xpath', '//a[@data-magellan-step="previous"]').click()
        self.browser.implicitly_wait(5)
        self.findBy(
            'xpath',
            '//a[@data-magellan-destination="question1" and @class="active"]')
        self.findByNot(
            'xpath',
            '//a[@data-magellan-destination="question2" and @class="active"]')

    def test_repeating_questiongroups(self, mock_do_auth):

        mock_do_auth.return_value = ('tempsessionid')

        initial_button_count = 2

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new_step, args=['cat_3']))

        # She sees many buttons to add more questions
        add_more_buttons = self.findManyBy(
            'xpath', '//a[@data-questiongroup-keyword]')
        self.assertEqual(len(add_more_buttons), initial_button_count)

        # She sees the first questiongroups which has no possibility to
        # add more questions
        self.findBy('name', 'qg_5-0-key_7')
        self.findByNot('name', 'qg_5-1-key_7')

        # The second questiongroup is shown only once but can be
        # repeated up to 3 times
        self.findBy('name', 'qg_6-0-key_8').send_keys('1')
        self.findByNot('name', 'qg_6-1-key_8')

        # She adds another one and sees there is a remove button
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findBy('name', 'qg_6-1-key_8').send_keys('2')
        self.findByNot('name', 'qg_6-2-key_8')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 2)

        # And yet another one
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findBy('name', 'qg_6-1-key_8')
        self.findBy('name', 'qg_6-2-key_8').send_keys('3')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 3)

        # Adding a fourth questiongroup is not possible
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findByNot('name', 'qg_6-3-key_8')

        # She removes the middle one and sees that the correct one is
        # removed and the names of the other ones are updated.
        remove_buttons[1].click()
        f1 = self.findBy('name', 'qg_6-0-key_8')
        self.assertEqual(f1.get_attribute('value'), '1')
        f2 = self.findBy('name', 'qg_6-1-key_8')
        self.assertEqual(f2.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-2-key_8')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 2)

        # She removes the first one and sees that only one remains with
        # no button to remove it
        remove_buttons[0].click()
        f1 = self.findBy('name', 'qg_6-0-key_8')
        self.assertEqual(f1.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-1-key_8')
        self.findByNot('name', 'qg_6-2-key_8')
        self.findByNot(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')

        # The third questiongroup appears two times but has no buttons
        self.findBy('name', 'qg_7-0-key_9').send_keys('a')
        self.findBy('name', 'qg_7-1-key_9').send_keys('b')

        # The fourth questiongroup has two minimum fields and maximum 3
        self.findBy('name', 'qg_8-0-key_10').send_keys('x')
        self.findBy('name', 'qg_8-1-key_10').send_keys('y')
        self.findByNot('name', 'qg_8-2-key_10')

        # She adds one questiongroup and sees the button to remove it 3 times.
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_8"]').click()
        self.findBy('name', 'qg_8-2-key_10').send_keys('z')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 3)

        # She submits the form
        self.findBy('id', 'button-submit').click()

        # She sees the values were submitted
        self.checkOnPage('Key 8: 3')
        self.checkOnPage('Key 9: a')
        self.checkOnPage('Key 9: b')
        self.checkOnPage('Key 10: x')
        self.checkOnPage('Key 10: y')
        self.checkOnPage('Key 10: z')

        # She edits again
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new_step, args=['cat_3']))

        # Key 8 is there only once
        f1 = self.findBy('name', 'qg_6-0-key_8')
        self.assertEqual(f1.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-1-key_8')
        self.findByNot('name', 'qg_6-2-key_8')

        # Key 10 is there 3 times
        f1 = self.findBy('name', 'qg_8-0-key_10')
        self.assertEqual(f1.get_attribute('value'), 'x')
        f2 = self.findBy('name', 'qg_8-1-key_10')
        self.assertEqual(f2.get_attribute('value'), 'y')
        f3 = self.findBy('name', 'qg_8-2-key_10')
        self.assertEqual(f3.get_attribute('value'), 'z')

        # She removes one Key 10 and submits the form again
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 3)
        remove_buttons[0].click()
        self.findByNot(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')

    def test_enter_questionnaire(self, mock_do_auth):

        mock_do_auth.return_value = ('tempsessionid')

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes directly to the UNCCD questionnaire
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new))

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

        # She sees X buttons to edit a category and clicks the first
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit")]')
        self.assertEqual(len(edit_buttons), get_category_count())
        edit_buttons[0].click()

        # She sees the form for Category 1
        self.findBy('xpath', '//h2[contains(text(), "Category 1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_2")]')

        # She enters Key 1
        self.findBy('name', 'qg_1-0-key_1').send_keys('Foo')

        # # She tries to submit the form and sees an error message saying
        # # that Key 3 is also required.
        # self.findBy('id', 'button-submit').click()
        # error = self.findBy(
        #     'xpath', '//div[contains(@class, "qg_1")]/ul[contains(@class, '
        #     '"errorlist")]/li')
        # self.assertEqual(error.text, "This field is required.")

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

        # She goes to the list of questionnaires and sees that the
        #  questionnaire she created is listed there.
        self.findBy('xpath', '//a[contains(@href, "{}")]'.format(
            reverse(questionnaire_route_list)))
        self.checkOnPage('List')
        self.checkOnPage('Foo')

        # If she goes to the questionnaire overview form again, she sees
        # that the session values are not there anymore.
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new))
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 1")]')
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findByNot('xpath', '//*[contains(text(), "Bar")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findBy('xpath', '//h4[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')
