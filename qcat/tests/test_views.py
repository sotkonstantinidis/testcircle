from django.test import TestCase


class HomePageTest(TestCase):

    fixtures = ['sample.json']

    def test_home_page_renders_correct_template(self):
        res = self.client.get('/')
        self.assertTemplateUsed(res, 'home.html')
