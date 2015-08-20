from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from functional_tests.base import FunctionalTest
from qcat.utils import get_session_questionnaire
from sample.tests.test_views import (
    route_questionnaire_new_step as sample_route_questionnaire_new_step,
    route_questionnaire_new as sample_route_questionnaire_new,
)
from unccd.tests.test_views import (
    route_questionnaire_new_step as unccd_route_questionnaire_new_step,
)


TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
class SessionTest(FunctionalTest):

    fixtures = [
        'global_key_values.json', 'sample.json', 'unccd.json']

    def test_stores_session_dictionary_correctly(self):

        # Alice logs in
        self.doLogin()

        # She goes to a step of the questionnaire
        self.browser.get(self.live_server_url + reverse(
            sample_route_questionnaire_new_step,
            kwargs={'identifier': 'new', 'step': 'cat_1'}))

        # She enters something as first key
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        self.assertEqual(key_1.text, '')
        key_1.send_keys('Foo')

        self.findBy('id', 'button-submit').click()

        self.findBy('xpath', '//*[text()[contains(.,"Foo")]]')
        session_data = get_session_questionnaire('sample')
        self.assertEqual(
            session_data, ({'qg_1': [{'key_1': {'en': 'Foo'}}]}, {}))

        # self.assertEqual(self.browser.current_url, 'foo')
        self.findBy('id', 'button-submit').click()

    def test_sessions_separated_by_configuration(self):

        # Alice logs in
        self.doLogin()

        # She goes to a step of the sample questionnaire
        self.browser.get(self.live_server_url + reverse(
            sample_route_questionnaire_new_step,
            kwargs={'identifier': 'new', 'step': 'cat_1'}))

        # She enters something as first key
        key_1 = self.findBy('name', 'qg_1-0-original_key_1')
        self.assertEqual(key_1.text, '')
        key_1.send_keys('Foo')

        # She submits the form and sees the value is stored in the
        # session and displayed in the overview
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//*[text()[contains(.,"Foo")]]')

        # She goes to a step of the unccd questionnaire
        self.browser.get(self.live_server_url + reverse(
            unccd_route_questionnaire_new_step,
            kwargs={
                'identifier': 'new', 'step': 'unccd_0_general_information'}))

        # She enters something as first key
        key_1 = self.findBy('name', 'qg_name-0-original_name')
        self.assertEqual(key_1.text, '')
        key_1.send_keys('Bar')

        # She submits the form and sees the value is stored in the
        # session and displayed in the overview
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//*[text()[contains(.,"Bar")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"Foo")]]')

        # She submits the unccd questionnaire and sees only the unccd value
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//*[text()[contains(.,"Bar")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"Foo")]]')

        # She goes back to the sample questionnaire and sees the value
        # in the session is still there
        self.browser.get(self.live_server_url + reverse(
            sample_route_questionnaire_new))
        self.findBy('xpath', '//*[text()[contains(.,"Foo")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"Bar")]]')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//*[text()[contains(.,"Foo")]]')
        self.findByNot('xpath', '//*[text()[contains(.,"Bar")]]')
