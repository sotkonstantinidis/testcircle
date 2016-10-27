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
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data
    """
    def __init__(self, config: QuestionnaireConfiguration, **data):
        # self.raw_data = ConfiguredQuestionnaireSummary(
        #     config=config, **data
        # ).data
        # self.data = self.get_data()
        self.data = self.get_demo_dict()

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

    def get_demo_dict(self) -> dict:
        """
        Return static dict during development.

        - 'sections' are defined by the configuration ('is_in_summary' value)
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
