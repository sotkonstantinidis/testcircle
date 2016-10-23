from configuration.configuration import QuestionnaireConfiguration
from configuration.configured_questionnaire import ConfiguredQuestionnaireSummary


def get_summary_data(config: QuestionnaireConfiguration, **data):
    """
    Load summary config according to configuration.
    """
    if config.keyword == 'technologies':
        return TechnologySummaryProvider(config=config, **data).data
    raise Exception('Summary not configured.')


class SummaryDataProvider:
    """
    - Load summary-config according to configuration
    - load configured questionnaire
    - select fields
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data

    key question: where is the summary-config stored?
    - existing configuration object
    - new configuration object

    define fields for summary on configuration.
    """
    def __init__(self, config: QuestionnaireConfiguration, **data):
        self.raw_data = ConfiguredQuestionnaireSummary(config=config, **data).data
        self.data = self.get_data()

    def get_data(self):
        data = []
        for field in self.fields:
            data.append({
                'type': field['type'],
                'label': self.raw_data[field['key']]['label'],
                'content': self.raw_data[field['key']]['value'],
                'position': field['position']
            })
        return data

    @property
    def fields(self):
        raise NotImplementedError


class TechnologySummaryProvider(SummaryDataProvider):
    """
    Store configuration for annotation, aggregation, module type and order for
    technology questionnaires.
    """
    fields = [
        {
            'type': 'image',
            'key': 'qg_image.image',
            'position': '',
        },
        {
            'type': 'text',
            'key': 'qg_name.name',
            'position': ''
        }
    ]
