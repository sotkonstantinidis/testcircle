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
    LOC_LINK_ENTRY_REMOVE = (
        By.XPATH, '(//div[@class="link-preview"])[{index}]//'
                  'a[@class="close"]')  # 1-based!
    LOC_LINK_ADD_MORE = (
        By.XPATH, '//a[@data-questiongroup-keyword="{questiongroup}" and '
                  '@data-add-item]')
    LOC_INPUT_SEARCH_LINK = (
        By.XPATH, '(//div[contains(@class, "link-search") and not(contains('
                  '@style, "display: none;"))])[1]/input[contains(@class, '
                  '"link-search-field")]')
    LOC_BUTTON_BACK_WITHOUT_SAVING = (
        By.XPATH, '//a[@class="wizard-header-back"]')

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

    def back_without_saving(self):
        self.get_el(self.LOC_BUTTON_BACK_WITHOUT_SAVING).click()

    def check_links(self, link_list: list, count: bool=True) -> bool:
        found_links = []
        for link in link_list:
            link_el = self.get_el(
                self.format_locator(self.LOC_LINK_ENTRY, link_text=link))
            found_links.append(link_el)
        if count is True:
            return len(self.get_els(self.LOC_LINK_ENTRIES)) == len(found_links)
        return True

    def delete_link(self, index: int):
        self.get_el(
            self.format_locator(self.LOC_LINK_ENTRY_REMOVE, index=index+1)
        ).click()

    def add_link(self, qg_keyword: str, link_name: str, add_more: bool=False):
        if add_more is True:
            self.get_el(
                self.format_locator(
                    self.LOC_LINK_ADD_MORE, questiongroup=qg_keyword)
            ).click()
        self.get_el(self.LOC_INPUT_SEARCH_LINK).send_keys(link_name)
        self.select_autocomplete(link_name)
