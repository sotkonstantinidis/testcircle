from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from qcat.utils import get_session_questionnaire
from sample.tests.test_views import (
    route_questionnaire_list,
    route_questionnaire_new,
    route_questionnaire_new_step,
    get_category_count,
    get_position_of_category,
)


class QuestionnaireTest(FunctionalTest):

    fixtures = ['sample.json']

    def test_stores_session_dictionary_correctly(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))

        # She enters something as first key
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        self.assertEqual(key_1.text, '')
        key_1.send_keys('Foo')

        self.findBy('id', 'button-submit').click()

        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        session_data = get_session_questionnaire()
        self.assertEqual(session_data, {'qg_1': [{'key_1': {'en': 'Foo'}}]})

        # self.assertEqual(self.browser.current_url, 'foo')

    def test_navigate_questionnaire(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))

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

    def test_repeating_questiongroups(self):

        initial_button_count = 3

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_3']))

        # She sees the helptext
        self.checkOnPage('Helptext 1')

        # She sees many buttons to add more questions
        add_more_buttons = self.findManyBy(
            'xpath', '//a[@data-questiongroup-keyword]')
        self.assertEqual(len(add_more_buttons), initial_button_count)

        # She sees the first questiongroups which has no possibility to
        # add more questions
        self.findBy('name', 'qg_5-0-original_key_7')
        self.findByNot('name', 'qg_5-1-original_key_7')

        # The second questiongroup is shown only once but can be
        # repeated up to 3 times
        self.findBy('name', 'qg_6-0-original_key_8').send_keys('1')
        self.findByNot('name', 'qg_6-1-original_key_8')

        # She adds another one and sees there is a remove button
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findBy('name', 'qg_6-1-original_key_8').send_keys('2')
        self.findByNot('name', 'qg_6-2-original_key_8')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 2)

        # And yet another one
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findBy('name', 'qg_6-1-original_key_8')
        self.findBy('name', 'qg_6-2-original_key_8').send_keys('3')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 3)

        # Adding a fourth questiongroup is not possible
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_6"]').click()
        self.findByNot('name', 'qg_6-3-original_key_8')

        # She removes the middle one and sees that the correct one is
        # removed and the names of the other ones are updated.
        remove_buttons[1].click()
        f1 = self.findBy('name', 'qg_6-0-original_key_8')
        self.assertEqual(f1.get_attribute('value'), '1')
        f2 = self.findBy('name', 'qg_6-1-original_key_8')
        self.assertEqual(f2.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-2-original_key_8')
        remove_buttons = self.findManyBy(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')
        self.assertEqual(len(remove_buttons), 2)

        # She removes the first one and sees that only one remains with
        # no button to remove it
        remove_buttons[0].click()
        f1 = self.findBy('name', 'qg_6-0-original_key_8')
        self.assertEqual(f1.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-1-original_key_8')
        self.findByNot('name', 'qg_6-2-original_key_8')
        self.findByNot(
            'xpath',
            '//a[@data-remove-this and not(contains(@style,"display: none"))]')

        # The third questiongroup appears two times but has no buttons
        self.findBy('name', 'qg_7-0-original_key_9').send_keys('a')
        self.findBy('name', 'qg_7-1-original_key_9').send_keys('b')

        # The fourth questiongroup has two minimum fields and maximum 3
        self.findBy('name', 'qg_8-0-original_key_10').send_keys('x')
        self.findBy('name', 'qg_8-1-original_key_10').send_keys('y')
        self.findByNot('name', 'qg_8-2-original_key_10')

        # She adds one questiongroup and sees the button to remove it 3 times.
        self.findBy('xpath', '//a[@data-questiongroup-keyword="qg_8"]').click()
        self.findBy('name', 'qg_8-2-original_key_10').send_keys('z')
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
            route_questionnaire_new_step, args=['cat_3']))

        # Key 8 is there only once
        f1 = self.findBy('name', 'qg_6-0-original_key_8')
        self.assertEqual(f1.get_attribute('value'), '3')
        self.findByNot('name', 'qg_6-1-original_key_8')
        self.findByNot('name', 'qg_6-2-original_key_8')

        # Key 10 is there 3 times
        f1 = self.findBy('name', 'qg_8-0-original_key_10')
        self.assertEqual(f1.get_attribute('value'), 'x')
        f2 = self.findBy('name', 'qg_8-1-original_key_10')
        self.assertEqual(f2.get_attribute('value'), 'y')
        f3 = self.findBy('name', 'qg_8-2-original_key_10')
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

    def test_form_progress(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')
        cat_1_position = get_position_of_category('cat_1')

        # She goes directly to the Sample questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))

        # She sees that all progress bars are to 0%
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="progress radius"]')
        self.assertEqual(len(progress_indicators), get_category_count())
        for x in progress_indicators:
            self.assertIn('0 /', x.text)
        progress_bars = self.findManyBy(
            'xpath', '//span[@class="meter" and @style="width:0.0%"]')
        self.assertEqual(len(progress_bars), len(progress_indicators))

        # She goes to the first category and sees another progress bar
        self.findBy('xpath', '(//a[contains(@href, "edit/cat")])[{}]'.format(
            cat_1_position)).click()
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')
        completed_steps = self.findBy('class_name', 'progress-completed')
        self.assertEqual(completed_steps.text, '0')
        total_steps = self.findBy('class_name', 'progress-total')
        self.assertEqual(total_steps.text, '2')

        # She types something in the first field and sees that the
        # progress bar changed
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('')
        self.findByNot('xpath', '//span[@class="meter" and @style="width:0%"]')
        self.findBy('xpath', '//span[@class="meter" and @style="width: 50%;"]')
        completed_steps = self.findBy('class_name', 'progress-completed')
        self.assertEqual(completed_steps.text, '1')

        # She saves the step and sees that the progress bar on the
        # overview page has changed
        self.findBy('id', 'button-submit').click()
        progress_bars = self.findManyBy(
            'xpath', '//span[@class="meter" and @style="width:0.0%"]')
        self.assertEqual(len(progress_bars), get_category_count() - 1)
        progress_bars = self.findBy(
            'xpath', '//span[@class="meter" and @style="width:50.0%"]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_1_position))
        self.assertEqual(progress_indicator.text, '1 / 2')

        # She decides to edit the step again and deletes what she
        # entered. She notices that the bar is back to 0, also on the
        # overview page.
        self.findBy('xpath', '(//a[contains(@href, "edit/cat")])[{}]'.format(
            cat_1_position)).click()
        self.findBy('xpath', '//span[@class="meter" and @style="width: 50%;"]')
        self.findBy('name', 'qg_1-0-original_key_1').clear()
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('')
        self.findBy('xpath', '//span[@class="meter" and @style="width: 0%;"]')
        self.findBy('id', 'button-submit').click()

        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="progress radius"]')
        self.assertEqual(len(progress_indicators), get_category_count())
        for x in progress_indicators:
            self.assertIn('0 /', x.text)
        progress_bars = self.findManyBy(
            'xpath', '//span[@class="meter" and @style="width:0.0%"]')
        self.assertEqual(len(progress_bars), len(progress_indicators))

        # Alice tries to submit the questionnaire but it is empty and
        # she sees an error message
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "info")]')

    def test_checkbox(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_2_position = get_position_of_category('cat_2')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))

        # She sees that no Checkbox of Key 13 is selected by default
        self.findByNot(
            'xpath', '//input[@name="qg_10-0-key_13" and @checked="checked"]')

        # She sees that the form progress is at 0
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She submits the form empty and sees that no value was submitted,
        # progress of Category 2 is still 0
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Key 13")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_2_position))
        self.assertIn('0 /', progress_indicator.text)

        # She goes back to the questionnaire step and sees that form
        # progress is still at 0 and no checkbox is selected
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')
        self.findByNot(
            'xpath', '//input[@name="qg_10-0-key_13" and @checked="checked"]')

        # She selects a first checkbox and sees that the form progress
        # was updated
        self.findBy(
            'xpath', '(//input[@name="qg_10-0-key_13"])[1]').click()
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She submits the step and sees that the value was submitted and
        # the form progress on the overview page is updated
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//*[contains(text(), "Key 13")]')
        self.findBy('xpath', '//*[contains(text(), "Value 13_1")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_2_position))
        self.assertIn('1 /', progress_indicator.text)

        # She goes back to the step and sees that the first checkbox is
        # selected, form progress is at 1
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She deselects the first value and sees that the progress was
        # updated
        self.findBy(
            'xpath', '(//input[@name="qg_10-0-key_13"])[1]').click()
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 0%;"]')

        # She then selects the second and third values and submits the
        # form
        self.findBy(
            'xpath', '(//input[@name="qg_10-0-key_13"])[2]').click()
        self.findBy(
            'xpath', '(//input[@name="qg_10-0-key_13"])[3]').click()
        self.findBy('id', 'button-submit').click()

        # The overview now shows both values
        self.findBy('xpath', '//*[contains(text(), "Key 13")]')
        self.findByNot('xpath', '//*[contains(text(), "Value 13_1")]')
        self.findBy('xpath', '//*[contains(text(), "Value 13_2")]')
        self.findBy('xpath', '//*[contains(text(), "Value 13_3")]')

        # She submits the form and sees that the radio value is stored
        # correctly
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//*[contains(text(), "Key 13")]')
        self.findByNot('xpath', '//*[contains(text(), "Value 13_1")]')
        self.findBy('xpath', '//*[contains(text(), "Value 13_2")]')
        self.findBy('xpath', '//*[contains(text(), "Value 13_3")]')

    def test_image_checkbox(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_4_position = get_position_of_category('cat_4')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))

        # She sees that no Checkbox of Key 14 is selected by default
        self.findByNot(
            'xpath', '//input[@name="qg_11-0-key_14" and @checked="checked"]')

        # She sees that the form progress is at 0
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She submits the form empty and sees that no value was submitted,
        # progress of Category 4 is still 0
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Key 14")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_4_position))
        self.assertIn('0 /', progress_indicator.text)

        # She goes back to the questionnaire step and sees that form
        # progress is still at 0 and no checkbox is selected
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')
        self.findByNot(
            'xpath', '//input[@name="qg_11-0-key_14" and @checked="checked"]')

        # She selects a first checkbox and sees that the form progress
        # was updated
        self.findBy(
            'xpath', '(//input[@name="qg_11-0-key_14"])[1]').click()
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She submits the step and sees that the value was submitted and
        # the form progress on the overview page is updated
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 14')
        self.findBy('xpath', '//img[@alt="Value 14_1"]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_4_position))
        self.assertIn('1 /', progress_indicator.text)

        # She goes back to the step and sees that the first checkbox is
        # selected, form progress is at 1
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She deselects the first value and sees that the progress was
        # updated
        self.findBy(
            'xpath', '(//input[@name="qg_11-0-key_14"])[1]').click()
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 0%;"]')

        # She then selects the second and third values and submits the
        # form
        self.findBy(
            'xpath', '(//input[@name="qg_11-0-key_14"])[2]').click()
        self.findBy(
            'xpath', '(//input[@name="qg_11-0-key_14"])[3]').click()
        self.findBy('id', 'button-submit').click()

        # The overview now shows both values
        self.checkOnPage('Key 14')
        self.findByNot('xpath', '//img[@alt="Value 14_1"]')
        self.findBy('xpath', '//img[@alt="Value 14_2"]')
        self.findBy('xpath', '//img[@alt="Value 14_3"]')

        # She submits the form and sees that the radio value is stored
        # correctly
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 14')
        self.findByNot('xpath', '//img[@alt="Value 14_1"]')
        self.findBy('xpath', '//img[@alt="Value 14_2"]')
        self.findBy('xpath', '//img[@alt="Value 14_3"]')

    def test_image_checkbox_subcategory(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_4_position = get_position_of_category('cat_4')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))

        # She sees the checkbox images of Key 15 which are not the same
        # as for Key 14.
        img_1_key_14 = self.findBy('xpath', '//img[@alt="Value 14_1"]')
        img_1_key_15 = self.findBy('xpath', '//img[@alt="Value 15_1"]')
        self.assertNotEqual(
            img_1_key_14.get_attribute('src'),
            img_1_key_15.get_attribute('src'))

        # She sees that no Checkbox of Key 15 is selected by default
        self.findByNot(
            'xpath', '//input[@name="qg_12-0-key_15" and @checked="checked"]')

        # She also sees that Key 16 is not visible
        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), 'display: none;')

        # She sees that the form progress is at 0
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She submits the form empty and sees that no value was submitted,
        # progress of Category 4 is still 0
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Key 15")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_4_position))
        self.assertIn('0 /', progress_indicator.text)

        # She goes back to the questionnaire step and sees that form
        # progress is still at 0 and no checkbox is selected
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')
        self.findByNot(
            'xpath', '//input[@name="qg_12-0-key_15" and @checked="checked"]')

        # She also sees that Key 16 is not visible
        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), 'display: none;')

        # She selects the first checkbox and sees that the form progress
        # was updated
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_15"])[1]').click()
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She also sees that Key 16 is now visible but no value is selected
        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), '')
        self.findByNot(
            'xpath', '//input[@name="qg_12-0-key_16" and @checked="checked"]')

        # She submits the step and sees that Key 15 was submitted and
        # the form progress on the overview page is updated
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 15')
        self.findBy('xpath', '//img[@alt="Value 15_1"]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_4_position))
        self.assertIn('1 /', progress_indicator.text)

        # She goes back to the step and sees that the value of Key 15 is
        # selected, form progress is at 1
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # Key 16 is visible but no value selected
        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), '')
        self.findByNot(
            'xpath', '//input[@name="qg_12-0-key_16" and @checked="checked"]')

        # She selects a value of Key 16
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_16"])[1]').click()

        # She submits the step and sees that both values are submitted
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 15')
        self.findBy('xpath', '//img[@alt="Value 15_1"]')
        self.checkOnPage('Key 16')
        self.findBy('xpath', '//img[@alt="Value 16_1"]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_4_position))
        self.assertIn('1 /', progress_indicator.text)

        # She goes back to the step and sees that the value of Key 15 is
        # selected, form progress is at 1
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_4']))
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She sees that the value of Key 15 is selected. Key 16 is
        # visible and the first value is selected.
        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), '')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16" and @checked="checked"]')

        # She deselects the value of Key 15 and sees that Key 16 is not
        # visible anymore
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_15"])[1]').click()

        subcat_val_1 = self.findBy(
            'xpath', '//div[@class="list-sub small-12 columns"]')
        self.findBy(
            'xpath', '//input[@name="qg_12-0-key_16"]', base=subcat_val_1)
        self.assertEqual(subcat_val_1.get_attribute('style'), 'display: none;')

        # She reselects the value of Key 15 and sees that the previously
        # selected value of Key 16 is not selected anymore.
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_15"])[1]').click()
        self.findByNot(
            'xpath', '//input[@name="qg_12-0-key_16" and @checked="checked"]')

        # She selects two values of Key 16 again and submits the form
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_16"])[1]').click()
        self.findBy(
            'xpath', '(//input[@name="qg_12-0-key_16"])[2]').click()
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 15')
        self.findBy('xpath', '//img[@alt="Value 15_1"]')
        self.checkOnPage('Key 16')
        self.findBy('xpath', '//img[@alt="Value 16_1"]')
        self.findBy('xpath', '//img[@alt="Value 16_2"]')

        # She submits the form and sees that the values were stored
        # correctly
        self.findBy('id', 'button-submit').click()
        self.checkOnPage('Key 15')
        self.findBy('xpath', '//img[@alt="Value 15_1"]')
        self.checkOnPage('Key 16')
        self.findBy('xpath', '//img[@alt="Value 16_1"]')
        self.findBy('xpath', '//img[@alt="Value 16_2"]')

    def test_measure_selects(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_2_position = get_position_of_category('cat_2')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))

        # She sees Key 12 in a row which is not selected
        self.findByNot(
            'xpath', '//div[@class="row list-item is-selected"]/div/label['
            'contains(text(), "Key 12")]')

        # She sees that the first (None) value is selected by default
        self.findBy(
            'xpath', '//input[@checked="" and @name="qg_9-0-key_12" and '
            '@value=""]')

        # She sees that the form progress is at 0
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She submits the form empty and sees that no value was submitted,
        # progress of Category 2 is still 0
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Key 12")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_2_position))
        self.assertIn('0 /', progress_indicator.text)

        # She goes back to the questionnaire step and sees that form
        # progress is still at 0 and the row is unselected
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')
        self.findByNot(
            'xpath', '//div[@class="row list-item is-selected"]/div/div/label['
            'contains(text(), "Key 12")]')

        # She selects the first value and sees that the row is now
        # selected and the form progress was updated
        self.findBy(
            'xpath', '//label/span[contains(text(), "Value 1")]').click()
        self.findBy(
            'xpath', '//div[@class="row list-item is-selected"]/div/div/label['
            'contains(text(), "Key 12")]')
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She submits the step and sees that the value was submitted and
        # the form progress on the overview page is updated
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//*[contains(text(), "Key 12")]')
        self.findBy('xpath', '//*[contains(text(), "Value 1")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_2_position))
        self.assertIn('1 /', progress_indicator.text)

        # She goes back to the step and sees the row is highlighted and
        # Value 1 selected, form progress is at 1
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_2']))
        self.findBy(
            'xpath', '//div[@class="row list-item is-selected"]/div/div/label['
            'contains(text(), "Key 12")]')
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She selects None and sees that the row is not highlighted
        # anymore and the progress was updated
        self.findBy(
            'xpath', '//label/span[contains(text(), "-")]').click()
        self.findByNot(
            'xpath', '//div[@class="row list-item is-selected"]/div/div/label['
            'contains(text(), "Key 12")]')
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 0%;"]')

        # She then selects Value 2 and submits the form
        self.findBy(
            'xpath', '//label/span[contains(text(), "Value 2")]').click()
        self.findBy('id', 'button-submit').click()

        # The overview now shows Value 2 and she submits the form
        self.findBy('xpath', '//*[contains(text(), "Key 12")]')
        self.findBy('xpath', '//*[contains(text(), "Value 2")]')

        # She submits the form and sees that the radio value is stored
        # correctly
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//*[contains(text(), "Key 12: Value 2")]')

    def test_radio_selects(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_1_position = get_position_of_category('cat_1')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))

        # She sees that Key 11 is a radio button
        radios = self.findManyBy(
            'xpath', '//input[@name="qg_3-0-key_11" and @type="radio"]')
        self.assertEqual(len(radios), 2)

        # She sees that the form does not have any progress
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She submits the form empty and sees no value was submitted,
        # progress of Category 1 is still 0
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Key 11")]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_1_position))
        self.assertIn('0 /', progress_indicator.text)

        # She goes to the form again and clicks "Yes".
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))
        self.findBy(
            'xpath', '//input[@name="qg_3-0-key_11" and @value="True"]')\
            .click()

        # She sees that the progress was updated and submits the form.
        self.findBy('xpath', '//span[@class="meter" and @style="width: 50%;"]')

        self.findBy('id', 'button-submit').click()

        # She sees the value was transmitted and the progress was updated
        self.findBy('xpath', '//*[contains(text(), "Key 11: Yes")]')
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width:50.0%"]')
        progress_indicator = self.findBy(
            'xpath', '(//div[@class="progress radius"])[{}]'.format(
                cat_1_position))
        self.assertEqual(progress_indicator.text, '1 / 2')

        # She edits the form again and sets the radio button to "No"
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))
        self.findBy('xpath', '//span[@class="meter" and @style="width: 50%;"]')
        self.findBy(
            'xpath', '//input[@name="qg_3-0-key_11" and @value="True" and '
            '@checked=""]')
        self.findBy(
            'xpath', '//input[@name="qg_3-0-key_11" and @value="False"]')\
            .click()
        self.findBy('id', 'button-submit').click()

        # She sees the value was updated
        self.findBy('xpath', '//*[contains(text(), "Key 11: No")]')

        # She submits the form and sees the radio value is stored correctly
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//*[contains(text(), "Key 11: No")]')

    # def test_enter_questionnaire_requires_login(self):

    #     # Alice opens the login form and does not see a message
    #     self.browser.get(self.live_server_url + reverse(accounts_route_login))
    #     self.findByNot(
    #         'xpath', '//div[@class="alert-box info" and contains(text(), "' +
    #         reverse(route_questionnaire_new) + '")]')

    #     # Alice tries to access the form without being logged in
    #     self.browser.get(self.live_server_url + reverse(
    #         route_questionnaire_new))
    #     self.findBy(
    #         'xpath', '//div[@class="alert-box info" and contains(text(), "' +
    #         reverse(route_questionnaire_new) + '")]')

    #     # She sees that she has been redirected to the login page
    #     self.checkOnPage('Login')
    #     # self.checkOnPage(reverse(
    #     #     route_questionnaire_new))
    #     self.findBy('name', 'user').send_keys('a@b.com')
    #     self.findBy('name', 'pass').send_keys('foo')
    #     self.findBy('id', 'button_login').click()

    #     # # She sees that she is logged in and was redirected back to the form.
    #     # self.checkOnPage('Category 1')

    def test_header_image(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_0']))

        # She sees a field to put files, drawn by Dropzone
        dropzone = self.findBy(
            'xpath', '//div[@id="id_qg_14-0-file_key_19" and contains(@class, '
            '"dropzone")]')
        self.assertTrue(dropzone.is_displayed())

        # She does not see the preview field, which is hidden and does not
        # contain an image
        preview = self.findBy(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]')
        self.assertFalse(preview.is_displayed())
        self.findByNot(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]/'
            'div[@class="image-preview"]/img')

        # The hidden input field is empty
        filename = self.findBy('xpath', '//input[@id="id_qg_14-0-key_19"]')
        self.assertEqual(filename.get_attribute('value'), '')

        # She sees that the form does not have any progress
        self.findBy('xpath', '//span[@class="meter" and @style="width:0%"]')

        # She uploads an image
        self.dropImage('id_qg_14-0-file_key_19')

        # She sees that the dropzone is hidden, the preview is visible
        self.assertFalse(dropzone.is_displayed())
        self.assertTrue(preview.is_displayed())

        # Preview contains an image
        self.findBy(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]/'
            'div[@class="image-preview"]/img')

        # The filename was added to the hidden input field
        self.assertNotEqual(filename.get_attribute('value'), '')

        # She sees that the progress was updated.
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She removes the file
        self.findBy(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]/div/button'
            ).click()

        # She sees the image was removed and the preview container is not
        # visible anymore
        self.findByNot(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]/'
            'div[@class="image-preview"]/img')
        self.assertFalse(preview.is_displayed())

        # She sees the dropzone container again
        self.assertTrue(dropzone.is_displayed())

        # The hidden input field is empty again
        self.assertEqual(filename.get_attribute('value'), '')

        # She sees that the form does not have any progress
        self.findBy('xpath', '//span[@class="meter" and @style="width: 0%;"]')

        # She uploads an image again
        self.dropImage('id_qg_14-0-file_key_19')

        # Dropzone is hidden, preview is there, filename was written to field
        self.assertFalse(dropzone.is_displayed())
        self.assertTrue(preview.is_displayed())
        self.assertNotEqual(filename.get_attribute('value'), '')

        img_src = self.findBy(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]/'
            'div[@class="image-preview"]/img').get_attribute('src')
        img_name = img_src.split('/')[-1]

        # She sees that the progress was updated.
        self.findBy(
            'xpath', '//span[@class="meter" and @style="width: 100%;"]')

        # She submits the form
        self.findBy('id', 'button-submit').click()

        # On the overview page, she sees the image she uploaded
        self.findBy('xpath', '//img[contains(@src, "{}")]'.format(img_name))

        # She edits the form again and sees the image was populated correctly.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_0']))

        # Dropzone is hidden, preview is there, filename was written to field
        dropzone = self.findBy(
            'xpath', '//div[@id="id_qg_14-0-file_key_19" and contains(@class, '
            '"dropzone")]')
        self.assertFalse(dropzone.is_displayed())
        preview = self.findBy(
            'xpath', '//div[@id="preview-id_qg_14-0-file_key_19"]')
        self.assertTrue(preview.is_displayed())
        filename = self.findBy('xpath', '//input[@id="id_qg_14-0-key_19"]')
        self.assertNotEqual(filename.get_attribute('value'), '')

        # She submits the form and sees that the image was submitted correctly.
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//img[contains(@src, "{}")]'.format(img_name))

    def test_enter_questionnaire(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_1_position = get_position_of_category('cat_1', start0=True)

        # She goes directly to the Sample questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))

        # She sees the categories but without content, keys and
        # subcategories are hidden if they are empty.
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 1")]')
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findByNot('xpath', '//*[contains(text(), "Bar")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She tries to submit the form empty and sees an error message
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "info")]')

        # She sees X buttons to edit a category and clicks the first
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(@href, "edit/cat")]')
        self.assertEqual(len(edit_buttons), get_category_count())
        edit_buttons[cat_1_position].click()

        # She sees the form for Category 1
        self.findBy('xpath', '//h2[contains(text(), "Category 1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//legend[contains(text(), "Subcategory 1_2")]')

        # She enters Key 1
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')

        # # She tries to submit the form and sees an error message saying
        # # that Key 3 is also required.
        # self.findBy('id', 'button-submit').click()
        # error = self.findBy(
        #     'xpath', '//div[contains(@class, "qg_1")]/ul[contains(@class, '
        #     '"errorlist")]/li')
        # self.assertEqual(error.text, "This field is required.")

        # She enters Key 3 and submits the form again
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()

        # She sees that she was redirected to the overview page and is
        # shown a success message
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//h3[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//*[contains(text(), "Key 1")]')
        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Bar")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She submits the entire questionnaire
        self.findBy('id', 'button-submit').click()

        # She is being redirected to the details page and sees a success
        # message.
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//h3[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//*[contains(text(), "Key 1")]')
        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Bar")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

        # She sees that on the detail page, there is only one edit button
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit")]')
        self.assertEqual(len(edit_buttons), 1)

        # She goes to the list of questionnaires and sees that the
        #  questionnaire she created is listed there.
        self.findBy('xpath', '//a[contains(@href, "{}")]'.format(
            reverse(route_questionnaire_list)))
        self.checkOnPage('List')
        self.checkOnPage('Foo')

        # If she goes to the questionnaire overview form again, she sees
        # that the session values are not there anymore.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 1")]')
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findByNot('xpath', '//*[contains(text(), "Bar")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 1_2")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 4")]')
        self.findByNot('xpath', '//h3[contains(text(), "Subcategory 2_1")]')
        self.findByNot('xpath', '//*[contains(text(), "Key 5")]')

    def test_edit_questionnaire(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        cat_1_position = get_position_of_category('cat_1', start0=True)

        # She goes directly to the first category of the Sample
        # questionnaire and enters some data
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=['cat_1']))

        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()

        # She submits the entire questionnaire and clicks the edit
        # button on the detail page
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # She is back at the overview page of the questionnaire with the
        # previously entered values already there
        self.findBy('xpath', '//*[contains(text(), "Key 1")]')
        self.findBy('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Key 3")]')
        self.findBy('xpath', '//*[contains(text(), "Bar")]')

        # She edits a form and sees the values are there already
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/cat")]')[cat_1_position].click()
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        self.assertEqual(key_1.get_attribute('value'), 'Foo')
        key_3 = self.findBy('name', 'qg_1-0-original_key_3')
        self.assertEqual(key_3.get_attribute('value'), 'Bar')
        key_1.clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Faz')

        # She submits the step and sees that the values on the overview
        # page changed.
        self.findBy('id', 'button-submit').click()
        self.findByNot('xpath', '//*[contains(text(), "Foo")]')
        self.findBy('xpath', '//*[contains(text(), "Faz")]')

        # She submits the entire questionnaire
        self.findBy('id', 'button-submit').click()
