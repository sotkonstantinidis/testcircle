import re

import time

import pytest
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.test.utils import override_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from unittest.mock import patch

from accounts.models import User
from accounts.tests.test_models import create_new_user
from accounts.tests.test_views import accounts_route_questionnaires
from functional_tests.base import FunctionalTest
from questionnaire.models import Questionnaire
from sample.tests.test_views import (
    route_questionnaire_new,
    route_questionnaire_details,
    get_position_of_category)
from wocat.tests.test_views import route_home
from search.tests.test_index import create_temp_indices

from functional_tests.pages.sample import SampleDetailPage, SampleListPage, \
    SampleNewPage, SampleEditPage


@pytest.mark.usefixtures('es')
@override_settings(
    NOTIFICATIONS_CREATE='create_foo',
    NOTIFICATIONS_CHANGE_STATUS='change_foo'
)
class ModerationTest(FunctionalTest):

    fixtures = [
        'groups_permissions.json',
        'sample_global_key_values.json',
        'sample.json',
    ]

    def setUp(self):
        super(ModerationTest, self).setUp()
        create_temp_indices([('sample', '2015')])

    @patch('questionnaire.signals.create_questionnaire.send')
    @patch('questionnaire.signals.change_status.send')
    def test_questionnaire_permissions(
            self, mock_change_status, mock_create_signal):

        key_1 = 'Foo'
        key_3 = 'Bar'

        user_1 = self.create_new_user(email='user_1@foo.com')
        user_2 = self.create_new_user(email='user_2@foo.com')
        user_moderator = self.create_new_user(
            email='moderator@foo.com', groups=['Reviewers', 'Publishers'])

        # User 1 logs in and creates a questionnaire
        new_page = SampleNewPage(self)
        new_page.open(login=True, user=user_1)
        new_page.create_new_questionnaire(key_1=key_1, key_3=key_3)

        # A new notification should be created
        mock_create_signal.assert_called_once_with(
            questionnaire=Questionnaire.objects.latest('created'),
            sender='create_foo',
            user=user_1
        )

        # User 1 changes to the view mode
        new_page.view_questionnaire()

        # User 1 refreshes the page and sees the questionnaire
        view_page = SampleDetailPage(self)
        view_page.route_kwargs = {
            'identifier': Questionnaire.objects.latest('pk').code}
        view_page.open()
        view_page.has_text(key_1)

        # User 1 logs out and cannot see the questionnaire
        view_page.logout()
        view_page.open()
        assert new_page.is_not_found_404()

        # User 2 logs in and cannot see the questionnaire
        view_page.open(login=True, user=user_2)
        assert view_page.is_not_found_404()

        # Moderator logs in and cannot see the questionnaire
        view_page.open(login=True, user=user_moderator)
        assert view_page.is_not_found_404()

        # User 1 submits the questionnaire
        view_page.open(login=True, user=user_1)
        view_page.submit_questionnaire()

        # A notification for the new status is created
        mock_change_status.assert_called_once_with(
            message='',
            questionnaire=Questionnaire.objects.latest('created'),
            sender='change_foo',
            user=user_1
        )

        # User 1 logs out and cannot see the questionnaire
        view_page.logout()
        view_page.open()
        assert view_page.is_not_found_404()

        # User 2 logs in and cannot see the questionnaire
        view_page.open(login=True, user=user_2)
        assert view_page.is_not_found_404()

        # Moderator logs in and sees the questionnaire
        view_page.open(login=True, user=user_moderator)
        assert view_page.has_text(key_1)

        # Moderator publishes the questionnaire
        view_page.review_questionnaire()
        view_page.publish_questionnaire()

        # The moderator cannot create a new version
        assert not view_page.can_create_new_version()

        # Logged out users can see the questionnaire
        view_page.logout()
        view_page.open()
        assert view_page.has_text(key_1)

        # Logged out users cannot create a new version
        assert not view_page.can_create_new_version()

        # User 2 cannot edit the questionnaire
        view_page.open(login=True, user=user_2)
        assert view_page.has_text(key_1)
        assert not view_page.can_create_new_version()

        # User 1 can edit the questionnaire
        view_page.open(login=True, user=user_1)
        assert view_page.has_text(key_1)
        assert view_page.can_create_new_version()


