from unittest import mock

from configuration.models import Configuration
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from accounts.models import User
from accounts.tests.test_views import accounts_route_questionnaires
from model_mommy import mommy

from functional_tests.base import FunctionalTest
from questionnaire.models import Questionnaire, QuestionnaireMembership, Lock
from sample.tests.test_views import (
    route_questionnaire_details,
    route_questionnaire_new,
    get_categories)

from django.contrib.auth.models import Group
from accounts.tests.test_models import create_new_user


def has_old_version_step(browser):
    browser.findBy(
        'xpath', '//p[contains(text(), "There is an old version with changes '
        'in this section.")]')


def has_no_old_version_step(browser):
    browser.findByNot(
        'xpath', '//p[contains(text(), "There is an old version with changes '
        'in this section.")]')


def has_old_version_overview(browser):
    browser.findBy(
        'xpath', '//p[contains(text(), "There is an old version which is '
        'different than the current one.")]')


def has_no_old_version_overview(browser):
    browser.findByNot(
        'xpath', '//p[contains(text(), "There is an old version which is '
        'different than the current one.")]')


def get_sample_4_5_options(testcase, index=0):
    return testcase.findManyBy(
        'xpath',
        '//select[@id="id_qg_43-{}-key_58"]/option[not(@value="")]'.format(
            index))


def get_sample_4_6_options(testcase, index=0):
    return testcase.findManyBy(
        'xpath',
        '//select[@id="id_qg_46-{}-key_63"]/option[not(@value="")]'.format(
            index))


def get_sample_5_4_options(testcase, index=0):
    return testcase.findManyBy(
        'xpath',
        '//select[@id="id_qg_44-{}-key_60"]/option[not(@value="")]'.format(
            index))


def get_sample_5_5_options(testcase, index=0):
    return testcase.findManyBy(
        'xpath',
        '//select[@id="id_qg_45-{}-key_62"]/option[not(@value="")]'.format(
            index))


