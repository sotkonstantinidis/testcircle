import time
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from unittest.mock import patch

from accounts.client import Typo3Client
from accounts.models import User
from accounts.tests.test_models import create_new_user
from functional_tests.base import FunctionalTest
from sample.tests.test_views import (
    route_home,
    route_questionnaire_new,
    route_questionnaire_details,
    get_position_of_category,
)
from search.index import delete_all_indices
from search.tests.test_index import create_temp_indices


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
@patch.object(Typo3Client, 'get_user_id')
class ModerationTest(FunctionalTest):

    fixtures = [
        'groups_permissions.json', 'sample_global_key_values.json',
        'sample.json']

    def setUp(self):
        super(ModerationTest, self).setUp()
        delete_all_indices()
        create_temp_indices(['sample'])

    def tearDown(self):
        super(ModerationTest, self).tearDown()
        delete_all_indices()

    def test_questionnaire_permissions(self, mock_get_user_id):

        cat_1_position = get_position_of_category('cat_1', start0=True)

        user_alice = create_new_user()
        user_bob = create_new_user(id=2, email='bob@bar.com')
        user_moderator = create_new_user(id=3, email='foo@bar.com')
        user_moderator.groups = [
            Group.objects.get(pk=3), Group.objects.get(pk=4)]
        user_moderator.save()

        # Alice logs in
        self.doLogin(user=user_alice)

        # She creates a questionnaire and saves it
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        edit_buttons = self.findManyBy(
            'xpath', '//main//a[contains(@href, "edit/new/cat")]')
        edit_buttons[cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She changes to the view mode
        self.review_action('view')
        url = self.browser.current_url

        # She refreshes the page and sees the questionnaire
        self.browser.get(url)
        self.checkOnPage('Foo')

        # She logs out and cannot see the questionnaire
        self.doLogout()
        self.browser.get(url)
        self.checkOnPage('404')

        # Bob logs in and cannot see the questionnaire
        self.doLogin(user=user_bob)
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[contains(text(), '404')]")))
        # self.checkOnPage('404')

        # The moderator logs in and cannot see the questionnaire
        self.doLogin(user=user_moderator)
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[contains(text(), '404')]")))

        # Alice submits the questionnaire
        self.doLogin(user=user_alice)
        self.browser.get(url)
        self.review_action('submit')

        # She logs out and cannot see the questionnaire
        self.doLogout()
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[contains(text(), '404')]")))

        # Bob logs in and cannot see the questionnaire
        self.doLogin(user=user_bob)
        self.browser.get(url)
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//span[contains(text(), '404')]")))

        # The moderator logs in and sees the questionnaire
        self.doLogin(user=user_moderator)
        self.browser.get(url)
        self.checkOnPage('Foo')

        # He publishes the questionnaire
        self.review_action('review')
        self.review_action('publish')

        # The moderator cannot edit the questionnaire
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')

        # Logged out users can see the questionnaire
        self.doLogout()
        self.browser.get(url)
        self.checkOnPage('Foo')

        # Logged out users cannot edit the questionnaire
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')

        # Bob cannot edit the questionnaire
        self.doLogin(user=user_bob)
        self.browser.get(url)
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')

        # Alice can edit the questionnaire
        self.doLogin(user=user_alice)
        self.browser.get(url)
        self.checkOnPage('Foo')
        self.review_action('edit', exists_only=True)


@patch.object(Typo3Client, 'get_user_id')
class ModerationTestFixture(FunctionalTest):

    fixtures = [
        'groups_permissions.json', 'sample_global_key_values.json',
        'sample.json', 'sample_questionnaire_status.json']

    def setUp(self):
        super(ModerationTestFixture, self).setUp()
        delete_all_indices()
        create_temp_indices(['sample'])

        self.user_compiler = User.objects.get(pk=101)
        self.user_editor = User.objects.get(pk=102)
        self.user_reviewer = User.objects.get(pk=103)
        self.user_publisher = User.objects.get(pk=104)
        self.user_secretariat = User.objects.get(pk=107)

    def tearDown(self):
        super(ModerationTestFixture, self).tearDown()
        delete_all_indices()

    def test_review_panel(self, mock_get_user_id):

        # Editor logs in
        self.doLogin(user=self.user_editor)

        # He goes to the details of a questionnaire which he did not enter.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_5'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 5")]]')

        # He does see the review panel but no actions are possible
        self.findBy('xpath', '//form[@id="review_form"]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # He sees that there is no edit button for him.
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')

        # He goes to the details of a questionnaire where he is editor.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_3'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 3")]]')

        # He does see the review panel but can only edit
        self.findBy('xpath', '//form[@id="review_form"]')
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # He sees a button to edit the questionnaire and clicks on it.
        self.review_action('edit')

        # He makes some changes and saves the questionnaire
        self.findBy(
            'xpath', '(//a[contains(text(), "Edit this section")])[2]').click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (by Editor)')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # He sees a review panel but he does not see the button to
        # submit the questionnaire for review
        self.findBy('xpath', '//form[@id="review_form"]')
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # He sees the buttons to edit each section
        self.click_edit_section('cat_0', return_button=True)

        self.review_action('view')
        url_details = self.browser.current_url

        # He does not see the button to edit each section anymore
        self.click_edit_section('cat_0', exists_not=True)

        # Compiler logs in
        self.doLogin(user=self.user_compiler)

        # She also goes to the details page of the questionnaire and
        # she does see the button to submit the questionnaire for
        # review.
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findBy('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # She is on the detail page and does not see the buttons to edit each
        # section
        self.click_edit_section('cat_0', exists_not=True)

        # She goes to the edit page and now she sees the buttons as well as a
        # button to view the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.click_edit_section('cat_0', return_button=True)
        self.review_action('view', exists_only=True)

        # She submits the questionnaire to review
        self.review_action('submit')

        # The questionnaire is now pending for review. The review panel
        # is visible but Compiler cannot do any actions.
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # Editor logs in
        self.doLogin(user=self.user_editor)
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)

        # He goes to the page and he also sees the review panel but no
        # actions can be taken.
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # Reviewer logs in.
        self.doLogin(user=self.user_reviewer)
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)

        # He goes to the page and sees the review panel. There is a
        # button to do the review.
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findBy('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_only=True)
        self.review_action('publish', exists_not=True)

        # He is on the detail page and does not see the buttons to edit each
        # section
        self.click_edit_section('cat_0', exists_not=True)
        self.rearrangeStickyMenu()

        # He goes to the edit page and now she sees the buttons as well as a
        # button to view the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.click_edit_section('cat_0', return_button=True)
        self.review_action('view', exists_only=True)

        # He clicks the button to do the review
        self.review_action('review')

        # He sees the review panel but no action is possible.
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # Compiler logs in and goes to the page, sees the review panel
        # but no actions possible
        self.doLogin(user=self.user_compiler)
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # Editor logs in and goes to the page, sees the review panel but
        # no actions possible.
        self.doLogin(user=self.user_editor)
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # Publisher logs in and goes to the page. He sees the review
        # panel with a button to publish.
        self.doLogin(user=self.user_publisher)
        self.browser.get(url_details)
        self.browser.implicitly_wait(3)
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findBy('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_only=True)

        # He is on the detail page and does not see the buttons to edit each
        # section
        self.click_edit_section('cat_0', exists_not=True)

        # He goes to the edit page and now she sees the buttons as well as a
        # button to view the questionnaire
        self.rearrangeStickyMenu()
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.click_edit_section('cat_0', return_button=True)
        self.review_action('view', exists_only=True)

        # He clicks the button to publish the questionnaire.
        self.scroll_to_element(
            self.findBy('xpath', '//form[@id="review_form"]'))
        self.review_action('publish')

        # The review panel is there but he cannot edit
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')

    def test_secretariat_can_assign_reviewer(self, mock_get_user_id):

        identifier = 'sample_2'

        # A user logs in
        self.doLogin(user=self.user_editor)

        # He goes to a submitted questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

        # He sees he can neither edit, review or assign users
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.findByNot('id', 'button-review')
        self.findByNot('id', 'review-list-assigned-users')

        # A reviewer logs in
        self.doLogin(user=self.user_reviewer)

        # He goes to a submitted questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

        # He sees he can edit and review, but not assign users
        self.findBy('xpath', '//a[contains(text(), "Edit")]')
        self.findBy('id', 'button-review')
        self.findByNot('id', 'review-list-assigned-users')

        # Secretariat logs in
        self.doLogin(user=self.user_secretariat)

        # She goes to a submitted questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

        # She sees he can edit and review and assign users
        self.findBy('xpath', '//a[contains(text(), "Edit")]')
        self.findBy('id', 'button-review')
        self.findBy('id', 'review-list-assigned-users')

        # She decides to add two users as reviewers
        self.findBy(
            'xpath', '//a[contains(@class, "js-toggle-edit-assigned-users")]').\
            click()

        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 0)

        self.findBy('id', 'review-search-user').send_keys('kurt')
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ui-menu-item")))
        self.findBy(
            'xpath',
            '//li[@class="ui-menu-item"]//strong[text()="Kurt Gerber"]'
        ).click()

        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 1)

        self.findBy('id', 'review-search-user').send_keys('lukas')
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ui-menu-item")))
        self.findBy(
            'xpath',
            '//li[@class="ui-menu-item"]//strong[text()="Lukas Vonlanthen"]'
        ).click()

        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 2)
        self.assertTrue('Kurt Gerber' in selected_users[0].text)
        self.assertTrue('Lukas Vonlanthen' in selected_users[1].text)

        # She updates the users
        btn = self.findBy('id', 'button-assign')
        self.scroll_to_element(btn)
        btn.click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the users were added
        assigned_users = self.findManyBy(
            'xpath', '//div[@id="review-list-assigned-users"]/ul/li')
        self.assertEqual(len(assigned_users), 2)
        self.assertTrue('Kurt Gerber' in assigned_users[0].text)
        self.assertTrue('Lukas Vonlanthen' in assigned_users[1].text)

        # She edits the users again
        self.findBy(
            'xpath', '//a[contains(@class, "js-toggle-edit-assigned-users")]').\
            click()
        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 2)
        self.assertTrue('Kurt Gerber' in selected_users[0].text)
        self.assertTrue('Lukas Vonlanthen' in selected_users[1].text)

        # She removes one of the user
        self.findBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")][1]/a').click()
        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 1)

        # She adds another user
        self.findBy('id', 'review-search-user').send_keys('sebastian')
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "ui-menu-item")))
        self.findBy(
            'xpath',
            '//li[@class="ui-menu-item"]//strong[text()="Sebastian Manger"]'
        ).click()

        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 2)
        self.assertTrue('Lukas Vonlanthen' in selected_users[0].text)
        self.assertTrue('Sebastian Manger' in selected_users[1].text)

        # She updates the users
        btn = self.findBy('id', 'button-assign')
        self.scroll_to_element(btn)
        btn.click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the users were added
        assigned_users = self.findManyBy(
            'xpath', '//div[@id="review-list-assigned-users"]/ul/li')
        self.assertEqual(len(assigned_users), 2)
        self.assertTrue('Lukas Vonlanthen' in assigned_users[0].text)
        self.assertTrue('Sebastian Manger' in assigned_users[1].text)

    def test_reviewer_can_edit_questionnaire(self, mock_get_user_id):

        cat_1_position = get_position_of_category('cat_1', start0=True)
        identifier = 'sample_2'

        # The moderator logs in
        self.doLogin(user=self.user_reviewer)

        # He goes to a submitted questionnaire and sees that he can edit
        # the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # He changes the name and submits the step
        self.findManyBy(
            'xpath',
            '//main//a[contains(@href, "edit/{}/cat")]'.format(identifier))[
                cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # He sees the changes in the overview and submits the questionnaire
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # He starts editing again
        # self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # He sees there is a message of an old version
        # has_old_version_overview(self)

        # He edits the step again and sees there is now a message of changes
        self.findManyBy(
            'xpath',
            '//main//a[contains(@href, "edit/{}/cat")]'.format(identifier))[
                cat_1_position].click()
        # has_old_version_step(self)
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # He goes back to the overview and reviews the questionnaire
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')
        self.review_action('review')
        self.findBy('xpath', '//span[contains(@class, "is-reviewed")]')

    def test_reviewer_can_reject_questionnaire(self, mock_get_user_id):

        identifier = 'sample_2'

        # The reviewer logs in
        self.doLogin(user=self.user_reviewer)

        # He goes to a submitted questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

        # He sees a button to edit the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]')

        # He sees that he can reject the questionnaire and so he does
        self.review_action('reject')

        # He sees the reject was successful
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # The reviewer has been taken "home" because he has no
        # permission to view or edit the draft questionnaire
        # route_home
        home_url = self.live_server_url + reverse(route_home)
        self.assertEqual(self.browser.current_url, home_url)

        # User 102 (the compiler of the questionnaire) logs in
        self.doLogin(user=self.user_editor)

        # He sees the questionnaire and sees it is draft.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')

    def test_publishers_can_edit_questionnaire(self, mock_get_user_id):

        cat_1_position = get_position_of_category('cat_1', start0=True)
        identifier = 'sample_7'

        # The moderator logs in
        self.doLogin(user=self.user_publisher)

        # He goes to a submitted questionnaire and sees that he can edit
        # the questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # He changes the name and submits the step
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/{}/cat")]'.format(identifier))[
                cat_1_position].click()
        self.findBy('name', 'qg_1-0-original_key_1').send_keys(' (changed)')
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # He sees the changes in the overview and submits the questionnaire
        self.findBy('xpath', '//*[text()[contains(.," (changed)")]]')

        # He starts editing again
        # self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # He sees there is a message of an old version
        # TODO: Basically, the old version should disappear after a compiler
        # saves it.
        # has_old_version_overview(self)

        # He edits the step again and sees there is now a message of changes
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "edit/{}/cat")]'.format(identifier))[
                cat_1_position].click()
        # has_old_version_step(self)
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # He goes back to the overview and reviews the questionnaire
        self.findBy('xpath', '//span[contains(@class, "is-reviewed")]')
        self.review_action('publish')

    def test_publisher_can_reject_questionnaire(self, mock_get_user_id):

        identifier = 'sample_7'

        # The reviewer logs in
        self.doLogin(user=self.user_publisher)

        # He goes to a reviewed questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-reviewed")]')

        # He sees a button to edit the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]')

        # He sees that he can reject the questionnaire and so he does
        self.review_action('reject')

        # The reviewer has been taken "home" because he has no
        # permission to view or edit the draft questionnaire
        # route_home
        home_url = self.live_server_url + reverse(route_home)
        self.assertEqual(self.browser.current_url, home_url)

        # User 102 (the compiler of the questionnaire) logs in
        self.doLogin(user=self.user_compiler)

        # He sees the questionnaire and sees it is draft.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')
