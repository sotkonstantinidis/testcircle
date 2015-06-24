# Prevent logging of Elasticsearch queries
import logging
logging.disable(logging.CRITICAL)

from django.test.utils import override_settings

from accounts.tests.test_models import create_new_user
from functional_tests.base import FunctionalTest
from search.index import delete_all_indices


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class SearchTestAdmin(FunctionalTest):

    fixtures = ['sample.json', 'sample_questionnaires.json']

    def setUp(self):
        super(SearchTestAdmin, self).setUp()
        user = create_new_user()
        user.is_superuser = True
        user.save()
        self.user = user

    def tearDown(self):
        super(SearchTestAdmin, self).tearDown()
        delete_all_indices()

    def test_search_admin(self):

        # Alice logs in
        self.doLogin(user=self.user)

        # She sees the button to access the search administration in the
        # top navigation bar and clicks it.
        navbar = self.findBy('class_name', 'top-bar')
        navbar.find_element_by_link_text('Search Index Administration').click()

        # She sees that the active configurations are listed, all of
        # them having no index
        self.findBy(
            'xpath',
            '//tbody/tr[1]/td/span[text()="Sample Core Configuration"]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[1]/td/span/strong[@class="text-warning"]').text,
            'No Index!')
        self.findBy(
            'xpath',
            '//tbody/tr[2]/td/span[text()="Sample Configuration"]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[2]/td/span/strong[@class="text-warning"]').text,
            'No Index!')

        # She creates the index for the sample configuration
        self.findBy('xpath', '//a[contains(@href, "/index/sample/")]').click()

        # She sees the index was created successfully
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[1]/td/span/strong[@class="text-warning"]').text,
            'No Index!')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[2]/td/span/strong[@class="text-warning"]').text,
            '0 / 2')

        # She updates the newly created index
        self.findBy('xpath', '//a[contains(@href, "/update/sample/")]').click()

        # She sees that the index was updated successfully
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[1]/td/span/strong[@class="text-warning"]').text,
            'No Index!')
        self.findByNot(
            'xpath', '//tbody/tr[2]/td/span/strong[@class="text-warning"]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[2]/td/span/strong[@class="text-ok"]').text,
            '2 / 2')

        # She decides to delete all indices
        self.findBy('xpath', '//a[contains(@href, "/search/delete/")]').click()

        # She sees that all indices were deleted
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy(
            'xpath',
            '//tbody/tr[1]/td/span[text()="Sample Core Configuration"]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[1]/td/span/strong[@class="text-warning"]').text,
            'No Index!')
        self.findBy(
            'xpath',
            '//tbody/tr[2]/td/span[text()="Sample Configuration"]')
        self.assertEqual(
            self.findBy(
                'xpath',
                '//tbody/tr[2]/td/span/strong[@class="text-warning"]').text,
            'No Index!')
