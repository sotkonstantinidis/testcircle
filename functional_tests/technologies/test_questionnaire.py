from functional_tests.base import FunctionalTest
from functional_tests.pages.qcat import HomePage
from functional_tests.pages.questionnaire import QuestionnaireStepPage
from functional_tests.pages.technologies import TechnologiesNewPage
from functional_tests.pages.wocat import AddDataPage


class QuestionnaireTest(FunctionalTest):

    fixtures = [
        'global_key_values.json',
        'technologies.json',
    ]

    def test_questionnaire_is_available(self):

        # User logs in and goes to the home page.
        home_page = HomePage(self)
        home_page.open(login=True)

        # User clicks a link to add data in the top menu.
        home_page.click_add_slm_data()

        # User clicks a link to add a new Technology.
        add_page = AddDataPage(self)
        add_page.click_add_technology()

        # User sees an empty edit page and the categories of the Technology.
        edit_page = TechnologiesNewPage(self)
        progress_indicators = edit_page.get_progress_indicators()
        categories = edit_page.CATEGORIES
        assert len(progress_indicators) == len(categories)

        # All the categories are listed.
        for __, category in categories:
            edit_page.get_category_by_name(category)

        # User edits the first category.
        edit_page.click_edit_category(categories[0][0])

        # The focal point is available
        step_page = QuestionnaireStepPage(self)
        step_page.is_focal_point_available()

        # User saves the first category.
        step_page.submit_step()

        # All the categories are still there.
        progress_indicators = edit_page.get_progress_indicators()
        categories = edit_page.CATEGORIES
        assert len(progress_indicators) == len(categories)
        for __, category in categories:
            edit_page.get_category_by_name(category)

    def test_translation(self):

        # User logs in and goes to the Edit page.
        page = TechnologiesNewPage(self)
        page.open(login=True)

        # User sees the category names in English.
        for __, category in page.CATEGORIES:
            page.get_category_by_name(category)

        # User changes the language.
        page.change_language('es')

        # User sees the category names in Spanish.
        for __, category in page.CATEGORIES_TRANSLATED:
            page.get_category_by_name(category)
