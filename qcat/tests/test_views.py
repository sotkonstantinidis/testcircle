from qcat.tests import TestCase


qcat_route_home = 'home'
qcat_route_about = 'about'


class HomePageTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def test_home_page_renders_correct_template(self):
        res = self.client.get('/')
        self.assertTemplateUsed(res, 'home.html')
