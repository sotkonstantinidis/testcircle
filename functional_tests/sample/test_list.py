from django.core.urlresolvers import reverse
from django.db.models import Q
from unittest.mock import patch

from functional_tests.base import FunctionalTest

from sample.tests.test_views import (
    route_home,
    route_questionnaire_list,
)


class ListTest(FunctionalTest):

    fixtures = [
        'global_key_values.json', 'sample.json', 'unccd.json',
        'sample_questionnaires_5.json']

    def test_list_is_available(self):

        # Alice goes to the main page of the configuration and sees a
        # list with questionnaires
        self.browser.get(self.live_server_url + reverse(
            route_home))

        self.checkOnPage('Last updates')

        # She sees the list contains 3 entries.
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 3)

        # The entries are ordered with the latest changes on top and
        # each entry contains Keys 1 and 5 of the questionnaires.
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 4")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'text()="Faz 4"]')
        link = self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 3")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'text()="Faz 3"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "Foo 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'text()="Faz 2"]')

        # Each entry has a placeholder because there is no image
        for e in list_entries:
            self.findBy(
                'xpath', '//div[contains(@style, "height: 180px")]', base=e)

        # She clicks a link and sees she is taken to the detail page of the
        # questionnaire
        link.click()
        self.checkOnPage('Key 3')
        self.checkOnPage('Bar')

        # She goes to the list page and sees all 4 questionnaires available.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_list))
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 4)

        # The entries are also ordered and each entry contains Keys 1 and 5 of
        # the questionnaires.
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 4")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'text()="Faz 4"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 3")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'text()="Faz 3"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "Foo 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'text()="Faz 2"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "Foo 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'text()="Faz 1"]')

        # Each entry has a placeholder because there is no image
        for e in list_entries:
            self.findBy(
                'xpath', '//div[contains(@style, "height: 180px")]', base=e)

    @patch('sample.views.get_configuration_query_filter')
    def test_list_with_foreign_configuration(self, mock_config_query_filter):
        mock_config_query_filter.return_value = (
            Q(configurations__code='sample') | Q(configurations__code='unccd'))

        # Alice goes to the list and sees that there are 5 questionnaires
        # available (one in UNCCD config)
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_list))

        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 5)

        # The UNCCD entry has a valid key but the attribute [unccd] in front
        # of the title
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/small['
            'text()="[unccd]"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "Foo 5")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'text()="Faz 5"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "Foo 4")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'text()="Faz 4"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "Foo 3")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'text()="Faz 3"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "Foo 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'text()="Faz 2"]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[5]//h1/a['
            'contains(text(), "Foo 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[5]//p['
            'text()="Faz 1"]')
