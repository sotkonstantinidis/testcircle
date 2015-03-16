from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from unccd.tests.test_views import (
    questionnaire_route_home,
    questionnaire_route_new_step,
    get_category_count,
)


class QuestionnaireTest(FunctionalTest):

    fixtures = ['unccd.json']

    def test_questionnaire_is_available(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She goes to the UNCCD app
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_home))

        # She sees a link to enter a new questionnaire and clicks it
        self.findBy(
            'xpath', '//a[@href="/en/unccd/edit/" and @class="button tiny"]'
        ).click()

        # She is taken to the form and sees the steps
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="progress radius"]')
        self.assertEqual(len(progress_indicators), get_category_count())

        # She goes to the first step and sees the link works.
        self.browser.get(self.live_server_url + reverse(
            questionnaire_route_new_step, args=['unccd_cat_1']))

        self.findBy('id', 'button-submit').click()
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="progress radius"]')
        self.assertEqual(len(progress_indicators), get_category_count())
