from functional_tests.base import FunctionalTest
from accounts.tests.test_authentication import get_mock_do_auth_return_values
from unittest.mock import patch


@patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
class LoginTest(FunctionalTest):

    def test_login(self, mock_do_auth):

        mock_do_auth.return_value = None

        # Alice opens her web browser and goes to the home page
        self.browser.get(self.live_server_url)

        # She sees the top naviation bar with the login button, on which she
        # clicks.
        navbar = self.findBy('class_name', 'top-bar')
        navbar.find_element_by_link_text('Login').click()

        login_url = self.browser.current_url

        # She tries to submit the form empty and sees that the form was
        # not submitted.
        self.findBy('id', 'button_login').click()
        self.findBy('name', 'user')

        # She enters some (wrong) user credentials
        self.findBy('name', 'user').send_keys('wrong@user.com')
        self.findBy('name', 'pass').send_keys('wrong')

        # She tries to submit the form and sees an error message
        self.findBy('id', 'button_login').click()

        self.checkOnPage('WOCAT login failure')
        # self.findBy('class_name', 'alert-box')
        # self.checkOnPage('not correct')

        mock_do_auth.return_value = get_mock_do_auth_return_values()
        self.browser.get(login_url)

        # She enters some correct credentials
        email_field = self.findBy('name', 'user')
        email_field.clear()
        email_field.send_keys('correct@user.com')
        self.findBy('name', 'pass').send_keys('correct')
        self.findBy('id', 'button_login').click()

        self.browser.get(login_url)
        self.browser.add_cookie({'name': 'fe_typo_user', 'value': 'foo'})
        self.browser.get(login_url)

        self.checkOnPage('Logout')

        # She submits the form and notices she is being redirected to the home
        # page and she is now logged in (the top bar showing a logout button).
        # self.assertEqual(self.browser.current_url, self.live_server_url + '/')
        # navbar = self.findBy('class_name', 'top-bar')
        # navbar.find_element_by_link_text('Logout')


# @patch('accounts.authentication.WocatAuthenticationBackend._do_auth')
# class LogoutTest(FunctionalTest):

#     def test_logout(self, mock_do_auth):

#         mock_do_auth.return_value = ('tempsessionid')

#         # Alice logs in
#         self.doLogin('a@b.com', 'foo')

#         # She sees a logout button in the top navigation bar and clicks on it
#         navbar = self.findBy('class_name', 'top-bar')
#         navbar.find_element_by_link_text('Logout').click()

#         # She notices she was redirected to the home page and is now logged
#         # out (the top bar showing a login button)
#         self.assertEqual(self.browser.current_url, self.live_server_url + '/')
#         navbar = self.findBy('class_name', 'top-bar')
#         navbar.find_element_by_link_text('Login')
