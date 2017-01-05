import json
from itertools import islice

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from configuration.configuration import QuestionnaireConfiguration
from .summary_configuration import ConfiguredQuestionnaireSummary
from .models import Questionnaire, QuestionnaireLink


def get_summary_data(config: QuestionnaireConfiguration, summary_type: str,
                     questionnaire: Questionnaire, **data):
    """
    Load summary config according to configuration.
    """
    if config.keyword == 'technologies' and summary_type == 'full':
        return TechnologyFullSummaryProvider(
            config=config, questionnaire=questionnaire, **data
        ).data

    if config.keyword == 'approaches' and summary_type == 'full':
        return ApproachesSummaryProvider(
            config=config, questionnaire=questionnaire, **data
        ).data

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

    def __init__(self, config: QuestionnaireConfiguration,
                 questionnaire: Questionnaire, **data):
        """
        Load full (raw) data in the same way that it is created for the API and
        apply data transformations to self.data.
        """
        self.raw_data = ConfiguredQuestionnaireSummary(
            config=config, summary_type=self.summary_type,
            questionnaire=questionnaire, **data
        ).data
        self.questionnaire = questionnaire
        self.data = dict(self.get_data())
        # self.data = self.get_demo_dict(config_type=config.keyword)

    def get_data(self):
        """
        This is not a dict comprehenstion as access to 'self' is needed. See
        http://stackoverflow.com/a/13913933
        """
        for section in self.content:
            yield section, getattr(self, section)

    def get_demo_dict(self, config_type: str) -> dict:
        """
        Demo-file for frontend development.
        """
        pth = '{}/apps/questionnaire/templates/questionnaire/summary/{}.json'
        with open(pth.format(settings.BASE_DIR, config_type)) as data:
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
        """
        Get the first 'value' for given key from the data.
        """
        # todo: don't return none values, but empty string
        try:
            return self.raw_data[key][0][value] if value else self.raw_data[key]
        except (AttributeError, TypeError, IndexError):
            return ''

    def string_from_list(self, key):
        """
        Concatenate a list of values from the data to a single string.
        """
        try:
            return ', '.join(self.raw_data[key][0].get('values', []))
        except IndexError:
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

    def images(self):
        image_urls = self.raw_data_getter('images_image', value='')
        image_captions = self.raw_data_getter('images_caption', value='')
        image_photographers = self.raw_data_getter(
            'images_photographer', value=''
        )
        images = []
        if image_urls:
            for index, image in islice(enumerate(image_urls), 1, 3):
                images.append({
                    'url': image['value'],
                    'caption': '{caption}\n{photographer}'.format(
                        caption=image_captions[index].get('value') or '',
                        photographer=image_photographers[index].get('value') or ''
                    )}
                )
        return {
            "partials": {
                "images": images
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
            'weaknesses_compiler': 'weaknesses_compiler_overcome',
            'weaknesses_landuser': 'weaknesses_landuser_overcome',
        }
        for key_name, overcome_name in weaknesses_datasets.items():
            for index, item in enumerate(self.raw_data_getter(key_name, value='')):
                weaknesses_list.append({
                    'text': item['value'],
                    'subtext': self.raw_data_getter(overcome_name, value='')[index].get('value')
                })
        return {
            "title": _('Conclusions and lessons learnt'),
            "partials": {
                "pro": {
                    "label": _("Strengths"),
                    "items": pro_list
                },
                "contra": {
                    "label": _("Weaknesses/ disadvantages/ risks and how they "
                               "can be overcome"),
                    "items": weaknesses_list
                }
            }
        }

    def references(self):
        return {
            "title": _('References'),
            "partials": [
                {
                    "title": _("Compiler"),
                    "css_class": "bullets",
                    "items": self.get_reference_compiler()
                },
                {
                    "title": _("Resource persons"),
                    "css_class": "bullets",
                    "items": self.get_reference_resource_persons()
                },
                {
                    "title": _("Links"),
                    "css_class": "bullets",
                    "items": self.get_reference_links()
                },
                {
                    "title": _("Key references"),
                    "css_class": "bullets",
                    "items": self.get_reference_articles()
                }
            ]
        }

    def get_reference_compiler(self):
        members = self.questionnaire.questionnairemembership_set.filter(
            role=settings.QUESTIONNAIRE_COMPILER
        ).select_related('user')
        if members.exists():
            return [
                {'text': '{name} - {email}'.format(
                    name=member.user.get_display_name(),
                    email=member.user.email)
                } for member in members]
        return []

    def get_reference_resource_persons(self):
        """
        Resource persons is either a dictionary with only one element or a list
        which always contains a type and either a user-id or a first/last name.
        The order of type and name correlates, so starting from the type the
        users details are appended.
        """
        resoureperson_types = self.raw_data_getter(
            'references_resourceperson_type', value=''
        )
        person_firstnames = self.raw_data_getter(
            'references_person_firstname', value=''
        )
        person_lastnames = self.raw_data_getter(
            'references_resourceperson_lastname', value=''
        )
        person_user_id = self.raw_data_getter(
            'references_resourceperson_user_id', value=''
        )
        for index, person in enumerate(resoureperson_types):
            if person_user_id[index] and isinstance(person_user_id[index], dict):
                name = person_user_id[index].get('value')
            elif len(person_firstnames) >= index and len(person_lastnames) >= index:
                name = '{first_name} {last_name}'.format(
                    first_name=person_firstnames[index].get('value'),
                    last_name=person_lastnames[index].get('value')
                )
            else:
                continue
            yield {'text': '{name} - {type}'.format(
                name=name, type=', '.join(person.get('values', [])))}

    def get_reference_links(self):
        base_url = 'https://qcat.wocat.net'  # maybe: use django.contrib.site
        link_items = [
            {'text': 'Full case study in WOCAT DB: <a href="{base_url}{url}">'
                     '{base_url}{url}</a>'.format(
                base_url=base_url,
                url=self.questionnaire.get_absolute_url()
            )}
        ]
        links = QuestionnaireLink.objects.filter(
            from_questionnaire=self.questionnaire
        ).prefetch_related('to_questionnaire')
        if links.exists():
            for link in links:
                link_items.append({
                    'text': 'Corresponding entry in DB: <a href="{base_url}{url}">'
                            '{base_url}{url}</a>'.format(
                        base_url=base_url,
                        url=link.to_questionnaire.get_absolute_url()
                    )
                })
        vimeo_id = self.raw_data.get('references_vimeo_id')
        if vimeo_id and vimeo_id[0].get('value'):
            vimeo_url = 'https://player.vimeo.com/video/{}'.format(
                vimeo_id[0].get('value')
            )
            link_items.append({
                'text': 'Video: <a href="{vimeo_url}">{vimeo_url}</a>'.format(
                    vimeo_url=vimeo_url)
            })
        return link_items

    def get_reference_articles(self):
        titles = self.raw_data.get('references_title', [])
        sources = self.raw_data.get('references_source', [])
        for index, title in enumerate(titles):
            yield {'text': '{title}: {source}'.format(
                title=title.get('value'),
                source=sources[index].get('value') if sources[index] else '')}


class TechnologyFullSummaryProvider(GlobalValuesMixin, SummaryDataProvider):
    """
    Configuration for 'full' technology summary.
    """
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'description', 'images',
                'classification', 'technical_drawing', 'establishment_costs',
                'natural_environment', 'human_environment', 'impacts',
                'conclusion', 'references']

    def location(self):
        return {
            "title": _("Location"),
            "partials": {
                "map": {
                    "url": self.raw_data.get('location_map_data', {}).get('img_url')
                },
                "infos": {
                    "location": {
                        "title": _("Location"),
                        "text": "{detail}, {prov}, {country}".format(
                            detail=self.raw_data_getter('location_further'),
                            prov=self.raw_data_getter('location_state_province'),
                            country=self.raw_data_getter('country')
                        )
                    },
                    "sites": {
                        "title": "No. of Technology sites analysed",
                        "text": self.string_from_list('location_sites_considered')
                    },
                    "geo_reference": self.raw_data.get(
                        'location_map_data', {}
                    ).get('coordinates'),
                    "spread": {
                        "title": _("Spread of the Technology"),
                        "text": self.string_from_list('location_spread')
                    },
                    "date": {
                        "title": _("Date of implementation"),
                        "text": self.string_from_list('location_implementation_decade')
                    },
                    "introduction": {
                        "title": _("Type of introduction"),
                        "items": self.raw_data.get('location_who_implemented')
                    }
                }
            }
        }

    def classification(self):
        try:
            slm_group = self.raw_data_getter(
                'classification_slm_group', value=''
            )[0].get('values')
        except (KeyError, IndexError):
            slm_group = None

        return {
            "title": "Classification of the Technology",
            "partials": {
                "main_purpose": {
                    "title": _("Main purpose"),
                    "partials": self.raw_data.get('classification_main_purpose')
                },
                "landuse": {
                    "title": "Land use",
                    "partials": self.raw_data.get('classification_landuse')
                },
                "water_supply": {
                    "title": "Water supply",
                    "partials": {
                        "list": self.raw_data.get('classification_watersupply'),
                        "text": [
                            {
                                "title": "Number of growing seasons per year",
                                "text": self.string_from_list(
                                    'classification_growing_seasons'
                                )
                            },
                            {
                                "title": "Land use before implementation of "
                                         "the Technology",
                                "text": self.raw_data_getter(
                                    'classification_lu_before'
                                )
                            }
                        ]
                    }
                },
                "purpose": {
                    "title": "Purpose related to land degradation",
                    "partials": self.raw_data.get('classification_purpose')
                },
                "degredation": {
                    "title": "Degradation addressed",
                    "partials": self.raw_data.get('classification_degradation')
                },
                "slm_group": {
                    "title": "SLM group",
                    "partials": slm_group
                },
                "measures": {
                    "title": "SLM measures",
                    "partials": self.raw_data.get('classification_measures')
                }
            }
        }

    def technical_drawing(self):
        return {
            'title': _('Technical drawing'),
            'partials': {
                'title': _('Technical specifications'),
                'text': self.raw_data_getter('tech_drawing_text'),
                'urls': [img['value'] for img in self.raw_data.get('tech_drawing_image')]
            }
        }

    def establishment_costs(self):
        base = self.string_from_list('establishment_cost_calculation_base')
        perarea_size = self.raw_data_getter('establishment_perarea_size')
        conversion = self.raw_data_getter('establishment_unit_conversion')
        conversion_text = '; conversion factor to one hectare: {}'.format(conversion)
        explanation = ' (size and area unit: {size}{conversion_text})'.format(
            size=perarea_size,
            conversion_text=conversion_text if conversion else ''
        )
        calculation = '{base}{extra}'.format(
            base=base,
            extra=explanation if perarea_size else ''
        )
        usd = self.string_from_list('establishment_dollar')
        national_currency = self.raw_data_getter('establishment_national_currency')
        currency = usd or national_currency or 'n.a'
        wage = self.raw_data_getter('establishment_average_wage') or _('n.a')
        exchange_rate = self.raw_data_getter('establishment_exchange_rate') or _('n.a')
        return {
            'title': _('Establishment and maintenance: activities, inputs and costs'),
            'partials': {
                'introduction': {
                    'title': _('Calculation of inputs and costs'),
                    'items': [
                        _('Costs are calculated: {}').format(calculation),
                        _('Currency used for cost calculation: {}').format(currency),
                        _('Exchange rate (to USD): {}.').format(exchange_rate),
                        _('Average wage cost of hired labour: {}.').format(wage)
                    ]
                },
                'establishment': {
                    'title': _('Establishment activities'),
                    'list': [{'text': activity['value']} for activity in self.raw_data['establishment_establishment_activities']],
                    'comment': self.raw_data_getter('establishment_input_comments'),
                    'table': {
                        'title': _('Establishment inputs and costs per ha'),
                        'head': {
                            '0': 'Inputs (earth ridge)',
                            '1': 'Costs (US$)',
                            '2': '%  l.u.'
                        },
                        'partials': [
                            {
                                'head': 'Labour',
                                'items': [
                                    {
                                        '0': 'construction: 600 person-days',
                                        '1': '1,200',
                                        '2': '97%'
                                    },
                                    {
                                        '0': 'survey',
                                        '1': '60',
                                        '2': '0'
                                    }
                                ]
                            },
                            {
                                'head': 'Equipment',
                                'items': [
                                    {
                                        '0': 'Tools: shovels, 2 wheel carts',
                                        '1': '30',
                                        '2': '100%'
                                    },
                                    {
                                        '0': 'Machine hours',
                                        '1': '',
                                        '2': ''
                                    }
                                ]
                            },
                            {
                                'head': 'Plant materials',
                                'items': [
                                    {
                                        '0': 'Fruit tree seedling (250 pc.)',
                                        '1': '',
                                        '2': ''
                                    },
                                    {
                                        '0': 'Grass seeds (4 kg)',
                                        '1': '',
                                        '2': ''
                                    }
                                ]
                            },
                            {
                                'head': 'Fertilizers and biocides',
                                'items': [
                                    {
                                        '0': 'Fertilizers (250 kg NPK)',
                                        '1': '',
                                        '2': ''
                                    },
                                    {
                                        '0': 'Biocides (6 kg)',
                                        '1': '',
                                        '2': ''
                                    }
                                ]
                            },
                            {
                                'head': 'Fertilizers and biocides',
                                'items': [
                                    {
                                        '0': 'Fertilizers (250 kg NPK)',
                                        '1': '',
                                        '2': ''
                                    },
                                    {
                                        '0': 'Biocides (6 kg)',
                                        '1': '',
                                        '2': ''
                                    },
                                    {
                                        '0': 'Manure (15 tons)',
                                        '1': '',
                                        '2': ''
                                    }
                                ]
                            },
                            {
                                'head': 'Construction materials',
                                'items': [
                                    {
                                        '0': 'Earth (2,000 – 2,500 m³)',
                                        '1': '0',
                                        '2': '0%'
                                    },
                                    {
                                        '0': 'Sand (250 m³)',
                                        '1': '',
                                        '2': ''
                                    }
                                ]
                            }
                        ],
                        'total': {
                            '0': 'Total',
                            '1': '1290',
                            '2': '93%'
                        }
                    }
                },
                'maintenance': {
                    'title': _('Maintenance activities'),
                    'list': [{'text': activity['value']} for activity in self.raw_data['establishment_maintenance_activities']],
                    'comment': self.raw_data_getter('establishment_maintenance_comments'),
                    'table': {
                        'title': 'Maintenance inputs and costs per ha',
                        'head': {
                            '0': 'Inputs',
                            '1': 'Costs (US$)',
                            '2': '%  l.u.'
                        },
                        'partials': [
                            {
                                'head': 'Labour',
                                'items': [
                                    {
                                        '0': '12 person days',
                                        '1': '25',
                                        '2': '97%'
                                    }
                                ]
                            },
                            {
                                'head': 'Equipment',
                                'items': [
                                    {
                                        '0': 'Tools (shovels, two-wheel carts)',
                                        '1': '10',
                                        '2': '100%'
                                    }
                                ]
                            },
                            {
                                'head': 'Materials',
                                'items': [
                                    {
                                        '0': 'Earth (1-2m3)',
                                        '1': '0',
                                        '2': '0%'
                                    }
                                ]
                            }
                        ],
                        'total': {
                            '0': 'Total',
                            '1': '35',
                            '2': '98%'
                        }
                    }
                }
            }
        }

    def natural_environment(self):
        return {
            'title': _('Natural environment'),
            'partials': {
                'rainfall': {
                    'title': _('Average annual rainfall'),
                    'items': self.raw_data.get('natural_env_rainfall')
                },
                'zone': {
                    'title': _('Agro-climatic zone'),
                    'items': self.raw_data.get('natural_env_climate_zone')
                },
                'specifications': {
                    'title': _('Specifications on climate'),
                    'text': self.raw_data_getter('natural_env_climate_zone_text')
                },
                'slope': {
                    'title': _('Slope'),
                    'items': self.raw_data.get('natural_env_slope')
                },
                'landforms': {
                    'title': _('Landforms'),
                    'items': self.raw_data.get('natural_env_landforms')
                },
                'altitude': {
                    'title': _('Altitude'),
                    'items': self.raw_data.get('natural_env_altitude')
                },
                'soil_depth': {
                    'title': _('Soil depth'),
                    'items': self.raw_data.get('natural_env_soil_depth')
                },
                'soil_texture_top': {
                    'title': _('Soil texture (topsoil)'),
                    'items': self.raw_data.get('natural_env_soil_texture')
                },
                'soil_texture_below': {
                    'title': _('Soil texture (> 20 cm below surface)'),
                    'items': self.raw_data.get('natural_env_soil_texture_below')
                },
                'topsoil': {
                    'title': _('Topsoil organic matter content'),
                    'items': self.raw_data.get('natural_env_soil_organic')
                },
                'groundwater': {
                    'title': _('Groundwater table'),
                    'items': self.raw_data.get('natural_env_groundwater')
                },
                'surface_water': {
                    'title': _('Availability of surface water'),
                    'items': self.raw_data.get('natural_env_surfacewater')
                },
                'water_quality': {
                    'title': _('Water quality (untreated)'),
                    'items': self.raw_data.get('natural_env_waterquality')
                },
                'flooding': {
                    'title': _('Occurrence of flooding'),
                    'items': self.raw_data.get('natural_env_flooding')
                },
                'salinity': {
                    'title': _('Is salinity a problem?'),
                    'items': self.raw_data.get('natural_env_salinity')
                },
                'species': {
                    'title': _('Species diversity'),
                    'items': self.raw_data.get('natural_env_species')
                },
                'habitat': {
                    'title': _('Habitat diversity'),
                    'items': self.raw_data.get('natural_env_habitat')
                }
            }
        }
    
    def human_environment(self):
        return {
            'title': _('Characteristics of land users applying the Technology'),
            'partials': {
                'market': {
                    'title': _('Market orientation'),
                    'items': self.raw_data.get('human_env_market_orientation')
                },
                'income': {
                    'title': _('Off-farm income'),
                    'items': self.raw_data.get('human_env_offfarm_income')
                },
                'wealth': {
                    'title': _('Relative level of wealth'),
                    'items': self.raw_data.get('human_env_wealth')
                },
                'mechanization': {
                    'title': _('Level of mechanization'),
                    'items': self.raw_data.get('human_env_mechanisation')
                },
                'sedentary': {
                    'title': _('Sedentary or nomadic'),
                    'items': self.raw_data.get('human_env_sedentary_nomadic')
                },
                'individuals': {
                    'title': _('Individuals or groups'),
                    'items': self.raw_data.get('human_env_individuals')
                },
                'gender': {
                    'title': _('Gender'),
                    'items': self.raw_data.get('human_env_gender')
                },
                'age': {
                    'title': _('Age'),
                    'items': self.raw_data.get('human_env_age')
                },
                'area': {
                    'title': _('Area used per household'),
                    'items': self.raw_data.get('human_env_land_size')
                },
                'scale': {
                    'title': _('Scale'),
                    'items': self.raw_data.get('human_env_land_size_relative')
                },
                'ownership': {
                    'title': _('Land ownership'),
                    'items': self.raw_data.get('human_env_ownership')
                },
                'land_rights': {
                    'title': _('Land use rights'),
                    'items': self.raw_data.get('human_env_landuser_rights')
                },
                'water_rights': {
                    'title': _('Water use rights'),
                    'items': self.raw_data.get('human_env_wateruser_rights')
                },
                'access': {
                    'title': _('Access to services and infrastructure'),
                    'items': self.raw_data.get('human_env_services')
                }
            }
        }

    def impacts(self):
        return {
            'title': _('Impacts: Benefits and disadvantages'),
            'partials': {
                'economic': {
                    'title': _('Socio-economic impacts'),
                    'items': self.raw_data.get('impacts_cropproduction'),
                },
                'cultural': {
                    'title': _('Socio-cultural impacts'),
                    'items': self.raw_data.get('impacts_foodsecurity')
                },
                'ecological': {
                    'title': _('Ecological impacts'),
                    'items': self.raw_data.get('impacts_soilmoisture')
                },
                'off_site': {
                    'title': _('Off-site impacts'),
                    'items': self.raw_data.get('impacts_downstreamflooding')
                },
                'benefits_establishment': {
                    'title': _('Benefits compared with establishment costs'),
                    'items': self.raw_data.get('impacts_establishment_costbenefit')
                },
                'benefits_maintenance': {
                    'title': _('Benefits compared with maintenance costs'),
                    'items': self.raw_data.get('impacts_maintenance_costbenefit')
                }
            }
        }


class ApproachesSummaryProvider(GlobalValuesMixin, SummaryDataProvider):
    """
    Configuration for 'full' approaches summary.
    """
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'description',
                'conclusion', 'references']

    def location(self):
        return {
            "title": _("Location"),
            "partials": {
                "map": {
                    "url": self.raw_data.get(
                        'location_map_data', {}
                    ).get('img_url')
                },
                "infos": {
                    "location": {
                        "title": _("Location"),
                        "text": "{detail}, {prov}, {country}".format(
                            detail=self.raw_data_getter('location_further'),
                            prov=self.raw_data_getter('location_state_province'),
                            country=self.raw_data_getter('country')
                        )
                    },
                    "geo_reference": self.raw_data.get(
                        'location_map_data', {}
                    ).get('coordinates'),
                    "initiation": {
                        "title": _("Initiation date"),
                        "text": self.raw_data_getter(
                            'location_initiation_year') or _("unknown")
                    },
                    "termination": {
                        "title": _("Year of termination"),
                        "text": self.raw_data_getter(
                            'location_termination_year') or '*'
                    },
                    "type": {
                        "title": _("Type of Approach"),
                        "items": self.raw_data.get('location_type')
                    }
                }
            }
        }
