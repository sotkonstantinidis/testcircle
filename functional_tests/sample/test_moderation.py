import time
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.test.utils import override_settings

from accounts.tests.test_models import create_new_user
from functional_tests.base import FunctionalTest
from sample.tests.test_views import (
    route_questionnaire_new,
    route_questionnaire_list,
    get_position_of_category,
)
from search.index import delete_all_indices
from search.tests.test_index import create_temp_indices


from nose.plugins.attrib import attr
# @attr('foo')

TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class ModerationTest(FunctionalTest):

    fixtures = ['groups_permissions.json', 'sample.json']

    def setUp(self):
        super(ModerationTest, self).setUp()
        delete_all_indices()
        create_temp_indices(['sample'])

    def tearDown(self):
        super(ModerationTest, self).tearDown()
        delete_all_indices()

    def test_enter_questionnaire_review_panel(self):

        # Alice logs in
        user = create_new_user()
        user_moderator = create_new_user(id=2, email='foo@bar.com')
        user_moderator.groups = [Group.objects.get(pk=3)]
        user_moderator.save()

        self.doLogin(user=user)

        cat_1_position = get_position_of_category('cat_1', start0=True)

        # She goes directly to the Sample questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))

        # She does not see the review panel
        self.findByNot('xpath', '//ol[@class="process"]')

        # She enters some values
        edit_buttons = self.findManyBy(
            'xpath', '//a[contains(@href, "edit/new/cat")]')
        edit_buttons[cat_1_position].click()
        # She enters Key 1
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()

        # She sees that she was redirected to the overview page and is
        # shown a success message
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//h3[contains(text(), "Subcategory 1_1")]')
        self.findBy('xpath', '//*[text()[contains(.,"Key 1")]]')
        self.findBy('xpath', '//*[text()[contains(.,"Foo")]]')
        self.findBy('xpath', '//*[text()[contains(.,"Bar")]]')

        # She still does not see the review panel
        self.findByNot('xpath', '//ol[@class="process"]')

        # She submits the form and now sees the review panel
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//ol[@class="process"]')

        overview_url = self.browser.current_url

        # She does not see the "publish" button
        self.findByNot('xpath', '//input[@name="publish"]')

        # Instead, she sees a button to submit the draft. She clicks the
        # button.
        self.findBy('xpath', '//input[@name="submit"]').click()

        # She sees that she is still back on the overview page but this
        # time, there is no "submit" button. There is no "Publish"
        # button either.
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.assertIn(self.browser.current_url, overview_url)
        self.findByNot('xpath', '//input[@name="publish"]')
        self.findByNot('xpath', '//input[@name="submit"]')

        # MODERATOR
        # Bob logs in
        self.doLogin(user=user_moderator)

        # He goes to the list view and sees that the questionnaire is
        # not there yet because it is not "published".
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_list))
        self.findByNot('xpath', '//article[1]//h1/a[text()="Foo"]')

        # He goes to the newly created questionnaire
        self.browser.get(overview_url)
        time.sleep(1)

        # The moderator sees the "publish" button and clicks it
        self.findBy('xpath', '//input[@name="publish"]').click()

        # There is no review panel anymore.
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findByNot('xpath', '//ol[@class="process"]')

        # He goes to the list view and sees that the questionnaire is now there
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_list))
        self.findBy('xpath', '//article[1]//h1/a[text()="Foo"]')
