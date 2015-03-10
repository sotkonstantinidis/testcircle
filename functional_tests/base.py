from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from nose.plugins.attrib import attr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from unittest import skipUnless

from unittest.mock import patch
from accounts.tests.test_authentication import get_mock_do_auth_return_values

loginRouteName = 'login'


def check_firefox_path():
    """
    Check if a path for Firefox to be used by Selenium is specified in
    the (local) settings.

    Returns:
        ``bool``. Returns ``True`` if the setting
        ``TESTING_FIREFOX_PATH`` is set. Returns ``False`` if the
        setting is not present or empty.
    """
    try:
        if settings.TESTING_FIREFOX_PATH != '':
            return True
    except:
        pass
    return False


@skipUnless(check_firefox_path(), "Firefox path not specified")
@attr('functional')
class FunctionalTest(StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Firefox(
            firefox_binary=FirefoxBinary(settings.TESTING_FIREFOX_PATH))
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def findByNot(self, by, el):
        try:
            self.browser.implicitly_wait(0)
            if by == 'class_name':
                self.browser.find_element_by_class_name(el)
            elif by == 'link_text':
                self.browser.find_element_by_link_text(el)
            elif by == 'name':
                self.browser.find_element_by_name(el)
            elif by == 'xpath':
                self.browser.find_element_by_xpath(el)
            elif by == 'id':
                self.browser.find_element_by_id(el)
            else:
                self.fail('Argument "by" = "%s" is not valid.' % by)
            self.fail('Element %s was found when it should not be' % el)
        except NoSuchElementException:
            pass

    def findBy(self, by, el, base=None):
        if base is None:
            base = self.browser
        f = None
        try:
            if by == 'class_name':
                f = base.find_element_by_class_name(el)
            elif by == 'link_text':
                f = base.find_element_by_link_text(el)
            elif by == 'name':
                f = base.find_element_by_name(el)
            elif by == 'xpath':
                f = base.find_element_by_xpath(el)
            elif by == 'id':
                f = base.find_element_by_id(el)
            else:
                self.fail('Argument "by" = "%s" is not valid.' % by)
        except NoSuchElementException:
            self.fail('Element %s was not found by %s' % (el, by))
        return f

    def findManyBy(self, by, el, base=None):
        if base is None:
            base = self.browser
        f = None
        try:
            if by == 'class_name':
                f = base.find_elements_by_class_name(el)
            elif by == 'link_text':
                f = base.find_elements_by_link_text(el)
            elif by == 'name':
                f = base.find_elements_by_name(el)
            elif by == 'xpath':
                f = base.find_elements_by_xpath(el)
            elif by == 'id':
                f = base.find_elements_by_id(el)
            else:
                self.fail('Argument "by" = "%s" is not valid.' % by)
        except NoSuchElementException:
            self.fail('Elements %s were not found by %s' % (el, by))
        return f

    def checkOnPage(self, text):
        self.assertIn(text, self.browser.page_source)

    def changeLanguage(self, locale):
        self.findBy('name', 'setLang%s' % locale).submit()

    @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
    def doLogin(self, username, password, mock_do_auth):
        mock_do_auth.return_value = get_mock_do_auth_return_values(
            username=username)
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({'name': 'fe_typo_user', 'value': 'foo'})
        self.browser.get(self.live_server_url + reverse(loginRouteName))
