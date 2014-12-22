from django.test import TestCase
from configuration.configuration import (
    read_configuration,
    QuestionnaireConfiguration,
)


class ConfigurationConfigurationTest(TestCase):

    fixtures = ['sample.json']

    def test_foo(self):
        # TODO
        questionnaire_configuration = QuestionnaireConfiguration('unccd')
        x = read_configuration(questionnaire_configuration, 'unccd')
        print (x)
