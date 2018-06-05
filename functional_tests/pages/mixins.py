from selenium.webdriver.common.by import By


class ListMixin:
    LOC_LIST_ENTRY = (By.XPATH, '//article[contains(@class, "tech-item")]')
    LOC_LIST_ENTRY_TITLE = (
        By.XPATH, '(//article[contains(@class, "tech-item")])[{i}]'  # 1-based!
                  '//a[contains(text(), "{title}")]')
    LOC_LIST_ENTRY_DESCRIPTION = (
        By.XPATH, '(//article[contains(@class, "tech-item")])[{i}]'  # 1-based!
                  '//p[contains(text(), "{description}")]')
    LOC_LIST_ENTRY_STATUS = (
        By.XPATH, '(//article[contains(@class, "tech-item")])[{i}]'  # 1-based!
                  '//span[contains(@class, "tech-status") and contains('
                  '@class, "is-{status}")]')
    LOC_LIST_ENTRY_LANGUAGE = (
        By.XPATH, '(//article[contains(@class, "tech-item")])[{i}]'  # 1-based!
                  '//a[contains(text(), "{lang}")]')
    LOC_FILTER_TYPE_SWITCHER = (By.ID, 'search-type-display')
    LOC_FILTER_TYPE_ENTRY = (
        By.XPATH, '//ul[contains(@class, "search-type-select")]/li/'
                  'a[@data-type="{type}"]')
    LOC_FILTER_TYPE_VALUE = (By.ID, 'search-type')  # The hidden value
    LOC_FILTER_COUNTRY_CHOSEN = (By.XPATH, '//div[@id="filter_country_chosen"]')
    LOC_BUTTON_FILTER_SUBMIT = (By.CLASS_NAME, 'search-submit')
    LOC_LOADING_INDICATOR = (By.CLASS_NAME, 'loading-indicator')
    LOC_ACTIVE_FILTERS = (By.XPATH, '//div[@id="active-filters"]//li')
    LOC_SEARCH_INPUT = (By.XPATH, '//input[@type="search" and @name="q"]')

    def get_type_value(self) -> str:
        return self.get_value(self.get_el(self.LOC_FILTER_TYPE_VALUE))

    def search(self, search_term: str, clear: bool=True):
        el = self.get_el(self.LOC_SEARCH_INPUT)
        if clear is True:
            el.clear()
        el.send_keys(search_term)

    def filter_by_type(self, type_keyword: str):
        self.get_el(self.LOC_FILTER_TYPE_SWITCHER).click()
        locator = self.format_locator(
            self.LOC_FILTER_TYPE_ENTRY, type=type_keyword)
        self.get_el(locator).click()

    def filter_by_country(self, country_name: str):
        self.select_chosen(self.LOC_FILTER_COUNTRY_CHOSEN, country_name)

    def apply_filter(self):
        self.get_el(self.LOC_BUTTON_FILTER_SUBMIT).click()
        self.wait_for(self.LOC_LOADING_INDICATOR, visibility=False)

    def get_active_filters(self) -> list:
        return [f.text for f in self.get_els(self.LOC_ACTIVE_FILTERS)]

    def count_list_results(self) -> int:
        return len(self.get_els(self.LOC_LIST_ENTRY))

    def check_list_results(self, expected: list, count: bool=True):
        """
        Args:
            expected: list of dicts. Can contain
                - title
                - description
                - status: Note that status "public" has no badge
                - translations (list)
            count: bool. Check whether length of expected list matches length of
                actual list results.
        """
        if count is True:
            assert self.count_list_results() == len(expected)
        for i, e in enumerate(expected):
            i_xpath = i + 1
            if e.get('title'):
                locator = self.format_locator(
                    self.LOC_LIST_ENTRY_TITLE, i=i_xpath, title=e['title'])
                self.get_el(locator)
            if e.get('description'):
                locator = self.format_locator(
                    self.LOC_LIST_ENTRY_DESCRIPTION, i=i_xpath,
                    description=e['description'])
                self.get_el(locator)
            if e.get('status'):
                locator = self.format_locator(
                    self.LOC_LIST_ENTRY_STATUS, i=i_xpath, status=e['status'])
                if e['status'] == 'public':
                    assert self.exists_el(locator) is False
                else:
                    self.get_el(locator)
            for lang in e.get('translations', []):
                locator = self.format_locator(
                    self.LOC_LIST_ENTRY_LANGUAGE, i=i_xpath, lang=lang)
                self.get_el(locator)


