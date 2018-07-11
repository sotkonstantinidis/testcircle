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
    LOC_LIST_ENTRY_COMPILER = (
        By.XPATH, '(//article[contains(@class, "tech-item")])[{i}]'  # 1-based!
                  '//li[text()="Compiler: {compiler}"]'
    )
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
            if e.get('compiler'):
                locator = self.format_locator(
                    self.LOC_LIST_ENTRY_COMPILER, i=i_xpath,
                    compiler=e['compiler'])
                self.get_el(locator)


class ReviewMixin:
    LOC_BUTTON_REVIEW_ACTION = (
        By.XPATH, '//a[@data-reveal-id="confirm-{action}"]')
    LOC_BUTTON_REVIEW_CONFIRM = (By.XPATH, '//button[@name="{action}"]')
    LOC_BUTTONS_REVIEW_ACTIONS = (
        By.XPATH, '//div[contains(@class, "review-panel")]//a[contains(@class, '
                  '"button") and contains(@class, "expand")]')
    LOC_BUTTON_CHANGE_COMPILER_PANEL = (
        By.XPATH, '//a[@data-toggle="review-change-compiler-panel" and '
                  'contains(@class, "expand")]')
    LOC_BUTTON_CHANGE_COMPILER = (By.ID, 'button-change-compiler')
    LOC_INPUT_NEW_COMPILER = (By.ID, 'review-change-compiler')
    LOC_INPUT_KEEP_COMPILER_AS_EDITOR = (By.NAME, 'change-compiler-keep-editor')
    LOC_CHANGE_COMPILER_SELECTED = (
        By.XPATH,
        '//div[@id="review-new-compiler"]/div[contains(@class, "alert-box")]')
    LOC_COMPILER = (
        By.XPATH, '//ul[@class="tech-infos"]/li/span[text()="Compiler:"]/../a')
    LOC_EDITORS = (
        By.XPATH,
        # Can be "Editor/s:" ...
        '//ul[@class="tech-infos"]/li/span[contains(text(), "Editor")]/../a')
    LOC_STATUS_LABEL = (By.XPATH, '//span[contains(@class, "is-{status}")]')
    TEXT_REVIEW_ACTION_CHANGE_COMPILER = 'Change compiler'
    TEXT_REVIEW_ACTION_DELETE_QUESTIONNAIRE = 'Delete'
    TEXT_MESSAGE_NO_VALID_NEW_COMPILER = 'No valid new compiler provided!'
    TEXT_MESSAGE_COMPILER_CHANGED = 'Compiler was changed successfully'
    TEXT_MESSAGE_USER_ALREADY_COMPILER = 'This user is already the compiler.'

    def do_review_action(self, action: str):
        btn_locator = self.format_locator(
            self.LOC_BUTTON_REVIEW_ACTION, action=action)
        self.get_el(btn_locator).click()
        confirm_locator = self.format_locator(
            self.LOC_BUTTON_REVIEW_CONFIRM, action=action)
        self.wait_for(confirm_locator)
        self.get_el(confirm_locator).click()
        assert self.has_success_message()

    def delete_questionnaire(self):
        self.do_review_action('delete')

    def submit_questionnaire(self):
        self.do_review_action('submit')

    def review_questionnaire(self):
        self.do_review_action('review')

    def publish_questionnaire(self):
        self.do_review_action('publish')

    def get_review_actions(self) -> list:
        return [el.text for el in self.get_els(self.LOC_BUTTONS_REVIEW_ACTIONS)]

    def open_change_compiler_panel(self):
        self.get_el(self.LOC_BUTTON_CHANGE_COMPILER_PANEL).click()

    def click_change_compiler(self):
        self.wait_for(self.LOC_BUTTON_CHANGE_COMPILER)
        self.get_el(self.LOC_BUTTON_CHANGE_COMPILER).click()

    def change_compiler(
            self, compiler: str, keep_as_editor: bool=False, submit: bool=True):
        self.open_change_compiler_panel()
        self.get_el(self.LOC_INPUT_NEW_COMPILER).send_keys(
            compiler.split(' ')[0])
        self.select_autocomplete(compiler)
        if keep_as_editor is True:
            self.select_keep_compiler_as_editor()
        if submit is True:
            self.click_change_compiler()

    def select_keep_compiler_as_editor(self):
        self.get_el(self.LOC_INPUT_KEEP_COMPILER_AS_EDITOR).click()

    def can_enter_new_compiler(self) -> bool:
        return not self.get_el(
            self.LOC_INPUT_NEW_COMPILER).get_attribute('disabled')

    def get_selected_compilers(self) -> list:
        return [
            el.text.replace('\n×', '') for el in
            self.get_els(self.LOC_CHANGE_COMPILER_SELECTED)]

    def can_change_compiler(self) -> bool:
        return self.TEXT_REVIEW_ACTION_CHANGE_COMPILER in \
               self.get_review_actions()

    def can_delete_questionnaire(self) -> bool:
        return self.TEXT_REVIEW_ACTION_DELETE_QUESTIONNAIRE in \
               self.get_review_actions()

    def get_compiler(self) -> str:
        """From the details view, return the name of the compiler"""
        return self.get_el(self.LOC_COMPILER).text

    def get_editors(self) -> list:
        """From the details view, return the names of the editors"""
        return [el.text for el in self.get_els(self.LOC_EDITORS)]

    def check_status(self, status: str):
        self.get_el(self.format_locator(self.LOC_STATUS_LABEL, status=status))


