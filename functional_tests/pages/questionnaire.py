from selenium.webdriver.common.by import By

from functional_tests.pages.base import QcatPage


class QuestionnaireStepPage(QcatPage):
    route_name = ''

    LOC_BUTTON_SUBMIT = (By.ID, 'button-submit')
    LOC_IMAGE_FOCAL_POINT_TARGET = (By.ID, 'id_qg_image-0-image_target')
    LOC_LINK_ENTRIES = (By.XPATH, '//div[@class="link-preview"]/div')
    LOC_LINK_ENTRY = (
        By.XPATH,
        '//div[@class="link-preview"]/div[text()="{link_text}"]')

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

    def check_links(self, link_list: list, count: bool=True) -> bool:
        found_links = []
        for link in link_list:
            link_el = self.get_el(
                self.format_locator(self.LOC_LINK_ENTRY, link_text=link))
            found_links.append(link_el)
        if count is True:
            return len(self.get_els(self.LOC_LINK_ENTRIES)) == len(found_links)
        return True
