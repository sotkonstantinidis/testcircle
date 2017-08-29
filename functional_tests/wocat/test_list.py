from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from configuration.tests.test_utils import DEFAULT_WOCAT_CONFIGURATIONS
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
        'global_key_values.json', 'technologies.json', 'unccd.json',
        'technologies_questionnaires.json', 'unccd_questionnaires.json']

    def setUp(self):
        super(ListTest, self).setUp()
        delete_all_indices()
        create_temp_indices(DEFAULT_WOCAT_CONFIGURATIONS)

    def tearDown(self):
        super(ListTest, self).tearDown()
        delete_all_indices()

    def test_list_is_available(self):

        # She goes to the WOCAT list and sees that all questionnaires of
        # WOCAT and the UNCCD one are listed, each with details.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        expected_results = [
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
                'translations': ['es'],
            },
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
                'translations': ['fr'],
            },
            {
                'title': 'UNCCD practice 2',
                'description': 'This is the description of the second UNCCD practice.',
            },
            {
                'title': 'UNCCD practice 1',
                'description': 'This is the description of the first UNCCD practice.',
                'translations': ['es'],
            },
        ]
        self.check_list_results(expected_results)

    def test_list_handles_invalid_type(self):

        # Alice goes to the WOCAT list and sees value "wocat" is
        # selected as type filter by default.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))
        self.assertEqual(
            self.findBy('id', 'search-type').get_attribute('value'), 'wocat')

        # Alice manually enters type "technologies" in the URL. She sees that
        # the search type has changed.
        self.browser.get(
            self.live_server_url + reverse(
                route_wocat_list) + '?type=technologies')
        self.assertEqual(
            self.findBy('id', 'search-type').get_attribute('value'),
            'technologies')

        # Alice goes to the WOCAT list but manually enters a type which is not
        # valid.
        self.browser.get(
            self.live_server_url + reverse(
                route_wocat_list) + '?type=foo')

        # She sees there is no error message
        self.findByNot('xpath', '//*[contains(text(), "Error")]')

        # The default search type ("All SLM Data") is selected.
        self.assertEqual(
            self.findBy('id', 'search-type').get_attribute('value'), 'foo')

        # She manually enters UNCCD (uppercase) as type. She sees that there is
        # no error.
        self.browser.get(
            self.live_server_url + reverse(
                route_wocat_list) + '?type=UNCCD')
        self.findByNot('xpath', '//*[contains(text(), "Error")]')

    def test_list_is_multilingual(self):

        # Alice goes to the list view and sees the questionnaires
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        # English
        expected_results = [
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
                'translations': ['es'],
            },
            {
                'title': 'WOCAT Technology 1',
                'description': 'This is the definition of the first WOCAT Technology.',
                'translations': ['fr'],
            },
            {
                'title': 'UNCCD practice 2',
                'description': 'This is the description of the second UNCCD practice.',
            },
            {
                'title': 'UNCCD practice 1',
                'description': 'This is the description of the first UNCCD practice.',
                'translations': ['es'],
            },
        ]
        self.check_list_results(expected_results)

        self.changeLanguage('es')

        # SPANISH
        expected_results = [
            {
                'title': 'WOCAT Tech 2 en español',
                'description': 'Descripción 2 en español',
            },
            {
                'title': 'WOCAT Technology 1 en français',
                'description': 'Ceci est la déscription 1 en français.',
                'translations': ['en', 'fr'],
            },
            {
                'title': 'UNCCD practice 2',
                'description': 'This is the description of the second UNCCD practice.',
            },
            {
                'title': 'UNCCD 1 en español',
                'description': 'Descripción 1 en español',
                'translations': ['en'],
            },
        ]
        self.check_list_results(expected_results)