@pytest.mark.usefixtures('es')
class ModerationTestFixture(FunctionalTest):

    fixtures = [
        'groups_permissions.json',
        'sample_global_key_values.json',
        'sample.json',
        'sample_questionnaire_status.json',
        'sample_user.json',
    ]

    def setUp(self):
        super(ModerationTestFixture, self).setUp()
        create_temp_indices([('sample', '2015')])

        self.user_compiler = User.objects.get(pk=101)
        self.user_editor = User.objects.get(pk=102)
        self.user_reviewer = User.objects.get(pk=103)
        self.user_publisher = User.objects.get(pk=104)
        self.user_secretariat = User.objects.get(pk=107)

        self.sample_2_text = 'Foo 2'

    def test_review_locked_questionnaire(self):
        # Secretariat user logs in and goes to the details of a SUBMITTED
        # questionnaire
        detail_page = SampleDetailPage(self)
        detail_page.route_kwargs = {'identifier': 'sample_2'}
        detail_page.open(login=True, user=self.user_secretariat)
        assert detail_page.has_text(self.sample_2_text)

        # User starts to edit the first section (this sets a lock on the
        # questionnaire)
        detail_page.edit_questionnaire()
        edit_page = SampleEditPage(self)
        edit_page.click_edit_category(edit_page.CATEGORIES[0][0])

        # User goes back to the details (without saving!)
        detail_page.open()

        # User reviews the questionnaire and sees there is no exception thrown
        detail_page.review_questionnaire()

        # He sees the questionnaire is now reviewed
        detail_page.check_status('reviewed')

    def test_review_locked_questionnaire_blocked_by_other(self):

        # Reviewer logs in
        self.doLogin(user=self.user_reviewer)

        # He goes to the details of a SUBMITTED questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_2'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 2")]]')

        # He starts to edit the first section (this sets a lock on the
        # questionnaire)
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        self.click_edit_section('cat_1')

        # Secretariat user logs in
        self.doLogin(user=self.user_secretariat)

        # He goes to the details of a SUBMITTED questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_2'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 2")]]')

        # He reviews the questionnaire which is still locked and sees there is
        # no exception thrown, however she sees a warning.
        self.review_action('review', expected_msg_class='warning')

        # He sees the questionnaire is still submitted
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

    def test_secretariat_edit(self):

        # Secretariat user logs in
        self.doLogin(user=self.user_secretariat)

        # He goes to the details of a DRAFT questionnaire which he did not enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_1'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 1")]]')

        # He sees a button to edit the questionnaire, he clicks it
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()

        # In edit mode, he sees that he can edit the first section
        self.click_edit_section('cat_1')

        # He saves the step and returns
        self.submit_form_step()

        # He also opens a public questionnaire which he did not enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_3'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 3")]]')

        # In the database, there is only 1 version
        self.assertEqual(
            Questionnaire.objects.filter(code='sample_3').count(), 1)

        # He sees a button to edit the questionnaire, he clicks it and creates a
        # new version
        self.findBy('xpath', '//form[@id="review_form"]')
        self.review_action('edit')

        # In edit mode, he sees that he can edit the first section
        self.click_edit_section('cat_1')

        # He saves the step and returns
        self.submit_form_step()

        # In the database, there are now 2 versions
        self.assertEqual(
            Questionnaire.objects.filter(code='sample_3').count(), 2)

    def test_secretariat_delete(self):
        # Secretariat user logs in
        self.doLogin(user=self.user_secretariat)

        # He goes to the details of a DRAFT questionnaire which he did not enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_1'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 1")]]')
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')

        # He sees a button to delete the questionnaire
        self.review_action('delete')

        # He sees that he has been redirected to the "My SLM Practices" page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(accounts_route_questionnaires) + '#top')

        # He goes to the details of a SUBMITTED questionnaire which he did not
        # enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_2'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 2")]]')
        self.findBy('xpath', '//span[contains(@class, "is-submitted")]')

        # He sees a button to delete the questionnaire
        self.review_action('delete')

        # He sees that he has been redirected to the "My SLM Practices" page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(accounts_route_questionnaires) + '#top')

        # He goes to the details of a REVIEWED questionnaire which he did not
        # enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_7'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 7")]]')
        self.findBy('xpath', '//span[contains(@class, "is-reviewed")]')

        # He sees a button to delete the questionnaire
        self.review_action('delete')

        # He sees that he has been redirected to the "My SLM Practices" page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(accounts_route_questionnaires) + '#top')

        # He also opens a PUBLIC questionnaire which he did not enter
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_3'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 3")]]')
        self.findByNot('xpath', '//span[contains(@class, "is-draft")]')
        self.findByNot('xpath', '//span[contains(@class, "is-submitted")]')
        self.findByNot('xpath', '//span[contains(@class, "is-reviewed")]')

        # In the database, there is only 1 version
        self.assertEqual(
            Questionnaire.objects.filter(code='sample_3').count(), 1)

        # He sees a button to edit the questionnaire, he clicks it and creates a
        # new version
        self.findBy('xpath', '//form[@id="review_form"]')
        self.review_action('delete')

        # He sees that he has been redirected to the "My SLM Practices" page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(accounts_route_questionnaires) + '#top')

        # In the database, there is still only 1 version
        self.assertEqual(
            Questionnaire.objects.filter(code='sample_3').count(), 1)

        # He opens another PUBLIC questionnaire and edits it
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': 'sample_5'}))
        self.findBy('xpath', '//*[text()[contains(.,"Foo 5")]]')
        self.findByNot('xpath', '//span[contains(@class, "is-draft")]')
        self.findByNot('xpath', '//span[contains(@class, "is-submitted")]')
        self.findByNot('xpath', '//span[contains(@class, "is-reviewed")]')
        self.review_action('edit')
        self.click_edit_section('cat_1')
        self.submit_form_step()

        # He deletes the newly created draft version
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')
        self.review_action('delete')

        # He sees that he has been redirected to the PUBLIC version of the
        # questionnaire, not the "My SLM Practices" page
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(
                route_questionnaire_details,
                kwargs={'identifier': 'sample_5'}) + '#top')
        self.findBy('xpath', '//*[text()[contains(.,"Foo 5")]]')
        self.findByNot('xpath', '//span[contains(@class, "is-draft")]')
        self.findByNot('xpath', '//span[contains(@class, "is-submitted")]')
        self.findByNot('xpath', '//span[contains(@class, "is-reviewed")]')

        # He creates another version by editing it
        self.review_action('edit')
        self.click_edit_section('cat_1')
        self.submit_form_step()

        # This time, he publishes the new version
        self.review_action('view')
        self.review_action('submit')
        self.review_action('review')
        self.review_action('publish')

        # Now he deletes it
        self.review_action('delete')

        # He is now redirected to the "My SLM Practices" page as there is no
        # version to show
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + reverse(accounts_route_questionnaires) + '#top')

    def test_review_panel(self):

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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_only=True)
        self.review_action('review', exists_not=True)
        self.review_action('publish', exists_not=True)

        # She is on the detail page and does not see the buttons to edit each
        # section
        self.click_edit_section('cat_0', exists_not=True)

        # She goes to the edit page and now she sees the buttons as well as a
        # button to view the questionnaire
        self.findBy('xpath', '//a[contains(text(), "Edit")]').click()
        time.sleep(0.5)

        self.click_edit_section('cat_0', return_button=True)
        self.review_action('view', exists_only=True)

        # She submits the questionnaire to review
        self.review_action('delete', exists_only=True)
        self.review_action('submit')

        # The questionnaire is now pending for review. The review panel
        # is visible but Compiler cannot do any actions.
        self.findBy('xpath', '//form[@id="review_form"]')
        self.findByNot('xpath', '//a[contains(text(), "Edit")]')
        self.review_action('edit', exists_not=True)
        self.review_action('submit', exists_not=True)
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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
        self.review_action('delete', exists_not=True)
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

    @override_settings(
        NOTIFICATIONS_ADD_MEMBER='add_member',
        NOTIFICATIONS_REMOVE_MEMBER='delete_member'
    )
    @patch('questionnaire.signals.change_member.send')
    def test_secretariat_can_assign_reviewer(self, mock_member_change):

        identifier = 'sample_2'

        # A user logs in
        self.doLogin(user=self.user_editor)

        # He goes to a submitted questionnaire
        url = self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}
        )
        self.browser.get(url)
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

        self.findBy('id', 'review-search-user').send_keys('vonlanthen')
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

        # Two notifications are created
        self.assertEqual(mock_member_change.call_count, 2)
        mock_member_change.assert_called_with(
            sender='add_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(email='lukas.vonlanthen@cde.unibe.ch'),
            role='reviewer'
        )
        mock_member_change.reset_mock()

        # She sees the users were added
        assigned_users = self.findManyBy(
            'xpath', '//div[@id="review-list-assigned-users"]/ul/li')
        self.assertEqual(len(assigned_users), 2)
        users = [self.get_text_excluding_children(user).strip() for user in
                 assigned_users]
        self.assertEqual(sorted(users), ['Kurt Gerber', 'Lukas Vonlanthen'])
        self.assertNotEqual(users[0], users[1])

        # She edits the users again
        self.findBy(
            'xpath', '//a[contains(@class, "js-toggle-edit-assigned-users")]').\
            click()
        selected_users = self.findManyBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box")]')
        self.assertEqual(len(selected_users), 2)
        users = [self.get_text_excluding_children(user).strip() for user in
                 selected_users]
        self.assertEqual(sorted(users), ['Kurt Gerber', 'Lukas Vonlanthen'])
        self.assertNotEqual(users[0], users[1])

        # She removes one of the user
        remove_button = self.findBy(
            'xpath', '//div[@id="review-new-user"]/div[contains(@class, '
                     '"alert-box") and contains(text(), "Kurt Gerber")]/a'
        )
        delete_user = re.findall('\d+', remove_button.get_attribute('onclick'))

        self.hide_notifications()
        remove_button.click()
        selected_users = self.findManyBy(
            'xpath',
            '//div[@id="review-new-user"]/div[contains(@class, "alert-box")]'
        )

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
        users = [self.get_text_excluding_children(user).strip() for user in
                 selected_users]
        self.assertEqual(sorted(users), ['Lukas Vonlanthen', 'Sebastian Manger'])
        self.assertNotEqual(users[0], users[1])

        # She updates the users
        btn = self.findBy('id', 'button-assign')
        self.scroll_to_element(btn)
        btn.click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the users were added
        assigned_users = self.findManyBy(
            'xpath', '//div[@id="review-list-assigned-users"]/ul/li')
        self.assertEqual(len(assigned_users), 2)
        users = [self.get_text_excluding_children(user).strip() for user in
                 assigned_users]
        self.assertEqual(sorted(users), ['Lukas Vonlanthen', 'Sebastian Manger'])
        self.assertNotEqual(users[0], users[1])

        # Users are deleted after submitting the page
        self.browser.get(url)
        mock_member_change.assert_called_with(
            sender='delete_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(id=delete_user[-1]),
            role='reviewer'
        )

    @override_settings(
        NOTIFICATIONS_ADD_MEMBER='add_member',
        NOTIFICATIONS_REMOVE_MEMBER='delete_member',
        QUESTIONNAIRE_COMPILER = 'compiler',
        QUESTIONNAIRE_EDITOR = 'editor'
    )
    @patch('questionnaire.signals.change_member.send')
    def test_secretariat_can_assign_reviewer_2(self, mock_member_change):

        identifier = 'sample_3'
        editor = 'Faz Taz'
        old_compiler = 'Foo Bar'
        old_compiler_id = 101
        new_compiler_1 = 'test2 wocat'
        new_compiler_1_id = 3034
        new_compiler_2 = 'test3 wocat'
        new_compiler_2_id = 3035

        # User (publisher) opens the details of a public questionnaire
        detail_page = SampleDetailPage(self)
        detail_page.route_kwargs = {'identifier': identifier}
        detail_page.open(login=True, user=self.user_publisher)

        # User (publisher) sees he can neither edit nor change compiler
        assert not detail_page.can_create_new_version()
        assert not detail_page.can_change_compiler()
        assert not detail_page.can_delete_questionnaire()

        # User (secretariat) opens the details of a public questionnaire
        detail_page.route_kwargs = {'identifier': identifier}
        detail_page.open(login=True, user=self.user_secretariat)

        # User (secretariat) can edit and review and assign users
        assert detail_page.can_create_new_version()
        assert detail_page.can_change_compiler()
        assert detail_page.can_delete_questionnaire()

        # The compiler and the editors are correct.
        assert detail_page.get_compiler() == old_compiler
        assert detail_page.get_editors() == [editor]

        # User goes to the list view and sees the compiler there
        list_page = SampleListPage(self)
        list_page.open()

        list_results = [
            {
            },
            {
                'title': 'Foo 3',
                'compiler': old_compiler
            }
        ]
        list_page.check_list_results(list_results)

        # User goes back to the questionnaire details
        detail_page.open()
        detail_page.hide_notifications()

        # User changes compiler but does not enter a name
        detail_page.open_change_compiler_panel()
        detail_page.click_change_compiler()

        # No notifications were created
        self.assertEqual(mock_member_change.call_count, 0)
        assert detail_page.has_error_message(
            detail_page.TEXT_MESSAGE_NO_VALID_NEW_COMPILER)
        detail_page.hide_notifications()

        # User selects a new compiler
        detail_page.change_compiler(new_compiler_1, submit=False)

        # The new compiler is listed
        assert detail_page.get_selected_compilers() == [new_compiler_1]

        # User confirms and sees a success message
        detail_page.click_change_compiler()
        assert detail_page.has_success_message(
            detail_page.TEXT_MESSAGE_COMPILER_CHANGED)

        # Two notifications were created
        self.assertEqual(mock_member_change.call_count, 2)
        mock_member_change.assert_any_call(
            sender='delete_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(pk=old_compiler_id),
            role='compiler'
        )
        mock_member_change.assert_any_call(
            sender='add_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(pk=new_compiler_1_id),
            role='compiler'
        )
        mock_member_change.reset_mock()

        # The new compiler is visible in the details, editor did not change
        assert detail_page.get_compiler() == new_compiler_1
        assert detail_page.get_editors() == [editor]

        # In the list, the new compiler is visible
        list_page.open()
        list_results = [
            {
            },
            {
                'title': 'Foo 3',
                'compiler': new_compiler_1
            }
        ]
        list_page.check_list_results(list_results)

        # In the details page, the user changes the compiler and enters the
        # current compiler once again
        detail_page.open()
        detail_page.hide_notifications()
        detail_page.change_compiler(new_compiler_1, submit=False)

        # The compiler is listed
        assert detail_page.get_selected_compilers() == [new_compiler_1]

        # User confirms and sees an error message
        detail_page.click_change_compiler()
        assert detail_page.has_notice_message(
            detail_page.TEXT_MESSAGE_USER_ALREADY_COMPILER)

        # No notifications were created
        self.assertEqual(mock_member_change.call_count, 0)

        # User changes the compiler yet again.
        detail_page.hide_notifications()
        detail_page.change_compiler(new_compiler_2, submit=False)
        assert detail_page.get_selected_compilers() == [new_compiler_2]

        # User sees the search box is now disabled
        assert not detail_page.can_enter_new_compiler()

        # User marks the checkbox which keeps the old compiler as editor
        detail_page.select_keep_compiler_as_editor()

        detail_page.click_change_compiler()
        assert detail_page.has_success_message(
            detail_page.TEXT_MESSAGE_COMPILER_CHANGED)

        # Three notifications were created
        self.assertEqual(mock_member_change.call_count, 3)
        mock_member_change.assert_any_call(
            sender='delete_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(pk=new_compiler_1_id),
            role='compiler'
        )
        mock_member_change.assert_any_call(
            sender='add_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(pk=new_compiler_2_id),
            role='compiler'
        )
        mock_member_change.assert_any_call(
            sender='add_member',
            questionnaire=Questionnaire.objects.get(code=identifier),
            user=self.user_secretariat,
            affected=User.objects.get(pk=new_compiler_1_id),
            role='editor'
        )
        mock_member_change.reset_mock()

        # The new compiler is visible in the details
        assert detail_page.get_compiler() == new_compiler_2

        # The old compiler is now an editor
        assert new_compiler_1 in detail_page.get_editors()

        list_page.open()
        list_results = [
            {
            },
            {
                'title': 'Foo 3',
                'compiler': new_compiler_2
            }
        ]
        list_page.check_list_results(list_results)

    def test_reviewer_can_edit_questionnaire(self):

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
        self.hide_notifications()
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

    def test_reviewer_can_reject_questionnaire(self):

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
        self.assertEqual(self.browser.current_url, home_url + '#top')

        # User 102 (the compiler of the questionnaire) logs in
        self.doLogin(user=self.user_editor)

        # He sees the questionnaire and sees it is draft.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')

    def test_publishers_can_edit_questionnaire(self):

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
        self.hide_notifications()
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

    def test_publisher_can_reject_questionnaire(self):

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
        self.assertEqual(self.browser.current_url, home_url + '#top')

        # User 102 (the compiler of the questionnaire) logs in
        self.doLogin(user=self.user_compiler)

        # He sees the questionnaire and sees it is draft.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_details, kwargs={'identifier': identifier}))
        self.findBy('xpath', '//span[contains(@class, "is-draft")]')
