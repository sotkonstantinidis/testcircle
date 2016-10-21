from configuration.configuration import QuestionnaireConfiguration
from configuration.configured_questionnaire import ConfiguredQuestionnaire


class SummaryDataProvider:
    """
    - Load summary-config according to configuration
    - load configured questionnaire
    - select fields
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data
    """
    data = {'foo': 'bar'}

    def __init__(self, config: QuestionnaireConfiguration, **data):
        self.summary_config = self.get_summary_config(config.keyword)
        self.raw_data = ConfiguredQuestionnaire(config=config, **data)

    def get_summary_config(self, configuration_code: str) -> dict:
        if configuration_code == 'technologies':
            return {}
