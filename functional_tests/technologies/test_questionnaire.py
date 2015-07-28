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

        # She sees that all the categories are there with their correct name
        # Except the first one which is not displayed in the header template
        for category in [c[1] for c in get_categories()][1:]:
            self.findBy('xpath', '//h2[text() = "' + category + '"]')

        # She goes to the first step and sees the link works.
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new_step, kwargs={
                'identifier': 'new', 'step': get_categories()[0][0]}))

        self.findBy('id', 'button-submit').click()
        progress_indicators = self.findManyBy(
            'xpath', '//div[@class="tech-section-progress progress"]')
        self.assertEqual(len(progress_indicators), get_category_count())
