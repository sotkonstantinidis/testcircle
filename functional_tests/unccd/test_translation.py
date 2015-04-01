from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from unccd.tests.test_views import (
    route_home,
)


class TranslationTest(FunctionalTest):

    fixtures = ['global_key_values.json', 'unccd.json']

    def test_change_languages(self):

        # Alice goes to the UNCCD app
        self.browser.get(self.live_server_url + reverse(
            route_home))

        # She sees that the page is in English because the available languages
        # are written in English.
        self.checkOnPage('English')
        self.checkOnPage('Spanish')

        url = self.browser.current_url

        # She changes the language to Spanish and sees that the available
        # languages are now written in Spanish.
        self.changeLanguage('es')
        self.checkOnPage('Inglés')
        self.checkOnPage('Español')

        # She sees that she is still on the same page as before
        self.assertEqual(url.replace('/en/', '/es/'), self.browser.current_url)
