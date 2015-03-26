from functional_tests.base import FunctionalTest


class TranslationTest(FunctionalTest):

    def test_change_languages(self):

        # Alice opens her web browser and goes to the home page.
        self.browser.get(self.live_server_url)

        # She sees that the page is in English because the available languages
        # are written in English.
        self.checkOnPage('English')
        self.checkOnPage('Spanish')

        # She changes the language to Spanish and sees that the available
        # languages are now written in Spanish.
        self.changeLanguage('es')
        self.checkOnPage('Inglés')
        self.checkOnPage('Español')
