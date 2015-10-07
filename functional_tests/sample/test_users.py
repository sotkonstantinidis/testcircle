from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from accounts.models import User
from accounts.tests.test_views import accounts_route_questionnaires

from nose.plugins.attrib import attr
# @attr('foo')


class UserTest(FunctionalTest):

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

    def test_user_questionnaires(self):

        user_alice = User.objects.get(pk=101)
        user_bob = User.objects.get(pk=102)

        # Alice logs in
        self.doLogin(user=user_alice)

        # She sees and clicks the link in the user menu to view her
        # Questionnaires
        self.findBy(
            'xpath', '//li[contains(@class, "has-dropdown")]/ul/li/a['
            'contains(@href, "accounts/101/questionnaires")]').click()

        # She sees here Questionnaires are listed, even those with
        # status draft or pending
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 4)
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 6")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 4")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "Foo 3")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "Foo 1")]')

        # She sees a customized title of the list
        self.findBy('xpath', '//h2[contains(text(), "Your Questionnaires")]')
        self.findByNot(
            'xpath', '//h2[contains(text(), "Questionnaires by Foo Bar")]')

        # She goes to the questionnaire page of Bob and sees the
        # Questionnaires of Bob but only the "public" ones.
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires, kwargs={'user_id': 102}))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 1)
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 3")]')

        # She logs out and sees the link in the menu is no longer visible.
        self.doLogout()
        self.findByNot(
            'xpath', '//li[contains(@class, "has-dropdown")]/ul/li/a['
            'contains(@href, "accounts/101/questionnaires")]')

        # On her Questionnaire page only the "public" Questionnaires are
        # visible.
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires, kwargs={'user_id': 101}))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 2)
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 6")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 3")]')

        # Bob logs in and goes to his Questionnaire page. He sees all
        # versions of his Questionnaires.
        self.doLogin(user=user_bob)
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires, kwargs={'user_id': 102}))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 2)
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 3")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 2")]')

        # He goes to the Questionnaire page of Alice and only sees the
        # "public" Questionnaires.
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires, kwargs={'user_id': 101}))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 2)
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 6")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 3")]')

        # He sees that the customized title of the list now changed.
        self.findByNot(
            'xpath', '//h2[contains(text(), "Your Questionnaires")]')
        self.findBy(
            'xpath', '//h2[contains(text(), "Questionnaires by Foo Bar")]')

        # He goes to the Questionnaire page of Chris and sees no
        # "public" Questionnaires with an appropriate message.
        self.browser.get(self.live_server_url + reverse(
            accounts_route_questionnaires, kwargs={'user_id': 103}))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 0)
        self.findBy(
            'xpath', '//p[@class="questionnaire-list-empty" and contains('
            'text(), "No WOCAT and UNCCD SLM practices found.")]')
