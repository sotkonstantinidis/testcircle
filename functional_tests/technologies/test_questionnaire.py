from django.core.urlresolvers import reverse
from functional_tests.base import FunctionalTest

from technologies.tests.test_views import (
    route_questionnaire_new_step,
    get_category_count,
    get_categories,
)
from wocat.tests.test_views import route_home


class QuestionnaireTest(FunctionalTest):

    fixtures = ['global_key_values.json', 'technologies.json']

    def test_questionnaire_is_available(self):

        # Alice logs in
        self.doLogin()

        # She goes to the technologies app
        self.browser.get(self.live_server_url + reverse(route_home))

        # She sees a link to enter a new questionnaire and clicks it
        self.findBy(
            'xpath',
            '//a[contains(@href, "/technologies/edit/") and '
            'contains(@class, "button")]'
        ).click()

        # She is taken to the form and sees the steps
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="tech-section-progress progress"]')
        self.assertEqual(len(progress_indicators), get_category_count())

        # She goes to the first step and sees the link works.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, args=[get_categories()[0][0]]))

        self.findBy('id', 'button-submit').click()
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="tech-section-progress progress"]')
        self.assertEqual(len(progress_indicators), get_category_count())
