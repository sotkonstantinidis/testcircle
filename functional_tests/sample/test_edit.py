from django.core.urlresolvers import reverse

from accounts.models import User
from functional_tests.base import FunctionalTest
from questionnaire.models import Questionnaire
from sample.tests.test_views import (
    get_position_of_category,
    route_questionnaire_details,
)

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

    def test_edit_published(self):

        code = 'sample_3'

        # Alice logs in
        user = User.objects.get(pk=101)
        self.doLogin(user=user)

        # She goes to the detail page of a "published" Questionnaire
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