class EditTest(FunctionalTest):

    fixtures = [
        'groups_permissions.json', 'global_key_values.json', 'sample.json',
        'sample_questionnaire_status.json']

    def test_creation_date_does_not_change(self):

        # Alice logs in
        user = User.objects.get(pk=102)
        self.doLogin(user=user)

        # She goes to the details of an existing questionnaire and takes
        # note of the creation and update dates
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_3'}))
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        creation_date = dates[0].text
        update_date = dates[1].text

        # She edits the questionnaire
        self.review_action('edit')
        self.click_edit_section('cat_1')
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the changes were submitted
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # She notices that the creation date did not change while the
        # update date changed.
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        self.assertEqual(creation_date, dates[0].text)
        self.assertTrue(update_date != dates[1].text)

        # Alice logs in as a different user
        user = User.objects.get(pk=101)
        self.doLogin(user=user)

        # She also opens a draft version of a questionnaire and takes
        # note of the creation and update dates
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_1'}))
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        creation_date = dates[0].text
        update_date = dates[1].text

        # She makes an edit
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.hide_notifications()
        self.click_edit_section('cat_1')
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the changes were submitted
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # She notices that the creation date did not change while the
        # update date changed.
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        self.assertEqual(creation_date, dates[0].text)
        self.assertTrue(update_date != dates[1].text)

    def test_edit_draft(self):

        code = 'sample_1'

        # Alice logs in
        user = User.objects.get(pk=101)
        self.doLogin(user=user)

        # She goes to the detail page of a "draft" Questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': code}))
        self.assertIn(code, self.browser.current_url)

        self.findBy('xpath', '//*[text()[contains(.,"Foo 1")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"asdf")]]')

        # She edits the Questionnaire and sees that the URL contains the
        # code of the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.assertIn(code, self.browser.current_url)

        # She edits a category and sees that the URL still contains the
        # code of the Questionnaire
        self.hide_notifications()
        self.click_edit_section('cat_1')
        self.assertIn(code, self.browser.current_url)

        # She makes some changes and submits the category
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        key_1.clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('asdf')
        self.findBy('id', 'button-submit').click()

        # She is back on the overview page and sees that the URL still
        # contains the code of the Questionnaire
        self.assertIn(code, self.browser.current_url)

        # She sees that no new code was created.
        self.assertIn(code, self.browser.current_url)

        # She sees that the value of Key 1 was updated
        self.findByNot('xpath', '//*[text()[contains(.,"Foo 1")]]')
        self.findBy('xpath', '//*[text()[contains(.,"asdf")]]')

        # Also there was no additional version created in the database
        self.assertEqual(Questionnaire.objects.count(), 10)

    def test_edit_public(self):

        code = 'sample_3'

        # Alice logs in
        user = User.objects.get(pk=101)
        self.doLogin(user=user)

        # She goes to the detail page of a "public" Questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': code}))
        self.assertIn(code, self.browser.current_url)

        self.findBy('xpath', '//*[text()[contains(.,"Faz 3")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"asdf")]]')

        # She edits the Questionnaire and sees that the URL contains the
        # code of the Questionnaire
        self.review_action('edit')
        self.assertIn(code, self.browser.current_url)

        #  She edits a category and sees that the URL still contains the
        # code of the Questionnaire
        self.click_edit_section('cat_2')
        self.assertIn(code, self.browser.current_url)

        # She makes some changes and submits the category
        key_1 = self.findBy('name', 'qg_19-0-original_key_5')
        key_1.clear()
        self.findBy('name', 'qg_19-0-original_key_5').send_keys('asdf')
        self.findBy('id', 'button-submit').click()

        # She is back on the overview page and sees that the URL still
        # contains the code of the Questionnaire
        self.assertIn(code, self.browser.current_url)

        # She sees that no new code was created.
        self.assertIn(code, self.browser.current_url)

        # She sees that the value of Key 1 was updated
        self.findByNot('xpath', '//*[text()[contains(.,"Faz 3")]]')
        self.findBy('xpath', '//*[text()[contains(.,"asdf")]]')

        # Also there was an additional version created in the database
        self.assertEqual(Questionnaire.objects.count(), 11)

        # The newly created version has the same code
        self.assertEqual(Questionnaire.objects.filter(code=code).count(), 2)

        # She goes to see her own questionnaire and sees sample_3 appears only
        # once
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires))
        self.wait_for(
            'xpath', '//img[@src="/static/assets/img/ajax-loader.gif"]',
            visibility=False)

        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 6)

        self.findBy(
            'xpath', '//*[text()[contains(.,"asdf")]]', base=list_entries[0])
        self.findBy(
            'xpath', '//*[text()[contains(.,"Faz 1")]]', base=list_entries[1])

        # She clicks the first entry and sees that she is taken to the
        # details page of the latest (pending) version.
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//*[text()[contains(.,"asdf")]]/../../../figure/a').click()
        self.toggle_all_sections()
        self.checkOnPage('asdf')

    def test_edit_questionnaire(self):

        user = create_new_user(id=6, email='mod@bar.com')
        user.groups = [Group.objects.get(pk=3), Group.objects.get(pk=4)]
        user.save()

        # Alice logs in
        self.doLogin(user=user)

        # She enters a Questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        self.click_edit_section('cat_1')

        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # The questionnaire is already saved as draft
        # She submits it for review
        self.review_action('submit')

        # She reviews it
        self.review_action('review')

        # She publishes it
        self.review_action('publish')

        # She sees it is public and visible
        self.findBy('xpath', '//p[text()="Foo"]')
        self.findBy('xpath', '//p[text()="Bar"]')

        url = self.browser.current_url

        # She edits it
        self.review_action('edit')
        self.findBy(
            'xpath', '(//a[contains(text(), "Edit this section")])[2]').click()

        # She changes some values
        self.findBy('name', 'qg_1-0-original_key_1').clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('asdf')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # The questionnaire is already saved as draft
        # She is taken to the overview page where she sees the latest
        # (pending) changes of the draft
        self.findBy('xpath', '//p[text()="Bar"]')
        self.findByNot('xpath', '//p[text()="Foo"]')
        self.findBy('xpath', '//p[text()="asdf"]')

        # She sees the edit buttons
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit this section")]')
        self.assertEqual(len(edit_buttons), len(get_categories()))

        # She sees the possibility to view the questionnaire
        self.review_action('view')
        self.assertIn(url, self.browser.current_url + '#top')

        # All the changes are there
        self.findBy('xpath', '//p[text()="Bar"]')
        self.findByNot('xpath', '//p[text()="Foo"]')
        self.findBy('xpath', '//p[text()="asdf"]')

        # There are no buttons to edit the sections anymore
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(text(), "Edit this section")]')
        self.assertEqual(len(edit_buttons), 0)

    def test_edit_public_new_config_edition(self):
        """
        If a public version is edited, and a new configuration edition exists, the
        method to update the case data must be called.
        """
        code = 'sample_3'

        # Alice logs in, she is a member of the secretariat
        user = User.objects.get(pk=107)
        self.doLogin(user=user)

        self.browser.get(
            self.live_server_url +
            reverse(route_questionnaire_details, kwargs={'identifier': code})
        )

        # Meanwhile, a new configuration edition is created.
        questionnaire = Questionnaire.objects.get(code=code)
        config = questionnaire.configuration
        config.id = None
        config.edition = '007'
        config.save()

        # She starts editing the public version - as a new version of the
        # configuration is available, the data is migrated in between.
        with mock.patch.object(Configuration, 'get_edition') as mock_edition:
            mock_edition.return_value.update_questionnaire_data.return_value = \
                questionnaire.data
            self.review_action('edit')
            self.assertTrue(mock_edition.return_value.update_questionnaire_data.called)


