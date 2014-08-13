from django.test import TestCase


class HomePageTest(TestCase):

    def test_home_page_renders_correct_template(self):
        res = self.client.get('/')
        self.assertTemplateUsed(res, 'home.html')
