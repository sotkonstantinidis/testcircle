from functional_tests.base import FunctionalTest


class FormTest(FunctionalTest):

    def test_test(self):

        self.browser.get('{}/questionnaire/new'.format(self.live_server_url))

        self.findBy('name', '1-0-slmname').send_keys('SLM Name')

        self.findBy('id', 'button-submit').click()

        self.findBy('name', '2-answera').send_keys('This is Answer A')
        self.findBy('name', '2-remarka').send_keys('This is Remark A')

        self.findBy('id', 'button-submit').click()

        # Make sure the entered values are represented
        self.checkOnPage('SLM Name')
        self.checkOnPage('This is Answer A')
        self.checkOnPage('This is Remark A')