class CustomToOptionsTest(FunctionalTest):

    fixtures = ['sample_global_key_values', 'sample']

    def test_custom_to_options(self):
        # Alice logs in
        self.doLogin()

        # She goes to step 5 of the SAMPLE form
        self.browser.get(
            self.live_server_url + reverse(route_questionnaire_new))
        self.click_edit_section('cat_5')

        # She sees that no labels are selected in key_65 and key_67
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="-"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="-"]')

        # She sees that the label fields are disabled
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="-"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="-"]')

        # She selects Value 1 of key 64
        self.select_chosen_element('id_qg_47_0_key_64_chosen', 'Value 64 1')

        # She sees the labels were updated in key_65 and key_67
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 1 Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="'
                    'Value 66 1 Right"]')

        # She deselects the value in key 64
        self.select_chosen_element('id_qg_47_0_key_64_chosen', '-')

        # She sees the labels were reset
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="-"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="-"]')

        # She selects Value 1 of key 64 again
        self.select_chosen_element('id_qg_47_0_key_64_chosen', 'Value 64 1')

        # She submits the step and sees the values were submitted correctly
        self.submit_form_step()
        self.findBy('xpath',
                    '//span[contains(@class, "chart-measure-label-left") and '
                    'contains(text(), "Value 66 1 Left")]')
        self.findBy('xpath',
                    '//span[contains(@class, "chart-measure-label-right") and '
                    'contains(text(), "Value 66 1 Right")]')

        # She goes back to the form
        self.click_edit_section('cat_5')

        # She sees the fields were populated correctly
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="Value 66 1 Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="Value 66 1 Right"]')

        # She sees the labels were updated in key_65 and key_67
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 1 Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="'
                    'Value 66 1 Right"]')

        # She selects Value 2 of key 64
        self.select_chosen_element('id_qg_47_0_key_64_chosen', 'Value 64 2')

        # She sees the labels were updated in key_65 and key_67
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 2 Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="'
                    'Value 66 2 Right"]')

        # She sees that the label fields are disabled
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="Value 66 2 Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen" and contains(@class, '
                    '"disabled")]/a/span[text()="Value 66 2 Right"]')

        # She selects Value 3 of key 64
        self.select_chosen_element('id_qg_47_0_key_64_chosen', 'Value 64 3')

        # She sees the labels were updated and show the first value possible
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 3A Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen"]/a/span[text()="'
                    'Value 66 3A Right"]')

        # She sees the field is not disabled anymore
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen" and not(contains('
                    '@class, "disabled"))]/a/span[text()="Value 66 3A Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen" and not(contains('
                    '@class, "disabled"))]/a/span[text()="Value 66 3A Right"]')

        # She sees she cannot select "Value 66 1 Left"
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]//ul[@class="chosen-'
                    'results"]/li[contains(text(), "Value 66 2 Left")]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 3A Left"]')

        # However, she can select "Value 66 3B Left"
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]//ul[@class="chosen-'
                    'results"]/li[contains(text(), "Value 66 3B Left")]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen"]/a/span[text()="'
                    'Value 66 3B Left"]')

        # She submits the step and sees the values were submitted correctly
        self.submit_form_step()
        self.findBy('xpath',
                    '//span[contains(@class, "chart-measure-label-left") and '
                    'contains(text(), "Value 66 3B Left")]')
        self.findBy('xpath',
                    '//span[contains(@class, "chart-measure-label-right") and '
                    'contains(text(), "Value 66 3A Right")]')

        # She goes back to step 5 of the form and sees the values were
        # initialized correctly, the label fields are not disabled
        self.click_edit_section('cat_5')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_65_chosen" and not(contains('
                    '@class, "disabled"))]/a/span[text()="Value 66 3B Left"]')
        self.findBy('xpath',
                    '//div[@id="id_qg_47_0_key_67_chosen" and not(contains('
                    '@class, "disabled"))]/a/span[text()="Value 66 3A Right"]')


