from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from unittest.mock import patch

from selenium import webdriver

from accounts.client import Typo3Client
from accounts.tests.test_models import create_new_user
from functional_tests.base import FunctionalTest
from questionnaire.models import Questionnaire
from sample.tests.test_views import route_questionnaire_new, \
    route_questionnaire_new_step, get_position_of_category

TEST_INDEX_PREFIX = 'qcat_test_prefix_'


@override_settings(ES_INDEX_PREFIX=TEST_INDEX_PREFIX)
@patch.object(Typo3Client, 'get_user_id')
class QuestionnaireTest(FunctionalTest):

    fixtures = ['groups_permissions.json', 'global_key_values.json',
                'sample.json']

    def test_add_points(self, mock_get_user_id):

        cat_3_position = get_position_of_category('cat_3', start0=True)

        # Alice logs in
        user_moderator = create_new_user()
        user_moderator.groups = [
            Group.objects.get(pk=3), Group.objects.get(pk=4)]
        self.doLogin(user=user_moderator)

        # She starts editing a new questionnaire, no map is visible
        self.browser.get(self.live_server_url + reverse(
            route_questionnaire_new))
        self.findByNot('id', 'map-view')

        # She goes to a step with the map and sets a point on the map
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "sample/edit/") and contains(@class, "button"'
            ')]')[cat_3_position].click()
        map = self.findBy(
            'xpath', '//div[contains(@class, "map-form-container")]')
        map.click()

        # She saves the step
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # In the overview, she now sees a map with the point on it
        self.findBy('id', 'map-view')

        cat_0_position = get_position_of_category('cat_0', start0=True)
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "sample/edit/") and contains(@class, "button"'
            ')]')[cat_0_position].click()
        self.rearrangeFormHeader()
        self.screenshot()
        self.findBy(
            'xpath', '//div[contains(@class, "chosen-container")]').click()
        self.findBy(
            'xpath', '//ul[@class="chosen-results"]/li[text()="Afghanistan"]') \
            .click()
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She submits the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # In the overview, there is still the map with the point.
        self.findBy('id', 'map-view')

        # In the database, a geometry was added
        db_questionnaire = Questionnaire.objects.order_by('-id')[0]
        geom = db_questionnaire.geom
        self.assertIsNotNone(geom)

        # She edits the questionnaire and adds another point
        self.findBy(
            'xpath', '//a[contains(@href, "sample/edit/") and contains(@class, '
                     '"button")]').click()
        self.findManyBy(
            'xpath',
            '//a[contains(@href, "sample/edit/") and contains(@class, "button"'
            ')]')[cat_3_position].click()
        self.rearrangeFormHeader()
        map = self.findBy(
            'xpath', '//div[contains(@class, "map-form-container")]')
        self.findBy('xpath', '//label[@for="qg_39_1_1"]').click()
        self.findBy('xpath', '//label[@for="qg_39_1_1"]').click()
        action = webdriver.common.action_chains.ActionChains(self.browser)
        action.move_to_element_with_offset(map, 5, 5)
        action.click()
        action.perform()

        # She submits the step and sees the map on the overview is updated
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('id', 'map-view')

        # She submits the questionnaire and sees the updated map
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('id', 'map-view')

        # In the database, the geometry was updated
        db_questionnaire = Questionnaire.objects.order_by('-id')[0]
        self.assertNotEqual(db_questionnaire.geom, geom)

        # She publishes the questionnaire
        self.findBy('id', 'button-submit').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//input[@name="review"]').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')
        self.findBy('xpath', '//input[@name="publish"]').click()
        self.findBy('xpath', '//div[contains(@class, "success")]')

        # She sees that still, the map is there on the overview
        self.findBy('id', 'map-view')
