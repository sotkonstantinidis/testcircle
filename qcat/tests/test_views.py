from qcat.tests import TestCase


class HomePageTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def test_home_page_renders_correct_template(self):
        res = self.client.get('/')
        self.assertTemplateUsed(res, 'home.html')
