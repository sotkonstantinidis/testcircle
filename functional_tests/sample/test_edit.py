from django.core.urlresolvers import reverse

from accounts.models import User
from functional_tests.base import FunctionalTest
from questionnaire.models import Questionnaire
from sample.tests.test_views import (
    get_position_of_category,
    route_home,
    route_questionnaire_details,
    route_questionnaire_new,
)

from django.contrib.auth.models import Group
from accounts.tests.test_models import create_new_user
from nose.plugins.attrib import attr
# @attr('foo')

cat_1_position = get_position_of_category('cat_1', start0=True)


class EditTest(FunctionalTest):

    fixtures = [
        'groups_permissions.json', 'global_key_values.json', 'sample.json',
        'sample_questionnaire_status.json']

    """
    id: 1   code: sample_1   version: 1   status: 1   user: 101
    id: 2   code: sample_2   version: 1   status: 2   user: 102
    id: 3   code: sample_3   version: 1   status: 3   user: 101, 102
    id: 4   code: sample_4   version: 1   status: 4   user: 101
    id: 5   code: sample_5   version: 1   status: 5   user: 101
    id: 6   code: sample_5   version: 2   status: 3   user: 101
    id: 7   code: sample_6   version: 1   status: 1   user: 103
    """

    def test_creation_date_does_not_change(self):

        # Alice logs in
        user = User.objects.get(pk=102)
        self.doLogin(user=user)

        # She goes to the details of an existing questionnaire and takes
        # note of the creation and update dates
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_3'}))
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-output-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        creation_date = dates[0].text
        update_date = dates[1].text

        # She edits the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/sample_3/cat")]')[
                cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the changes were submitted
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # She notices that the creation date did not change while the
        # update date changed.
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-output-infos")]/li/time')
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
            'xpath', '//ul[contains(@class, "tech-output-infos")]/li/time')
        self.assertEqual(len(dates), 2)
        creation_date = dates[0].text
        update_date = dates[1].text

        # She makes an edit
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/sample_1/cat")]')[
                cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the changes were submitted
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # She notices that the creation date did not change while the
        # update date changed.
        dates = self.findManyBy(
            'xpath', '//ul[contains(@class, "tech-output-infos")]/li/time')
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
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/{}/cat")]'.format(code))[
                cat_1_position].click()
        self.assertIn(code, self.browser.current_url)

        # She makes some changes and submits the category
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        key_1.clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('asdf')
        self.findBy('id', 'button-submit').click()

        # She is back on the overview page and sees that the URL still
        # contains the code of the Questionnaire
        self.assertIn(code, self.browser.current_url)

        # She submits the Questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees that no new code was created.
        self.assertIn(code, self.browser.current_url)

        # She sees that the value of Key 1 was updated
        self.findByNot('xpath', '//*[text()[contains(.,"Foo 1")]]')
        self.findBy('xpath', '//*[text()[contains(.,"asdf")]]')

        # Also there was no additional version created in the database
        self.assertEqual(Questionnaire.objects.count(), 7)

    def test_edit_public(self):

        code = 'sample_3'

        # Alice logs in
        user = User.objects.get(pk=101)
        self.doLogin(user=user)

        # She goes to the detail page of a "public" Questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': code}))
        self.assertIn(code, self.browser.current_url)

        self.findBy('xpath', '//*[text()[contains(.,"Foo 3")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"asdf")]]')

        # She edits the Questionnaire and sees that the URL contains the
        # code of the Questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.assertIn(code, self.browser.current_url)

        #  She edits a category and sees that the URL still contains the
        # code of the Questionnaire
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/{}/cat")]'.format(code))[
                cat_1_position].click()
        self.assertIn(code, self.browser.current_url)

        # She makes some changes and submits the category
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        key_1.clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('asdf')
        self.findBy('id', 'button-submit').click()

        # She is back on the overview page and sees that the URL still
        # contains the code of the Questionnaire
        self.assertIn(code, self.browser.current_url)

        # She submits the Questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees that no new code was created.
        self.assertIn(code, self.browser.current_url)

        # She sees that the value of Key 1 was updated
        self.findByNot('xpath', '//*[text()[contains(.,"Foo 3")]]')
        self.findBy('xpath', '//*[text()[contains(.,"asdf")]]')

        # Also there was an additional version created in the database
        self.assertEqual(Questionnaire.objects.count(), 8)

        # The newly created version has the same code
        self.assertEqual(Questionnaire.objects.filter(code=code).count(), 2)

        # She goes to the home page and sees the list of last updates
        # where sample_3 appears only once.
        self.browser.get(self.live_server_url + reverse(route_home))

        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 3)

        self.findBy(
            'xpath', '//a[contains(text(), "asdf")]',
            base=list_entries[0])
        self.findBy(
            'xpath', '//a[contains(text(), "Foo 6")]',
            base=list_entries[1])
        self.findBy(
            'xpath', '//a[contains(text(), "Foo 1")]',
            base=list_entries[2])

        # She clicks the first entry and sees that she is taken to the
        # details page of the latest (pending) version.
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "asdf")]').click()
        self.checkOnPage('asdf')

    def test_edit_questionnaire(self):

        user = create_new_user(id=6, email='mod@bar.com')
        user.groups = [Group.objects.get(pk=3)]
        user.save()

        # Alice logs in
        self.doLogin(user=user)

        # She enters a Questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(@href, "edit/new/cat")]')
        edit_buttons[cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She saves it as draft
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She submits it for review
        self.findBy('xpath', '//input[@name="submit"]').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She publishes it
        self.findBy('xpath', '//input[@name="publish"]').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees it is public and visible
        self.findBy('xpath', '//p[text()="Foo"]')
        self.findBy('xpath', '//p[text()="Bar"]')

        url = self.browser.current_url

        # She edits it
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.findBy(
            'xpath', '(//a[contains(text(), "Edit this section")])[2]').click()

        # She changes some values
        self.findBy('name', 'qg_1-0-original_key_1').clear()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('asdf')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She saves it as draft
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She is taken to the overview page where she sees the latest
        # (pending) changes of the draft

        self.assertEqual(url, self.browser.current_url)

        self.findBy('xpath', '//p[text()="Bar"]')
        self.findByNot('xpath', '//p[text()="Foo"]')
        self.findBy('xpath', '//p[text()="asdf"]')
