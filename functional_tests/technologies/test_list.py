from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from functional_tests.base import FunctionalTest

from search.index import delete_all_indices
from search.tests.test_index import create_temp_indices
from technologies.tests.test_views import route_questionnaire_list as \
    route_tech_list
from wocat.tests.test_views import (
    route_questionnaire_list as route_wocat_list,
    route_home as route_wocat_home,
)


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(
    ES_INDEX_PREFIX=TEST_INDEX_PREFIX,
    LANGUAGES=(('en', 'English'), ('es', 'Spanish'), ('fr', 'French')))
class ListTest(FunctionalTest):

    fixtures = [
        'global_key_values.json', 'wocat.json', 'technologies.json',
        'unccd.json', 'technologies_questionnaires.json',
        'unccd_questionnaires.json']

    def setUp(self):
        super(ListTest, self).setUp()
        delete_all_indices()
        create_temp_indices(['technologies', 'approaches', 'wocat', 'unccd'])

    def tearDown(self):
        super(ListTest, self).tearDown()
        delete_all_indices()

    def test_list_is_available(self):

        # She goes to the WOCAT list and sees that both Technologies and
        # UNCCD practices are listed, each with details.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        results = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(results), 4)

        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "UNCCD practice 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "This is the description of the second UNCCD '
            'practice.")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT Tech 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "Descripción 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "UNCCD practice 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'contains(text(), "This is the description of the first UNCCD '
            'practice.")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "WOCAT Technology 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'contains(text(), "This is the definition of the first WOCAT '
            'Technology.")]')

        # Alice goes to the Technologies list and sees that only the
        # Technologies are listed.
        self.browser.get(self.live_server_url + reverse(route_tech_list))

        results = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(results), 2)

        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "WOCAT Tech 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "Descripción 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT Technology 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "This is the definition of the first WOCAT '
            'Technology.")]')

    def test_list_is_multilingual(self):

        # Alice goes to the list view and sees the questionnaires
        self.browser.get(self.live_server_url + reverse(route_tech_list))

        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 2)

        """
        Tech 1: Original in FR, translation in EN
        Tech 2: Original in ES
        """

        # ENGLISH
        # WOCAT 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "WOCAT Tech 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "Descripción 2 en español")]')
        self.findBy('xpath', '//article[1]//a[contains(text(), "Spanish")]')
        # WOCAT 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT Technology 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "This is the definition of the first WOCAT '
            'Technology.")]')
        self.findBy('xpath', '//article[2]//a[contains(text(), "French")]')

        self.changeLanguage('es')
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 2)

        # SPANISH
        # WOCAT 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "WOCAT Tech 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "Descripción 2 en español")]')
        # WOCAT 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT Technology 1 en français")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "Ceci est la déscription 1 en français.")]')
        self.findBy('xpath', '//article[2]//a[contains(text(), "English")]')
        self.findBy('xpath', '//article[2]//a[contains(text(), "French")]')

    def test_filter(self):

        # Alice goes to the home page and decides to add a filter by country
        self.browser.get(self.live_server_url + reverse(route_wocat_home))

        self.findBy('link_text', 'Advanced filter').click()
        WebDriverWait(self.browser, 10).until(
            EC.visibility_of_element_located(
                (By.ID, "filter-country")))
        self.findBy('id', 'filter-country').send_keys('Switzerland')
        self.findBy('id', 'submit-filter').click()

        # She sees that she has been redirected to the list view and the filter
        # is set, only 1 entry is visible
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 1)

        # The filter was added to the list of active filters
        active_filter_panel = self.findBy(
            'xpath', '//div[@id="active-filters"]/div')
        self.assertTrue(active_filter_panel.is_displayed())
        active_filters = self.findManyBy(
            'xpath', '//div[@id="active-filters"]//li')
        self.assertEqual(len(active_filters), 1)
        filter_1 = self.findBy('xpath', '//div[@id="active-filters"]//li[1]')
        self.assertEqual(filter_1.text, 'Country: Switzerland')
