from functional_tests.base import FunctionalTest


class FormTest(FunctionalTest):

    def test_submit_new_unccd_questionnaire(self):

        # TODO: Extend this test.
        pass
        # self.browser.get('{}/unccd/new'.format(self.live_server_url))

        # self.findBy('name', '1-0-slmname').send_keys('SLM Name')

        # self.findBy('id', 'button-submit').click()

        # self.findBy('name', '2-answera').send_keys('This is Answer A')
        # self.findBy('name', '2-remarka').send_keys('This is Remark A')

        # # Alice submits the form and notices that she is redirected to the
        # # detail page of the Questionnaire where she also sees a success
        # # message
        # self.findBy('id', 'button-submit').click()
        # msg = self.findBy('class_name', 'alert-box')
        # self.assertIn(
        #     'The questionnaire was successfully submitted.', msg.text)

        # # She sees the values she entered previously
        # self.checkOnPage('SLM Name')
        # self.checkOnPage('This is Answer A')
        # self.checkOnPage('This is Remark A')

        # # She refreshes the page and notices the success message is gone
        # self.browser.refresh()
        # self.findByNot('class_name', 'alert-box')
