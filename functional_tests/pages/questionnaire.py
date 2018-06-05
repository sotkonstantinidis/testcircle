from selenium.webdriver.common.by import By

from functional_tests.pages.base import QcatPage


class QuestionnaireStepPage(QcatPage):
    route_name = ''

    LOC_BUTTON_SUBMIT = (By.ID, 'button-submit')
    LOC_IMAGE_FOCAL_POINT_TARGET = (By.ID, 'id_qg_image-0-image_target')

    def is_focal_point_available(self):
        # The script to set the focus point for the image is loaded, and the
        # hidden field is in the DOM.
        self.browser.execute_script("return $.addFocusPoint();")
        self.exists_el(self.LOC_IMAGE_FOCAL_POINT_TARGET)

    def enter_text(self, locator: tuple, text: str, clear: bool=False):
        el = self.get_el(locator)
        if clear is True:
            el.clear()
        el.send_keys(text)

    def submit_step(self):
        self.get_el(self.LOC_BUTTON_SUBMIT).click()
        assert self.has_success_message()
