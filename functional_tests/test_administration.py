from functional_tests.base import FunctionalTest
from selenium.common.exceptions import NoSuchElementException
from django.contrib.auth.models import Group

from accounts.models import User


class AdminTest(FunctionalTest):

    fixtures = ['groups_permissions.json']

    def setUp(self):
        super(AdminTest, self).setUp()
        user = User.create_new('a@b.com')
        user.is_superuser = True
        user.save()

    def test_admin_page_superuser(self):

        # Alice logs in
        self.doLogin('a@b.com', 'foo')

        # She sees the admin button in the top navigation bar and clicks on it
        navbar = self.findBy('class_name', 'top-bar')
        navbar.find_element_by_link_text('Administration').click()

        column_1 = self.findBy('id', 'column_1')
        module_1 = self.findBy('id', 'module_1', base=column_1)
        module_1.find_element_by_link_text('Users')
        module_2 = self.findBy('id', 'module_2', base=column_1)
        module_2.find_element_by_link_text('Categories')
        module_2.find_element_by_link_text('Configurations')
        module_2.find_element_by_link_text('Keys')
        module_3 = self.findBy('id', 'module_3', base=column_1)
        module_3.find_element_by_link_text('Translations')
        module_4 = self.findBy('id', 'module_4', base=column_1)
        module_4.find_element_by_link_text('Statuses')

        with self.assertRaises(NoSuchElementException):
            column_1.find_element_by_id('module_5')

    def test_admin_page_translators(self):

        user = User.create_new('foo@bar.com')
        user.groups.add(Group.objects.filter(name='Translators').first())
        user.save()

        # Alice logs in
        self.doLogin('foo@bar.com', 'foo')

        # She sees the admin button in the top navigation bar and clicks on it
        navbar = self.findBy('class_name', 'top-bar')
        navbar.find_element_by_link_text('Administration').click()

        column_1 = self.findBy('id', 'column_1')
        module_3 = self.findBy('id', 'module_3', base=column_1)
        module_3.find_element_by_link_text('Translations')

        with self.assertRaises(NoSuchElementException):
            column_1.find_element_by_id('module_2')