class LinkedChoicesTest(FunctionalTest):

    fixtures = ['sample_global_key_values', 'sample']

    def test_linked_across_step(self):
        # Alice logs in
        self.doLogin()

        # She goes to step 5 of the SAMPLE form
        self.browser.get(
            self.live_server_url + reverse(route_questionnaire_new))
        self.click_edit_section('cat_5')

        # She sees that there are no choices available for 5.4
        self.assertEqual(len(get_sample_5_4_options(self)), 0)

        # She goes to section 4 of the SAMPLE form
        self.submit_form_step()
        self.click_edit_section('cat_4')

        # She selects some options in 4.4
        self.findBy('xpath', '//input[@id="subcat_4_4"]').click()
        self.findBy(
            'xpath', '//input[@data-container="qg_40"]', wait=True).click()
        xpath = '//select[@id="id_qg_40-0-key_57"]/option[@value="value_57_1"]'
        self.findBy('xpath', xpath, wait=True).click()

        self.findBy(
            'xpath', '//input[@data-container="qg_41"]', wait=True).click()
        xpath = '//select[@id="id_qg_41-0-key_57"]/option[@value="value_57_2"]'
        self.findBy('xpath', xpath, wait=True).click()

        self.findBy(
            'xpath', '//input[@data-container="qg_42"]', wait=True).click()
        xpath = '//select[@id="id_qg_42-0-key_57"]/option[@value="value_57_3"]'
        self.findBy('xpath', xpath, wait=True).click()

        # She submits the step and goes to step 5 again
        self.submit_form_step()
        self.click_edit_section('cat_5')

        # She sees that in 5.4, there are now 3 choices available.
        self.assertEqual(len(get_sample_5_4_options(self)), 3)

        # She fills out a first questiongroup
        self.select_chosen_element('id_qg_44_0_key_60_chosen', 'QG 40')
        self.findBy('id', 'id_qg_44-0-original_key_61').send_keys('Foo')

        # She also fills out a second questiongroup
        self.form_click_add_more('qg_44')
        self.assertEqual(len(get_sample_5_4_options(self, index=1)), 3)
        self.findBy('xpath',
                    '//div[@id="id_qg_44_1_key_60_chosen"]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_44_1_key_60_chosen"]//ul[@class="chosen-'
                    'results"]/li[contains(text(), "QG 42")]').click()
        self.findBy('id', 'id_qg_44-1-original_key_61').send_keys('Bar')

        # She sees that in 5.5, there are only 2 choices available (no qg_42)
        self.assertEqual(len(get_sample_5_5_options(self)), 2)

        # She submits the form step and sees that the values are there.
        self.submit_form_step()
        self.findBy('xpath',
                    '//h3[contains(text(), "Subcategory 5_4")]/following::p['
                    'contains(text(), "QG 40")]')

        # She goes back to step 4
        self.click_edit_section('cat_4')

        # She deselects a value
        xpath = '//select[@id="id_qg_40-0-key_57"]/option[@value=""]'
        self.findBy('xpath', xpath, wait=True).click()

        # She submits the step and goes back to step 5
        self.submit_form_step()
        self.findByNot('xpath',
                    '//h3[contains(text(), "Subcategory 5_4")]/following::p['
                    'contains(text(), "QG 40")]')

        self.click_edit_section('cat_5')

        # She sees that the option is not selected anymore, all the other
        # values are there
        self.assertEqual(len(get_sample_5_4_options(self)), 2)
        self.assertEqual(len(get_sample_5_4_options(self, index=1)), 2)
        self.findBy('xpath',
                    '//div[@id="id_qg_44_0_key_60_chosen"]/a/span[text()="-"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_44-0-original_key_61').get_attribute(
                'value'), 'Foo')
        self.findBy('xpath',
                    '//div[@id="id_qg_44_1_key_60_chosen"]/a/span['
                    'text()="QG 42"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_44-1-original_key_61').get_attribute(
                'value'), 'Bar')

        # She sees that in 5.5, there is only one option left
        self.assertEqual(len(get_sample_5_5_options(self)), 1)

    def test_linked_choices_within_step(self):
        # Alice logs in
        self.doLogin()

        # She goes to step 4 of the SAMPLE form
        self.browser.get(
            self.live_server_url + reverse(route_questionnaire_new))
        self.click_edit_section('cat_4')

        # She sees that no extremes can be selected in 4.5
        self.assertEqual(len(get_sample_4_5_options(self)), 0)

        # She selects some questiongroups in 4.4 and sees that they are now
        # available for selection in 4.5
        self.findBy('xpath', '//input[@id="subcat_4_4"]').click()
        self.findBy(
            'xpath', '//input[@data-container="qg_40"]', wait=True).click()
        # It is not sufficient to click the checkbox of the questiongroup, an
        # actual value of the questiongroup must be selected.
        self.assertEqual(len(get_sample_4_5_options(self)), 0)
        self.findBy('xpath',
                    '//select[@id="id_qg_40-0-key_57"]/option['
                    '@value="value_57_1"]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)

        # The same option is also available in 4.6
        self.assertEqual(len(get_sample_4_6_options(self)), 1)

        # She deselects the value again and sees the option disappears in 4.5
        self.findBy('xpath',
                    '//select[@id="id_qg_40-0-key_57"]/option['
                    '@value=""]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 0)
        self.assertEqual(len(get_sample_4_6_options(self)), 0)

        # She selects a value again, the option appears in 4.5
        self.findBy('xpath',
                    '//select[@id="id_qg_40-0-key_57"]/option['
                    '@value="value_57_2"]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)

        # The same option is also available in 4.6
        self.assertEqual(len(get_sample_4_6_options(self)), 1)

        # She changes the value of 4.5, still the option appears only once
        self.findBy('xpath',
                    '//select[@id="id_qg_40-0-key_57"]/option['
                    '@value="value_57_1"]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)
        self.assertEqual(len(get_sample_4_6_options(self)), 1)

        # She also selects another value in 4.4
        self.findBy('xpath', '//input[@data-container="qg_41"]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)
        xpath = '//select[@id="id_qg_41-0-key_57"]/option[@value="value_57_1"]'
        self.findBy('xpath', xpath, wait=True).click()
        self.assertEqual(len(get_sample_4_5_options(self)), 2)

        # The same option is also available in 4.6
        self.assertEqual(len(get_sample_4_6_options(self)), 2)

        # She selects an option in 4.6
        self.select_chosen_element('id_qg_46_0_key_63_chosen', 'QG 41')

        # She also selects value 3 of 4.4, but sees that this one is not in the
        # list of options for 4.5
        self.findBy('xpath', '//input[@data-container="qg_42"]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 2)
        xpath = '//select[@id="id_qg_42-0-key_57"]/option[@value="value_57_1"]'
        self.findBy('xpath', xpath, wait=True).click()
        self.assertEqual(len(get_sample_4_5_options(self)), 2)

        # However, the same option appears in 4.6
        self.assertEqual(len(get_sample_4_6_options(self)), 3)

        # In 4.6, the selected option is still qg_41
        self.findBy('xpath', '//div[@id="id_qg_46_0_key_63_chosen"]/a/span['
                             'text()="QG 41"]')

        # She selects an option in 4.5 and fills out the additional key.
        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]//ul[@class="chosen-'
                    'results"]/li[contains(text(), "QG 41")]').click()
        self.findBy('id', 'id_qg_43-0-original_key_59').send_keys('Foo')

        # She also adds another option in 4.5 by clicking "Add more".
        self.form_click_add_more('qg_43')
        self.assertEqual(len(get_sample_4_5_options(self, index=1)), 2)
        self.findBy('xpath',
                    '//div[@id="id_qg_43_1_key_58_chosen"]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_43_1_key_58_chosen"]//ul[@class="chosen-'
                    'results"]/li[contains(text(), "QG 40")]').click()
        self.findBy('id', 'id_qg_43-1-original_key_59').send_keys('Bar')

        # She deselects a value in 4.4
        self.findBy('xpath',
                    '//select[@id="id_qg_41-0-key_57"]/option['
                    '@value=""]').click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)
        self.assertEqual(len(get_sample_4_5_options(self, index=1)), 1)

        # She sees that the first questiongroup of 4.5 now has no value selected
        # but the additional text field is still there.
        self.findBy('xpath', '//div[@id="id_qg_43_0_key_58_chosen"]/a/span['
                             'text()="-"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_43-0-original_key_59').get_attribute(
                'value'), 'Foo')

        # The second questiongroup of 4.5 is untouched
        self.findBy('xpath', '//div[@id="id_qg_43_1_key_58_chosen"]/a/span['
                             'text()="QG 40"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_43-1-original_key_59').get_attribute(
                'value'), 'Bar')

        # She submits the step and sees the values are submitted correctly
        self.submit_form_step()

        # She opens section 4 again and sees that she can still only select
        # certain options in 4.5
        self.click_edit_section('cat_4')
        self.assertEqual(len(get_sample_4_5_options(self)), 1)
        self.assertEqual(len(get_sample_4_5_options(self, index=1)), 1)

        # The same option is also available in 4.6 (plus qg_42)
        self.assertEqual(len(get_sample_4_6_options(self)), 2)

        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]/a/span[text()="-"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_43-0-original_key_59').get_attribute(
                'value'), 'Foo')
        self.findBy('xpath',
                    '//div[@id="id_qg_43_1_key_58_chosen"]/a/span['
                    'text()="QG 40"]')
        self.assertEqual(
            self.findBy('id', 'id_qg_43-1-original_key_59').get_attribute(
                'value'), 'Bar')

    def test_linked_choices_order(self):
        # Alice logs in
        self.doLogin()

        # She goes to step 4 of the SAMPLE form
        self.browser.get(
            self.live_server_url + reverse(route_questionnaire_new))
        self.click_edit_section('cat_4')

        # She sees that no extremes can be selected in 4.5
        self.assertEqual(len(get_sample_4_5_options(self)), 0)

        # She selects some questiongroups in 4.4 and sees that they are now
        # available for selection in 4.5
        self.findBy('xpath', '//input[@id="subcat_4_4"]').click()
        self.findBy(
            'xpath', '//input[@data-container="qg_41"]', wait=True).click()
        self.findBy('xpath',
                    '//select[@id="id_qg_41-0-key_57"]/option['
                    '@value="value_57_1"]', wait=True).click()
        self.assertEqual(len(get_sample_4_5_options(self)), 1)

        # She selects another option
        self.findBy('xpath', '//input[@data-container="qg_40"]').click()
        self.findBy('xpath',
                    '//select[@id="id_qg_40-0-key_57"]/option['
                    '@value="value_57_2"]', wait=True).click()
        self.assertEqual(len(get_sample_4_5_options(self)), 2)

        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]').click()

        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]//ul[@class="chosen-'
                    'results"]/li[2][contains(text(), "QG 40")]')
        self.findBy('xpath',
                    '//div[@id="id_qg_43_0_key_58_chosen"]//ul[@class="chosen-'
                    'results"]/li[3][contains(text(), "QG 41")]')


