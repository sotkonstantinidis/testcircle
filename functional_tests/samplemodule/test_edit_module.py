from unittest.mock import patch

from django.core.urlresolvers import reverse

from accounts.client import Typo3Client
from functional_tests.base import FunctionalTest
from sample.tests.test_views import route_questionnaire_new

route_add_module = 'sample:add_module'


@patch.object(Typo3Client, 'get_user_id')
class EditModuleTest(FunctionalTest):

    fixtures = [
        'groups_permissions.json', 'global_key_values.json', 'sample.json',
        'samplemodule.json'
    ]

    def test_edit_module(self, mock_get_user_id):

        # Alice logs in
        self.doLogin()

        # She creates a sample questionnaire
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        self.click_edit_section('cat_1')
        self.findBy('name', 'qg_1-0-original_key_1').send_keys('Foo')
        self.findBy('name', 'qg_1-0-original_key_3').send_keys('Bar')
        self.findBy('xpath', '//div[@id="id_qg_31_1_key_4_chosen"]').click()
        self.findBy('xpath',
                    '//div[@id="id_qg_31_1_key_4_chosen"]//'
                    'ul[@class="chosen-results"]/li[text()="Germany"]').click()
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        import time; time.sleep(5)

        # She adds a module for this questionnaire
        self.browser.get(self.live_server_url + reverse(route_add_module))
        search_field = self.findBy(
            'xpath', '//input[contains(@class, "link-search-field")]')
        search_field.send_keys('Foo')
        self.wait_for('xpath', '//li[@class="ui-menu-item"]')
        self.findBy(
            'xpath',
            '//li[@class="ui-menu-item"]//strong[text()="Foo"'
            ']').click()
        samplemodule_radio = self.findBy(
            'xpath',
            '//input[@value="samplemodule" and @name="module"]')
        samplemodule_radio.click()
        self.findBy('xpath', '//input[@type="submit"]').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees the inherited values

        # She edits the first step of the module

        # She sees the inherited values

        # She sees she can edit the first question but not the inherited ones.

        # She goes to the sample questionnaire

        # She edits some values

        # She goes back to the module and sees the updated values

        # She enters the first question and saves the step

        # She sees the inherited values and the first question

        # She goes back to the form and sees all values

        # By some hack, she makes the inherited value editable and submits the
        # step

        # She sees the unchanged inherited values

        # She goes to the questionnaire and sees the same values there.
