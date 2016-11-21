import json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

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

    if config.keyword == 'approaches' and summary_type == 'full':
        return ApproachesSummaryProvider(
            config=config, **data
        )

    raise Exception('Summary not configured.')


class SummaryDataProvider:
    """
    - Load summary-config according to configuration
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data

    Add values / fields by following these steps:
    - in the config-json, add the summary_type and unique label.
      e.g. "in_summary": {
          "full": "definition"
        }
      this will add the field 'definition' to the raw_values of the provider
      'full'
    - add the field to the 'content' property
    - add a method called 'definition' to the class, which gets the values

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

    def get_data(self) -> dict:
        return {section: getattr(self, section) for section in self.content}

    def get_demo_dict(self) -> dict:
        """
        Demo-file for frontend development.
        """
        pth = '{}/apps/questionnaire/templates/questionnaire/summary/demo.json'
        with open(pth.format(settings.BASE_DIR)) as data:
            return dict(json.load(data))

    @property
    def summary_type(self):
        raise NotImplementedError

    # This is a mapping for the structure of the summary and the fields from
    # the configuration with the content-types (that are important to generate
    # the markup in the frontend).
    # The keys such as 'header_image_image' must be set for the summary_type
    # in the configuration-json.
    @property
    def content(self):
        raise NotImplementedError


class GlobalValuesMixin:
    """
    Mixin for globally configured values
    """
    def raw_data_getter(self, key: str, value='value'):
        try:
            return self.raw_data[key][value] if value else self.raw_data[key]
        except (AttributeError, TypeError):
            return ''

    def header_image(self):
        return {
            'partials': {
                'image': {
                    'url': self.raw_data_getter('header_image_image')
                },
                'caption': {
                    'title': '{}: '.format(_('Title photo')),
                    'text': '{caption} {remarks}\n{name}'.format(
                        caption=self.raw_data_getter('header_image_caption'),
                        remarks=self.raw_data_getter('header_image_remarks'),
                        name=self.raw_data_getter('header_image_photographer')
                    )
                }
            }
        }

    def title(self):
        return {
            'partials': {
                'title': self.raw_data_getter('title_name'),
                'country': self.raw_data_getter('country'),
                'local_name': self.raw_data_getter('title_name_local'),
            }
        }

    def description(self):
        return {
            'title': _('Description'),
            'partials': {
                'lead': self.raw_data_getter('definition'),
                'text': self.raw_data_getter('description')
            }
        }

    def conclusion(self):
        # Combine answers from two questions: strengths compiler and landuser
        pro_list = [
            {'text': item['value']} for item in
            self.raw_data_getter('strengths_compiler', value='') +
            self.raw_data_getter('strengths_landuser', value='')
            ]

        # combine answers from two questions: weaknesses compiler + landuser -
        # and get the 'overcome' value as subtext
        weaknesses_list = []
        weaknesses_datasets = {
            'weaknesses_compiler': 'weaknesses_overcome',
            'weaknesses_landuser': 'weaknesses_landuser_overcome',
        }
        for key_name, overcome_name in weaknesses_datasets.items():
            for index, item in enumerate(self.raw_data_getter(key_name, value='')):
                weaknesses_list.append({
                    'text': item['value'],
                    'subtext': self.raw_data_getter(overcome_name, value='')[index].get('value')
                })
        return {
            "title": _("Conclusion & Comparison"),
            "partials": {
                "pro": {
                    "label": _("Strengths"),
                    "items": pro_list
                },
                "contra": {
                    "label": _("Weaknesses/ disadvantages/ risks and how they can be overcome"),
                    "items": weaknesses_list
                }
            }
        }


class TechnologyFullSummaryProvider(GlobalValuesMixin, SummaryDataProvider):
    """
    Configuration for 'full' technology summary.
    """
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'description', 'conclusion']


class ApproachesSummaryProvider(GlobalValuesMixin, SummaryDataProvider):
    """
    Configuration for 'full' approaches summary.
    """
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'description']