class LockTest(FunctionalTest):
    """
    Tests for questionnaire locking.
    """
    fixtures = ['sample_global_key_values', 'sample']

    def setUp(self):
        super().setUp()
        self.jay = mommy.make(
            _model=get_user_model(),
            firstname='jay',
            email = 'jay@spam.com'
        )
        self.robin = mommy.make(
            _model=get_user_model(),
            firstname='robin',
            email='robin@spam.com'
        )
        self.questionnaire = mommy.make(
            _model=Questionnaire,
            data={},
            code='sample_1',
            status=settings.QUESTIONNAIRE_DRAFT,
            configuration=Configuration.objects.filter(code='sample').first()
        )
        # Create a valid questionnaire with the least required data.
        mommy.make(
            _model=QuestionnaireMembership,
            user=self.jay,
            questionnaire=self.questionnaire,
            role='compiler'
        )
        mommy.make(
            _model=QuestionnaireMembership,
            user=self.robin,
            questionnaire=self.questionnaire,
            role='editor'
        )
        self.questionnaire_edit_url = '{}{}'.format(
            self.live_server_url,
            reverse('sample:questionnaire_edit', args=['sample_1'])
        )
        self.questionnaire_view_url = '{}{}'.format(
            self.live_server_url,
            self.questionnaire.get_absolute_url()
        )

    def test_edit_adds_lock(self):
        # Jay loggs in and starts editing a section.
        self.doLogin(user=self.jay)
        self.browser.get(self.questionnaire_edit_url)
        self.hide_notifications()
        self.findManyBy('link_text', 'Edit this section')[0].click()

        # Robin logs in and views the questionnaire
        self.doLogin(user=self.robin)
        self.browser.get(self.questionnaire_view_url)
        # but the questionnaire is locked
        self.assertTrue(
            Lock.with_status.is_blocked('sample_1').exists()
        )
        # and the edit button has no url, but a message about the locked status
        edit_button = self.findBy('link_text', 'Edit')
        self.assertTrue(edit_button.get_attribute('disabled'))
        self.findBy('xpath', '//*[text()[contains(.,"This questionnaire is '
                             'locked for editing by jay None.")]]')

        # if the url is accessed directly, a notification is shown
        self.browser.get(self.questionnaire_edit_url)
        self.findBy('xpath', '//div[contains(@class, "notification") '
                             'and contains(@class, "warning")]')
        # maybe: should the edit buttons be disabled?

    def test_edit_locked(self):
        # The questionnaire is locked for Jay
        Lock.objects.create(
            questionnaire_code='sample_1', user=self.jay
        )
        self.doLogin(user=self.robin)
        # Viewing the questionnaire is fine
        self.browser.get(self.questionnaire_view_url)
        # When Robin tries to edit a section, the browser gets redirected
        self.browser.get('{}cat_1'.format(self.questionnaire_edit_url))
        self.browser.implicitly_wait(3)
        self.assertEqual(self.browser.current_url, self.questionnaire_view_url)

    def test_refresh_lock(self):
        self.doLogin(user=self.jay)
        self.browser.get(self.questionnaire_edit_url)
        self.hide_notifications()
        self.findManyBy('link_text', 'Edit this section')[0].click()
        interval = (settings.QUESTIONNAIRE_LOCK_TIME - 1) * 60 * 1000
        self.findBy('xpath', '//*[text()[contains(.,"{}")]]'.format(interval))
