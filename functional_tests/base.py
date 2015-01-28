from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from nose.plugins.attrib import attr
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

loginRouteName = 'login'


@attr('functional')
class FunctionalTest(StaticLiveServerTestCase):

    fixtures = ['sample.json']

    def setUp(self):
        self.browser = webdriver.Firefox()
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

    def checkOnPage(self, text):
        self.assertIn(text, self.browser.page_source)

    def changeLanguage(self, locale):
        self.findBy('name', 'setLang%s' % locale).submit()

    def doLogin(self, username, password):
        self.browser.get(self.live_server_url + reverse(loginRouteName))
        self.findBy('name', 'email').send_keys(username)
        self.findBy('name', 'password').send_keys(password)
        self.findBy('id', 'button_login').click()
        self.browser.implicitly_wait(3)
