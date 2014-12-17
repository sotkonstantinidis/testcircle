from django.test import TestCase

from configuration.configuration import read_configuration


class ConfigurationConfigurationTest(TestCase):

    fixtures = ['configuration/fixtures/sample.json']

    def test_foo(self):
        x = read_configuration()
        print (x)