class EditMixin(ReviewMixin):

    LOC_CATEGORIES_PROGRESS_INDICATORS = (
        By.XPATH, '//div[@class="tech-section-progress"]')
    LOC_CATEGORY_TITLE = (By.XPATH, '//h2[contains(text(), "{category}")]')
    LOC_BUTTON_EDIT_CATEGORY = (
        By.XPATH, '//a[contains(@href, "/edit/") and contains('
                  '@href, "{keyword}")]')
    LOC_BUTTON_VIEW_QUESTIONNAIRE = (
        By.XPATH, '//div[contains(@class, "review-panel")]//a[contains(@class, '
                  '"success") and contains(@href, "/view/")]')

    def get_progress_indicators(self):
        return self.get_els(self.LOC_CATEGORIES_PROGRESS_INDICATORS)

    def get_category_by_name(self, name: str):
        locator = self.format_locator(self.LOC_CATEGORY_TITLE, category=name)
        return self.get_el(locator)

    def click_edit_category(self, keyword: str):
        self.hide_notifications()
        locator = self.format_locator(
            self.LOC_BUTTON_EDIT_CATEGORY, keyword=keyword)
        self.get_el(locator).click()

    def view_questionnaire(self):
        self.get_el(self.LOC_BUTTON_VIEW_QUESTIONNAIRE).click()
        assert self.has_success_message()


class DetailMixin(ReviewMixin):

    LOC_BUTTON_CREATE_NEW_VERSION = (
        By.XPATH, '//a[@type="submit" and contains(@href, "/edit/")]')
    LOC_BUTTON_EDIT_QUESTIONNAIRE = (
        By.XPATH, '//div[contains(@class, "review-panel")]//a[contains(@class, '
                  '"button") and contains(@href, "/edit/")]')
    TEXT_REVIEW_ACTION_CREATE_NEW_VERSION = 'Create new version'
    TEXT_REVIEW_ACTION_EDIT_QUESTIONNAIRE = 'Edit'

    def create_new_version(self):
        btn_locator = self.format_locator(
            EditMixin.LOC_BUTTON_REVIEW_ACTION, action='edit')
        self.get_el(btn_locator).click()
        confirm_locator = self.LOC_BUTTON_CREATE_NEW_VERSION
        self.wait_for(confirm_locator)
        self.get_el(confirm_locator).click()
        assert self.has_success_message()

    def edit_questionnaire(self):
        self.get_el(self.LOC_BUTTON_EDIT_QUESTIONNAIRE).click()
        assert self.has_success_message()

    def can_create_new_version(self):
        return self.TEXT_REVIEW_ACTION_CREATE_NEW_VERSION in \
               self.get_review_actions()

    def can_edit_questionnaire(self):
        return self.TEXT_REVIEW_ACTION_EDIT_QUESTIONNAIRE in \
               self.get_review_actions()
