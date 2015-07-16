from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test.utils import override_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from unittest.mock import patch

from functional_tests.base import FunctionalTest

from sample.tests.test_views import (
    route_home,
    route_questionnaire_list,
)
from search.index import delete_all_indices
from search.tests.test_index import create_temp_indices

from nose.plugins.attrib import attr
# @attr('foo')

TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class ListTest(FunctionalTest):

    fixtures = [
        'global_key_values.json', 'sample.json', 'unccd.json',
        'sample_questionnaires_5.json']

    def setUp(self):
        super(ListTest, self).setUp()
        delete_all_indices()
        create_temp_indices(['sample', 'unccd'])

    def tearDown(self):
        super(ListTest, self).tearDown()
        delete_all_indices()

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

    @patch('questionnaire.views.get_configuration_index_filter')
    def test_list_with_foreign_configuration(self, mock_config_index_filter):
        mock_config_index_filter.return_value = ['*']

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
        # self.findBy(
        #     'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
        #     'contains(text(), "Foo 5")]')
        # self.findBy(
        #     'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
        #     'text()="Faz 5"]')
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

    def test_list_database_es(self):

        # She goes to the WOCAT landing page and sees the latest updates
        # (retrieved from database) contains metadata entries
        self.browser.get(self.live_server_url + reverse(route_home))

        entry_xpath = '//article[contains(@class, "tech-item")][1]'
        code = self.findBy(
            'xpath', '{}//dl/dt[text()="ID:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(code.text, 'sample_4')
        creation = self.findBy(
            'xpath', '{}//dl/dt[text()="Creation:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(creation.text, '02/13/2015 5:08 p.m.')
        update = self.findBy(
            'xpath', '{}//dl/dt[text()="Update:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(update.text, '02/13/2015 5:08 p.m.')
        author = self.findBy(
            'xpath', '{}//dl/dt[text()="Author:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(author.text, 'Foo Bar')

        html_1 = self.findBy('xpath', entry_xpath).get_attribute('innerHTML')

        # She also sees that the second entry has two authors (1 author, 1
        # editor)
        entry_xpath = '//article[contains(@class, "tech-item")][2]'
        author = self.findBy(
            'xpath', '{}//dl/dt[text()="Authors:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(author.text, 'Foo Bar, Faz Taz')

        # # She goes to the WOCAT list and sees the list (retrieved from
        # # elasticsearch) also contains metadata information and is
        # # practically identical with the one on the landing page
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_list))

        entry_xpath = '//article[contains(@class, "tech-item")][1]'
        code = self.findBy(
            'xpath', '{}//dl/dt[text()="ID:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(code.text, 'sample_4')
        creation = self.findBy(
            'xpath', '{}//dl/dt[text()="Creation:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(creation.text, '02/13/2015 5:08 p.m.')
        update = self.findBy(
            'xpath', '{}//dl/dt[text()="Update:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(update.text, '02/13/2015 5:08 p.m.')
        author = self.findBy(
            'xpath', '{}//dl/dt[text()="Author:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(author.text, 'Foo Bar')

        html_2 = self.findBy('xpath', entry_xpath).get_attribute('innerHTML')

        # She also sees that the second entry has two authors (1 author, 1
        # editor)
        entry_xpath = '//article[contains(@class, "tech-item")][2]'
        author = self.findBy(
            'xpath', '{}//dl/dt[text()="Authors:"]/following::dd[1]'.format(
                entry_xpath))
        self.assertEqual(author.text, 'Foo Bar, Faz Taz')

        # She sees that both list entries are exactly the same
        self.assertEqual(html_1, html_2)

    # def test_filter_checkbox(self):

    #     # Alice goes to the list view
    #     self.browser.get(self.live_server_url + reverse(
    #         route_questionnaire_list))

    #     # She sees there are 4 Questionnaires in the list
    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 4)

    #     # There is no active filter set
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertFalse(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 0)

    #     # She sees a link for advanced filtering which opens the filter
    #     # panel
    #     filter_panel = self.findBy('id', 'search-advanced')
    #     self.assertFalse(filter_panel.is_displayed())
    #     self.findBy('link_text', 'Advanced filter').click()
    #     self.assertTrue(filter_panel.is_displayed())

    #     # She sees section 2 and below the image checkboxes for values
    #     # 14_1, 14_2 and 14_3
    #     self.findBy('id', 'section_2-heading').click()
    #     val_1 = self.findBy('id', 'key_14_value_14_1')
    #     val_2 = self.findBy('id', 'key_14_value_14_2')
    #     val_3 = self.findBy('id', 'key_14_value_14_3')

    #     # She selects value 2 and sees the list is now filtered
    #     val_2.click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 1)
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
    #         'contains(text(), "Foo 2")]')

    #     # The filter was added to the list of active filters
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertTrue(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 1)
    #     filter_1 = self.findBy('xpath', '//div[@id="active-filters"]//li[1]')
    #     self.assertEqual(filter_1.text, 'Key 14: Value 14_2')

    #     # She removes the filter again, the list is unfiltered again
    #     val_2.click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 4)
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertFalse(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 0)

    #     # She selects the first checkbox and again, the list is filtered
    #     val_1.click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 2)
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
    #         'contains(text(), "Foo 4")]')
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
    #         'contains(text(), "Foo 1")]')

    #     # The filter was added to the list of active filters
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertTrue(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 1)
    #     filter_1 = self.findBy('xpath', '//div[@id="active-filters"]//li[1]')
    #     self.assertEqual(filter_1.text, 'Key 14: Value 14_1')

    #     # She also selects value 3
    #     val_3.click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 1)
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
    #         'contains(text(), "Foo 4")]')

    #     # The filter was added to the list of active filters
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertTrue(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 2)
    #     filter_1 = self.findBy('xpath', '//div[@id="active-filters"]//li[1]')
    #     self.assertEqual(filter_1.text, 'Key 14: Value 14_1')
    #     filter_2 = self.findBy('xpath', '//div[@id="active-filters"]//li[2]')
    #     self.assertEqual(filter_2.text, 'Key 14: Value 14_3')

    #     # She sees that she can also remove the filter in the list of
    #     # filters
    #     self.findBy('xpath', '(//a[@class="remove-filter"])[1]').click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 2)
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
    #         'contains(text(), "Foo 4")]')
    #     self.findBy(
    #         'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
    #         'contains(text(), "Foo 3")]')

    #     # The filter was removed from the list of active filters
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertTrue(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 1)
    #     filter_1 = self.findBy('xpath', '//div[@id="active-filters"]//li[1]')
    #     self.assertEqual(filter_1.text, 'Key 14: Value 14_3')

    #     # She adds another filter
    #     # She also selects value 3
    #     val_2.click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     # She clicks the button to clear all filters and sees they are all gone
    #     self.findBy('id', 'filter-reset').click()

    #     WebDriverWait(self.browser, 10).until(
    #         EC.invisibility_of_element_located(
    #             (By.CLASS_NAME, "loading-indicator")))

    #     # She sees there are 4 Questionnaires in the list
    #     list_entries = self.findManyBy(
    #         'xpath', '//article[contains(@class, "tech-item")]')
    #     self.assertEqual(len(list_entries), 4)

    #     # There is no active filter set
    #     active_filter_panel = self.findBy(
    #         'xpath', '//div[@id="active-filters"]/div')
    #     self.assertFalse(active_filter_panel.is_displayed())
    #     active_filters = self.findManyBy(
    #         'xpath', '//div[@id="active-filters"]//li')
    #     self.assertEqual(len(active_filters), 0)