class EditMixin:

    LOC_CATEGORIES_PROGRESS_INDICATORS = (
        By.XPATH, '//div[@class="tech-section-progress"]')
    LOC_CATEGORY_TITLE = (By.XPATH, '//h2[contains(text(), "{category}")]')
    LOC_BUTTON_EDIT_CATEGORY = (
        By.XPATH, '//a[contains(@href, "/edit/") and contains('
                  '@href, "{keyword}")]')
    LOC_BUTTON_REVIEW_ACTION = (
        By.XPATH, '//a[@data-reveal-id="confirm-{action}"]')
    LOC_BUTTON_REVIEW_CONFIRM = (By.XPATH, '//button[@name="{action}"]')

    def get_progress_indicators(self):
        return self.get_els(self.LOC_CATEGORIES_PROGRESS_INDICATORS)

    def get_category_by_name(self, name: str):
        locator = self.format_locator(self.LOC_CATEGORY_TITLE, category=name)
        return self.get_el(locator)

    def click_edit_category(self, keyword: str):
        locator = self.format_locator(
            self.LOC_BUTTON_EDIT_CATEGORY, keyword=keyword)
        self.get_el(locator).click()

    def submit_questionnaire(self):
        btn_locator = self.format_locator(
            self.LOC_BUTTON_REVIEW_ACTION, action='submit')
        self.get_el(btn_locator).click()
        confirm_locator = self.format_locator(
            self.LOC_BUTTON_REVIEW_CONFIRM, action='submit')
        self.wait_for(confirm_locator)
        self.get_el(confirm_locator).click()

    # def review_action(
    #         self, action, exists_only=False, exists_not=False,
    #         expected_msg_class='success'):
    #     """
    #     Handle review actions which trigger a modal.
    #
    #     Args:
    #         action: One of
    #             - 'edit'
    #             - 'view'
    #             - 'submit'
    #             ⁻ 'review'
    #             - 'publish'
    #             - 'reject'
    #             - 'flag-unccd'
    #             - 'unflag-unccd'
    #         exists_only: Only check that the modal is opened without triggering
    #           the action.
    #         expected_msg_class: str.
    #
    #     Returns:
    #
    #     """
    #     if action == 'view':
    #         btn = self.findBy(
    #             'xpath', '//form[@id="review_form"]//a[text()="View"]')
    #         if exists_only is True:
    #             return btn
    #         btn.click()
    #         return
    #     if exists_not is True:
    #         self.findByNot(
    #             'xpath', '//a[@data-reveal-id="confirm-{}"]'.format(action))
    #         return
    #     self.findBy(
    #         'xpath', '//a[@data-reveal-id="confirm-{}"]'.format(action)).click()
    #     btn_xpath = '//button[@name="{}"]'.format(action)
    #     if action == 'edit':
    #         # No button for "edit"
    #         btn_xpath = '//a[text()="Edit" and @type="submit"]'
    #     WebDriverWait(self.browser, 10).until(
    #         EC.visibility_of_element_located(
    #             (By.XPATH, btn_xpath)))
    #     if action == 'reject':
    #         self.findBy('name', 'reject-message').send_keys("spam")
    #
    #     if exists_only is True:
    #         self.findBy('xpath', '//div[contains(@class, "reveal-modal") and contains(@class, "open")]//a[contains(@class, "close-reveal-modal")]').click()
    #         import time; time.sleep(1)
    #         return
    #     self.findBy('xpath', btn_xpath).click()
    #     self.findBy(
    #         'xpath', '//div[contains(@class, "{}")]'.format(expected_msg_class))
    #     if action not in ['reject', 'delete']:
    #         self.toggle_all_sections()
