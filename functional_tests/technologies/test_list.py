import json

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from functional_tests.base import FunctionalTest

from search.index import delete_all_indices
from search.tests.test_index import create_temp_indices
from wocat.tests.test_views import route_questionnaire_list as route_wocat_list


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(
    ES_INDEX_PREFIX=TEST_INDEX_PREFIX,
    LANGUAGES=(('en', 'English'), ('es', 'Spanish'), ('fr', 'French')))
class ListTest(FunctionalTest):

    fixtures = [
        'global_key_values.json', 'wocat.json', 'technologies.json',
        'unccd.json', 'approaches.json', 'cca.json', 'watershed.json',
        'technologies_questionnaires.json', 'unccd_questionnaires.json']

    def setUp(self):
        super(ListTest, self).setUp()
        delete_all_indices(prefix=TEST_INDEX_PREFIX)
        create_temp_indices([
            ('technologies', '2015'), ('approaches', '2015'), ('wocat', '2015'),
            ('unccd', '2015'), ('cca', '2015'), ('watershed', '2015')])

    def tearDown(self):
        super(ListTest, self).tearDown()
        delete_all_indices(prefix=TEST_INDEX_PREFIX)

    def test_list_is_available(self):

        # She goes to the WOCAT list and sees that both Technologies and
        # UNCCD practices are listed, each with details.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        expected_results = [
            {
                'title': 'UNCCD practice 2',
                'description': 'This is the description of the second UNCCD practice.',
            },
            {
                'title': 'UNCCD practice 1',
                'description': 'This is the description of the first UNCCD practice.',
            },
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
            },
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
            },
        ]
        self.check_list_results(expected_results)

        # Alice applies the type filter and sees that only technologies are
        # listed
        self.findBy('id', 'search-type-display').click()
        self.findBy('xpath', '//li/a[@data-type="technologies"]').click()
        self.apply_filter()

        expected_results = [
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
            },
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
            },
        ]
        self.check_list_results(expected_results)

    def test_filter(self):

        # Alice goes to the list view and filters by technologies.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))
        self.findBy('id', 'search-type-display').click()

        self.wait_for('xpath', '//li/a[@data-type="technologies"]')
        self.findBy('xpath', '//li/a[@data-type="technologies"]').click()
        self.apply_filter()

        # She also filters by country
        self.findBy('xpath', '//div[contains(@class,'
                             ' "chosen-container")]').click()

        self.findBy(
            'xpath', '//ul[@class="chosen-results"]/li[contains(text(), '
                     '"Switzerland")]').click()
        self.apply_filter()

        # She sees that she has been redirected to the list view and the filter
        # is set, only 1 entry is visible
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 1)

        # The filter was added to the list of active filters
        active_filters = self.get_active_filters()
        self.assertEqual(len(active_filters), 2)
        self.assertEqual(active_filters[0].text, 'SLM Data: SLM Technologies')
        self.assertEqual(active_filters[1].text, 'Country: Switzerland')

    def test_filter_also_in_api(self):
        api_url = reverse('v2:questionnaires-api-list')

        # Alice goes to the list view
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        # She sees there are 4 Questionnaires in the list
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 4)

        # She filters by country = Switzerland
        country_filter = self.findBy(
            'xpath', '//div/label[@for="filter-country"]/../div')
        country_filter.click()
        country_filter.find_element_by_xpath(
            '//ul[@class="chosen-results"]/li[text()="Switzerland"]'
        ).click()
        self.apply_filter()

        # She sees there is 1 results left
        expected_results = [
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
            },
        ]
        self.check_list_results(expected_results)

        # She adds the same filter params to the API url
        url = self.browser.current_url
        filter_params = url.split('?')[1]
        self.browser.get(self.live_server_url + api_url + '?' + filter_params + '&format=json')

        # She sees the API results are filtered
        json_response = json.loads(
            self.browser.find_element_by_tag_name('body').text)
        self.assertEqual(len(json_response['results']), 1)
        self.assertEqual(
            json_response['results'][0]['name'], 'WOCAT Technology 1')

        # She goes back to the list view and does a search
        self.browser.get(self.live_server_url + reverse(route_wocat_list))
        self.findBy('xpath', '//input[@type="search"]').send_keys('wocat')
        self.apply_filter()

        # She sees there are 2 results left
        expected_results = [
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
            },
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
            },
        ]
        self.check_list_results(expected_results)

        # Again, she adds the same filter params to the API url
        url = self.browser.current_url
        filter_params = url.split('?')[1]
        self.browser.get(
            self.live_server_url + api_url + '?' + filter_params + '&format=json')

        # She sees the API results are filtered
        json_response = json.loads(
            self.browser.find_element_by_tag_name('body').text)
        self.assertEqual(len(json_response['results']), 2)
        self.assertEqual(
            json_response['results'][0]['name'], 'WOCAT Technology 1')
        self.assertEqual(
            json_response['results'][1]['name'], 'WOCAT Tech 2 en español')
