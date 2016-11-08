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
        # self.raw_data = ConfiguredQuestionnaireSummary(
        #     config=config, summary_type=self.summary_type, **data
        # ).data
        # self.data = self.get_data()
        self.data = self.get_demo_dict()

    def get_data(self) -> dict:
        data = {}
        for section, fields in self.content.items():
            data[section] = {
                'has_header_bar': fields.get('has_header_bar', False),
                'title': str(fields.get('title', '')),
                'elements': list(self.get_enriched_elements(fields['elements']))
            }
        return data

    def get_demo_dict(self) -> dict:
        """
        Demo-file for frontend development.
        """
        pth = '{}/apps/questionnaire/templates/questionnaire/summary/demo.json'
        with open(pth.format(settings.BASE_DIR)) as data:
            return dict(json.load(data))

    def get_enriched_elements(self, elements: list):
        """
        Prepare non-empty elements, enriching them with the values from
        raw_values or their methods.
        """
        for element in elements:
            # 'raw' may be empty string, in which case the field is omitted.
            if self.raw_data[element['raw']]:
                if element.get('use_method'):
                    value = element['use_method']
                    label = ''
                else:
                    label = str(self.raw_data[element['raw']].get('key', ''))
                    value = self.raw_data[element['raw']].get('value')
                yield {
                    'module': element['module'],
                    'field_name': element['raw'],
                    'label': label,
                    'value': value
                }

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


class TechnologyFullSummaryProvider(SummaryDataProvider):
    """
    Store configuration for annotation, aggregation, module type and order for
    technology questionnaires.
    """
    summary_type = 'full'

    @property
    def content(self):
         return {
             'header': {
                 'elements': [
                     {
                         'module': 'image',
                         'raw': 'header_image_image'
                     },
                     {
                         'raw': 'header_image_remarks',
                         'module': 'text'
                     },
                     {
                         'raw': 'header_image_caption',
                         'module': 'lead'
                     },
                     {
                         'raw': 'header_image_photographer',
                         'module': 'image'
                     }
                 ]
             },
             'title': {
                 'title': _('Title'),
                 'has_header_bar': True,
                 'elements': [
                     {
                         'module': 'h1',
                         'raw': 'title_name'
                     },
                     {
                         'module': 'h1-addendum',
                         'raw': 'title_name_local'
                     }
                 ]
             },
             'description': {
                 'title': _('Desciption'),
                 'has_header_bar': True,
                 'elements': [
                     {
                         'module': 'text',
                         'use_method': self.combine_fields(
                             'definition', 'description'
                         ),
                         'raw': 'definition'
                     }
                 ]
             },
             'classification_of_the_technology': {
                 'title': _('Classification of the technology'),
                 'has_header_bar': True,
                 'elements': []
             }
        }

    def combine_fields(self, *sections):
        return '\n'.join([self.raw_data[section]['value'] for section in sections])
