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
        self.raw_data = ConfiguredQuestionnaireSummary(
            config=config, summary_type=self.summary_type, **data
        ).data
        self.data = self.get_data()
        # self.data = self.get_demo_dict()

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
                    {
                        'type': 'lead',
                        'text': 'Level bench terraces on the Loess Plateau, converting eroded and degraded sloping land into a series of steps suitable for cultivation.'
                    },
                    {
                        'type': 'text',
                        'text': 'The Loess Plateau in north-central China is characterised by very deep loess parent material (up to 200 m), that is highly erodible and the source of most of the sediment in the lower reaches of the Yellow River. The plateau is highly dissected by deep gullied valleys and gorges. The steep slopes, occupying 30-40% of the plateau area, have been heavily degraded by severe top soil and gully erosion. Over the whole Loess Plateau 73,350 km2 of these erosion prone slopes have been conserved by terraces. In Zhuanglang County the land that is suitable for terracing has been completely covered. The total terraced area is 1,088 km2, accounting for 90% of the hillsides. The terraces were constructed manually, starting at the bottom of the slopes and proceeding from valley to the ridge. The terraces comprise a riser of earth, with vertical or steeply sloping sides and an approximately flat bed (level bench). Depending on farmers preference some terrace beds are edged by a raised lip (a small earth ridge) which retains rainwater, others remain without lip. The semi-arid climate does not require a drainage system. For typical hillside terraces on slopes of 25-35% the bed width is about 3.5-5 metres with a 1-2 metre riser, involving moving about 2,000-2,500 cubic metres of soil (see table of technical specifications). Generally the risers are not specifically protected, but there may be some natural grasses growing on the upper part. The lower part of the riser is cut vertically into the original soil surface, and has no grass cover, being dry and compact. However it is not erosion-prone since it has a stable structure. Over most of the Loess Plateau, the soil is very deep and therefore well suited to terrace construction. In addition to downstream benefits, the purpose is to create a better environment for crop production through improved moisture conservation, and improved ease of farming operations. In an average rainfall year, crop yields on terraced land are more than three times higher than they used to be on unterraced, sloping land. The implication is that terrace construction – though labour intensive – pays back in only three to four years when combined with agronomic improvements (such as applying farm yard manure and planting green manure). Some farmers try to make the best use of the upper part of terrace risers by planting cash trees or forage crops. This is locally termed ‘terrace bund economy’. The plants stabilise the risers and at the same time provide extra benefits. Some farmers try to make the best use of the upper part of terrace risers by planting cash trees or forage crops. This is locally termed ‘terrace bund economy’. The plants stabilise the risers and at the same time provide extra benefits. Some farmers try to make the best use of the upper part of terrace risers by planting cash trees or forage crops. This is locally termed ‘terrace bund economy’. The plants stabilise the risers and at the same time provide extra benefits'

                    }
                ]
            },
            {
                'title': 'classification of the technology',
                'show_header_bar': True,
                'css_class': 'is-technology',
                'elements': [
                    {
                        'title': 'land use',
                        'elements': [
                            {
                                'type': 'image-label',
                                'img': '/icon-wheat.png',
                                'label': 'Annual cropping',
                                'text': 'Main crops: wheat, maize, potato, peas, millet, sorghum'
                            },
                            {
                                'type': 'image-label',
                                'img': '/icon-wood.png',
                                'label': '(Semi-)natural forests/ woodlands',
                                'text': 'Selective felling; used for timber, fuelwood, other forest products'
                            }
                        ]
                    },
                    {
                        'title': '',
                        'elements': [
                            {
                                'type': 'list-element',
                                'label': 'Land use before implementation of the Technology',
                                'text': 'Wasteland'
                            },
                            {
                                'type': 'list-element',
                                'label': 'Water supply',
                                'text': 'Mixed rainfed-irrigated'
                            },
                            {
                                'type': 'list-element',
                                'label': 'Number of growing seasons per year',
                                'text': '2'
                            },
                        ]
                    },
                    {
                        'title': 'Main purpose',
                        'elements': [
                            {
                                'type': 'list-element',
                                'label': '',
                                'text': 'reduce, prevent, restore land degradation'
                            },
                            {
                                'type': 'list-element',
                                'label': '',
                                'text': 'conserve ecosystem'
                            },
                            {
                                'type': 'list-element',
                                'label': '',
                                'text': 'protect a watershed / downstream areas'
                            },
                        ]
                    },
                    {
                        'title': 'Degradation addressed (s.a.p.)',
                        'elements': [
                            {
                                'type': 'image-label',
                                'img': '/icon-water-erosion.png',
                                'label': '',
                                'text': 'Soil erosion by water: loss of topsoil, gully erosion'
                            },
                            {
                                'type': 'image-label',
                                'img': '/icon-chemical-degradation.png',
                                'label': '',
                                'text': 'Chemical degradation: fertility decline and reduced organic matter content'
                            }
                        ]
                    },
                    {
                        'title': 'Purpose related to land degradation',
                        'elements': [
                            {
                                'type': 'list-element',
                                'text': 'prevent land degradation'
                            },
                            {
                                'type': 'list-element',
                                'text': 'reduce land degradation'
                            },
                            {
                                'type': 'list-element',
                                'text': 'restore/rehabilitate severely degraded land'
                            },
                            {
                                'type': 'list-element',
                                'text': 'adapt to land degradation'
                            },
                            {
                                'type': 'list-element',
                                'text': 'not applicable'
                            }
                        ]
                    },
                    {
                        'title': 'SLM group',
                        'elements': [
                            {
                                'type': 'list-element',
                                'text': 'Cross-slope barriers'
                            },
                            {
                                'type': 'list-element',
                                'text': 'Irrigation management'
                            },
                            {
                                'type': 'list-element',
                                'text': 'Other: specify'
                            }
                        ]
                    },
                    {
                        'title': 'SLM measures',
                        'elements': [
                            {
                                'type': 'image-label',
                                'img': '/icon-terrace.png',
                                'label': '',
                                'text': 'Structural: Terraces'
                            },
                            {
                                'type': 'image-label',
                                'img': '/icon-vegetative.png',
                                'label': '',
                                'text': 'Vegetative: Grasses and perennial herbaceous plants'
                            },
                            {
                                'type': 'image-label',
                                'img': '/icon-management.png',
                                'label': '',
                                'text': 'Management: traritrara fidirullala jucheissassa'
                            },
                            {
                                'type': 'image-label',
                                'img': '/icon-agronomic.png',
                                'label': '',
                                'text': 'Agronomic : Contour tillage, application of manure'
                            }
                        ]
                    }
                ]
            },
            {
                'title': 'technical drawing',
                'show_header_bar': True,
                'css_class': 'is-technology',
                'elements': [
                    {
                        'type': 'lead',
                        'text': 'Technical specifications'
                    },
                    {
                        'type': 'text',
                        'text': 'Layout of level bench terraces on the Loess Plateau: the lower, vertical section is cut into the compacted soil. Natural grasses – or planted grass/ shrub species – protect the more erodible and less steep upper part of the riser. Species used involve: X, Y and Z plants. he low ‘lip’ is optional (0.2-0.3 m high). Terraces are 1-2 m high (vertical interval), the terrace bed is 3.5 – 5 m long (spacing between terrace risers). In the case study area the original slope is 25-35%. After terracing the slope is 0%. The terrace beds are levelled (no gradient). Insert 1: Method of construction: the volume of soil to be excavated from the hillslope (see table below) equals the volume ‘returned’ to form the outer part of the terrace. Insert 2: Chinese Bench Terrace Technical Specifications.'
                    },
                    {
                        'type': 'image',
                        'url': 'technical-drawing.jpg'
                    }
                ]
            }
        ]

    def get_enriched_elements(self, elements: list):
        """
        Prepare non-empty elements, enriching them with the values from
        raw_values or their methods.
        """
        for element in elements:
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
