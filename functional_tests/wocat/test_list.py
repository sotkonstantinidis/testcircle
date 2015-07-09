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
        'global_key_values.json', 'technologies.json', 'unccd.json',
        'technologies_questionnaires.json', 'unccd_questionnaires.json']

    def setUp(self):
        super(ListTest, self).setUp()
        delete_all_indices()
        create_temp_indices(['technologies', 'unccd'])

    def tearDown(self):
        super(ListTest, self).tearDown()
        delete_all_indices()

    def test_list_is_available(self):

        # She goes to the WOCAT list and sees that all questionnaires of
        # WOCAT and the UNCCD one are listed, each with details.
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        results = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(results), 4)

        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "UNCCD practice 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "UNCCD practice 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'contains(text(), "")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "WOCAT practice 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'contains(text(), "")]')

    def test_list_is_multilingual(self):

        # Alice goes to the list view and sees the questionnaires
        self.browser.get(self.live_server_url + reverse(route_wocat_list))

        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 4)

        """
        UNCCD 1: Original in EN, translation in ES
        UNCCD 2: Original in EN
        WOCAT 1: Original in FR, translation in EN
        WOCAT 2: Original in ES
        """

        # ENGLISH
        # UNCCD 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "UNCCD practice 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "")]')
        # WOCAT 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "")]')
        self.findBy('xpath', '//article[2]//a[contains(text(), "Spanish")]')
        # UNCCD 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "UNCCD practice 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'contains(text(), "")]')
        self.findBy('xpath', '//article[3]//a[contains(text(), "Spanish")]')
        # WOCAT 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "WOCAT practice 1")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'contains(text(), "")]')
        self.findBy('xpath', '//article[4]//a[contains(text(), "French")]')

        self.changeLanguage('es')
        list_entries = self.findManyBy(
            'xpath', '//article[contains(@class, "tech-item")]')
        self.assertEqual(len(list_entries), 4)

        # SPANISH
        # UNCCD 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//h1/a['
            'contains(text(), "UNCCD practice 2")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[1]//p['
            'contains(text(), "")]')
        # WOCAT 2
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//h1/a['
            'contains(text(), "WOCAT 2 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[2]//p['
            'contains(text(), "")]')
        # UNCCD 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//h1/a['
            'contains(text(), "UNCCD 1 en español")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[3]//p['
            'contains(text(), "")]')
        self.findBy('xpath', '//article[3]//a[contains(text(), "English")]')
        # WOCAT 1
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//h1/a['
            'contains(text(), "WOCAT 1 en français")]')
        self.findBy(
            'xpath', '(//article[contains(@class, "tech-item")])[4]//p['
            'contains(text(), "")]')
        self.findBy('xpath', '//article[4]//a[contains(text(), "English")]')
        self.findBy('xpath', '//article[4]//a[contains(text(), "French")]')
