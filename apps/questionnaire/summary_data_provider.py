from configuration.configuration import QuestionnaireConfiguration
from configuration.configured_questionnaire import ConfiguredQuestionnaireSummary


def get_summary_data(config: QuestionnaireConfiguration, summary_type: str, **data):
    """
    Load summary config according to configuration.
    """
    if config.keyword == 'technologies' and summary_type == 'full':
        return TechnologyFullSummaryProvider(
            config=config, **data
        ).data
    raise Exception('Summary not configured.')


class SummaryDataProvider:
    """
    - Load summary-config according to configuration
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data
    """

    def __init__(self, config: QuestionnaireConfiguration, **data):
        """
        Load full (raw) data in the same way that it is created for the API and
        apply data transformations to self.data.
        """
        self.raw_data = ConfiguredQuestionnaireSummary(
            config=config, summary_type=self.summary_type, **data
        ).data
        self.data = self.get_data()
        # self.data = self.get_demo_dict()

    def get_data(self):
        data = []
        for field in self.fields:
            data.append({
                'type': field['type'],
                # 'label': self.raw_data[field['key']]['label'],
                # 'content': self.raw_data[field['key']]['value'],
            })
        return data

    def get_demo_dict(self) -> dict:
        """
        Return static dict during development.

        - 'sections' are defined by the configuration ('in_summary' value)
        - how do we handle i18n for section titles?
        - sections need metadata (show title bar; columns and position; page breaks)
        - 'modules' are ordered inside of section
        - placement of modules? also in section-metadata?
        """
        return [
            {
                'title': 'header_image',
                'show_header_bar': False,
                'css_class': '',
                'elements': [
                    {
                        'type': 'image',
                        'url': 'foo.jpg'
                    },
                    {
                        'type': 'caption',
                        'title': '',
                        'text': ''
                    }
                ]
            },
            {
                'title': 'title',
                'show_header_bar': False,
                'css_class': '',
                'elements': [
                    {
                        'type': 'h1',
                        'text': 'Zhuanglang level bench Loess terraces',
                    },
                    {
                        'type': 'h1-addendum',
                        'text': 'P.R. China'
                    },
                    {
                        'type': 'image',
                        'url': 'project.jpg'
                    },
                    {
                        'type': 'image',
                        'url': 'institution.jpg'
                    }
                ]
            },
            {
                'title': 'description',
                'show_header_bar': True,
                'css_class': 'is-technology',
                'elements': [

                ]
            }
        ]

    @property
    def summary_type(self):
        raise NotImplementedError

    @property
    def fields(self):
        raise NotImplementedError


class TechnologyFullSummaryProvider(SummaryDataProvider):
    """
    Store configuration for annotation, aggregation, module type and order for
    technology questionnaires.
    """
    summary_type = 'full'

    fields = [
        {
            'type': 'image',
            'key': 'qg_image.image',
        },
        {
            'type': 'text',
            'key': 'qg_name.name',
        }
    ]
