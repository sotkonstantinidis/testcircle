from django.core.urlresolvers import reverse
from django.test.client import RequestFactory

from qcat.tests import TestCase


route_home = 'wocat:home'


class WocatHomeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = reverse(route_home)

    def test_renders_correct_template(self):
        res = self.client.get(self.url)
        self.assertTemplateUsed(res, 'wocat/home.html')
        self.assertEqual(res.status_code, 200)
