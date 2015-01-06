from configuration.configuration import (
    # read_configuration,
    QuestionnaireConfiguration,
)
from qcat.tests import TestCase


class ConfigurationConfigurationTest(TestCase):

    fixtures = ['groups_permissions.json', 'sample.json']

    def test_foo(self):
        # TODO
        questionnaire_configuration = QuestionnaireConfiguration('unccd')
        # x = read_configuration(questionnaire_configuration, 'unccd')
        # print (x)
