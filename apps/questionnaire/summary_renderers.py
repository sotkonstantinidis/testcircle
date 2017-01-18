"""
Prepare data as required for the summary frontend templates.
"""
import json
from itertools import islice

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from configuration.configuration import QuestionnaireConfiguration
from .summary_parsers import ConfiguredQuestionnaireParser, TechnologyParser, \
    ApproachParser
from .models import Questionnaire, QuestionnaireLink


def get_summary_data(config: QuestionnaireConfiguration, summary_type: str,
                     questionnaire: Questionnaire, **data):
    """
    Load summary config according to configuration.
    """
    if config.keyword == 'technologies' and summary_type == 'full':
        return TechnologyFullSummaryRenderer(
            config=config, questionnaire=questionnaire, **data
        ).data

    if config.keyword == 'approaches' and summary_type == 'full':
        return ApproachesSummaryRenderer(
            config=config, questionnaire=questionnaire, **data
        ).data

    raise Exception('Summary not configured.')


class SummaryRenderer:
    """
    - Load summary-config according to configuration
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data

    Add values / fields by following these steps:
    - in the config-json, add the summary_type and unique label.
      e.g. "in_summary": {
          "types": ["full"],
          "default": {
            "field_name": "location_termination_year"
          }
        }
      this will add the field 'location_termination_year' to the raw_values of
      the parser 'full'
    - add the field to the 'content' property of the renderer
    - add a method called 'definition' to the renderer, which gets the values

    """
    parser = ConfiguredQuestionnaireParser

    def __init__(self, config: QuestionnaireConfiguration,
                 questionnaire: Questionnaire, **data):
        """
        Load full (raw) data in the same way that it is created for the API and
        apply data transformations/parsing to self.data.
        """
        self.raw_data = self.parser(
            config=config, summary_type=self.summary_type,
            questionnaire=questionnaire, **data
        ).data
        self.questionnaire = questionnaire
        self.data = dict(self.get_data())
        # self.data = self.get_demo_dict(config_type=config.keyword)

    def get_data(self):
        """
        This is not a dict comprehension as access to 'self' is needed. See
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
            val = self.raw_data[key][0][value] if value else self.raw_data[key]
            return val if val else ''
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
            # first element is the header image, show max. 2 images.
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
            {'text': _('Full case study in WOCAT DB: <a href="{base_url}{url}">'
                     '{base_url}{url}</a>'.format(
                base_url=base_url,
                url=self.questionnaire.get_absolute_url()
            ))}
        ]
        links = QuestionnaireLink.objects.filter(
            from_questionnaire=self.questionnaire
        ).prefetch_related('to_questionnaire')
        if links.exists():
            for link in links:
                link_items.append({
                    'text': _('Corresponding entry in DB: <a href="{base_url}{url}">'
                            '{base_url}{url}</a>'.format(
                        base_url=base_url,
                        url=link.to_questionnaire.get_absolute_url()
                    ))
                })
        vimeo_id = self.raw_data.get('references_vimeo_id')
        if vimeo_id and vimeo_id[0].get('value'):
            vimeo_url = 'https://player.vimeo.com/video/{}'.format(
                vimeo_id[0].get('value')
            )
            link_items.append({
                'text': _('Video: <a href="{vimeo_url}">{vimeo_url}</a>'.format(
                    vimeo_url=vimeo_url))
            })
        return link_items

    def get_reference_articles(self):
        titles = self.raw_data.get('references_title', [])
        sources = self.raw_data.get('references_source', [])
        for index, title in enumerate(titles):
            yield {'text': '{title}: {source}'.format(
                title=title.get('value'),
                source=sources[index].get('value') if sources[index] else '')}

    def project_insitution(self):
        self.raw_data.get('project_institution_project')
        self.raw_data.get('project_institution_institution')
        return {
            "items": [
                {
                    "title": "Food and Agriculture Organization of the United Nations",
                    "logo": ""
                },
                {
                    "title": "Caritas",
                    "logo": ""
                }
            ]
        }


class TechnologyFullSummaryRenderer(GlobalValuesMixin, SummaryRenderer):
    """
    Configuration for 'full' technology summary.
    """
    parser = TechnologyParser
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'description', 'images',
                'classification', 'technical_drawing', 'establishment_costs',
                'natural_environment', 'human_environment', 'impacts', 
                'climate_change', 'adoption_adaptation', 'conclusion',
                'references', 'project_insitution']

    def header_image(self):
        data = super().header_image()
        if self.raw_data_getter('header_image_sustainability') == 'Yes':
            data['partials']['note'] = _(
                '<strong>Note</strong>: This technology is problematic with '
                'regard to land degradation, so it cannot be declared a '
                'sustainable land management technology')
        return data

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
                    ],
                    'main_factors': self.raw_data_getter('establishment_determinate_factors'),
                    'main_factors_title': _('Most important factors affecting the costs')
                },
                'establishment': {
                    'title': _('Establishment activities'),
                    'list': self._get_establishment_list_items(
                        'establishment_establishment_activities',
                        'establishment_establishment_measure_type'
                    ),
                    'comment': self.raw_data_getter('establishment_input_comments'),
                    'table': {
                        'title': _('Establishment inputs and costs per ha'),
                        **self.raw_data.get('establishment_input'),
                    }
                },
                'maintenance': {
                    'title': _('Maintenance activities'),
                    'list': self._get_establishment_list_items(
                        'establishment_maintenance_activities',
                        'establishment_maintenance_measure_type'
                    ),
                    'comment': self.raw_data_getter('establishment_maintenance_comments'),
                    'table': {
                        'title': 'Maintenance inputs and costs per ha',
                        **self.raw_data.get('maintenance_input'),
                    }
                }
            }
        }

    def _get_establishment_list_items(self, activity: str, measure: str):
        for index, activity in enumerate(self.raw_data[activity]):
            # Get the measure type for current activity.
            try:
                measure_type = self.raw_data[measure][index]['value']
            except (KeyError, IndexError):
                measure_type = ''

            measure_type = ' ({})'.format(measure_type) if measure_type else ''
            yield {
                'text': '{activity}{measure_type}'.format(
                    activity=activity['value'],
                    measure_type=measure_type
                )}

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
                'convex': {
                    'title': _('Technology is applied in'),
                    'items': self.raw_data.get('natural_env_convex_concave')
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

    def climate_change(self):
        return {
            'title': _('Climate change'),
            'partials': self.raw_data.get('climate_change')
        }
    
    def adoption_adaptation(self):
        return {
            'title': _('Adoption and adaptation'),
            'partials': {
                'adopted': {
                    'title': _('Percentage of land users in the area who have adopted the Technology'),
                    'items': self.raw_data.get('adoption_percentage')
                },
                'adopted_no_incentive': {
                    'title': _('Percentage of land users who adopted the Technology without material incentives'),
                    'items': self.raw_data.get('adoption_spontaneously')
                },
                'adaptation': {
                    'title': _('Adaptation'),
                    'text': _('The technology has been modified recently to adapt to'),
                    'items': self.raw_data.get('adoption_modified')
                },
                'comments': self.raw_data_getter('adoption_comments')
            }
        }
    

class ApproachesSummaryRenderer(GlobalValuesMixin, SummaryRenderer):
    """
    Configuration for 'full' approaches summary.
    """
    summary_type = 'full'
    parser = ApproachParser

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'description', 'images',
                'aims', 'participation', 'technical_support', 'conclusion',
                'references']

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
                    "start_date": {
                        "title": _("Initiation date"),
                        "text": self.raw_data_getter(
                            'location_initiation_year') or _("unknown")
                    },
                    "end_date": {
                        "title": _("Year of termination"),
                        "text": self.raw_data_getter(
                            'location_termination_year') or '*'
                    },
                    "introduction": {
                        "title": _("Type of Approach"),
                        "items": self.raw_data.get('location_type')
                    }
                }
            }
        }

    def aims(self):
        return {
            'title': _('Approach aims and enabling environment'),
            'partials': {
                'main': {
                    'title': _('Main aims / objectives of the approach'),
                    'text': self.raw_data_getter('aims_main')
                },
                'elements': [
                    {
                        'title': _('Conditions enabling the implementation of the Technology/ ies applied under the Approach'),
                        'items': self.raw_data.get('aims_enabling')
                    },
                    {
                        'title': _('Conditions hindering the implementation of the Technology/ ies applied under the Approach'),
                        'items': self.raw_data.get('aims_hindering')
                    }
                ]
            }
        }

    def participation(self):
        lead_agency = self.raw_data_getter('participation_lead_agency')
        return {
            'title': _('Participation and roles of stakeholders involved'),
            'partials': {
                'stakeholders': {
                    'title': _('Stakeholders involved in the Approach and their roles'),
                    'items': self.raw_data.get('participation_stakeholders'),
                    'addendum': _('Lead agency: {}'.format(lead_agency)) if lead_agency else ''
                },
                'involvement': {
                    'title': _('Involvement of local land users/ local communities in the different phases of the Approach'),
                    'partials': self.raw_data.get('participation_involvement_scale')
                },
                'involvement_items': {
                    'title': _('Involvement of local land users/ local communities in the different phases of the Approach'),
                    'partials': self.raw_data.get('participation_involvement')
                },
                'flow_chart': {
                    'url': self.raw_data_getter('participation_flowchart_file'),
                    'title': _('Flow chart'),
                    'text': self.raw_data_getter('participation_flowchart_text')
                },
                'decision_making': {
                    'title': _('Decision-making on the selection of SLM Technology'),
                    'elements': [
                        {
                            'title': _('Decisions were taken by'),
                            'items': self.raw_data.get('participation_decisions_by')
                        },
                        {
                            'title': _('Decisions were made based on:'),
                            'items': self.raw_data.get('participation_decisions_based')
                        }
                    ]
                }
            }
        }

    def technical_support(self):
        if self.raw_data_getter('tech_support_monitoring_systematic') == 'No':
            monitoring_intention = 'This documentation is <i>not</i> intended to be used for monitoring and evaluation'
        else:
            monitoring_intention = 'This documentation is intended to be used for monitoring and evaluation'

        return {
            'title': _('Technical support, capacity building, and knowledge management'),
            'partials': {
                'activities': {
                    'title': 'The following activities or services have been part of the approach',
                    'items': [
                        self.raw_data.get('tech_support_training_is_training'),
                        self.raw_data.get('tech_support_advisory_is_advisory'),
                        self.raw_data.get('tech_support_institutions_is_institution', {}).get('bool'),
                        self.raw_data.get('tech_support_monitoring_is_monitoring'),
                        self.raw_data.get('tech_support_research_is_research')
                    ]
                },
                'training': {
                    'title': 'Capacity building/ training',
                    'elements': [
                        {
                            'title': _('Training was provided to the following stakeholders'),
                            'items': self.raw_data.get('tech_support_training_who')
                        },
                        {
                            'title': _('Form of training'),
                            'items': self.raw_data.get('tech_support_training_form')
                        }
                    ],
                    'list': {
                        'title': _('Subjects covered'),
                        'text': self.raw_data_getter('tech_support_training_subjects')
                    }
                },
                'advisory': {
                    'title': 'Advisory service',
                    'elements': [
                        {
                            'title': 'Advisory service was provided',
                            'items': self.raw_data.get('tech_support_advisory_service'),
                            'description': self.raw_data_getter('tech_support_advisory_description')
                        }
                    ]
                },
                'institution_strengthening': {
                    'title': _('Institution strenghtening'),
                    'subtitle': {
                        'title': _('Institutions have been strengthened / established'),
                        'value': self.raw_data.get('tech_support_institutions_is_institution', {}).get('value')
                    },
                    'elements': [
                        {
                            'title': _('at the following level'),
                            'items': self.raw_data.get('tech_support_institutions_level'),
                            'description': self.raw_data_getter('tech_support_institutions_describe')
                        },
                        {
                            'title': 'Type of support',
                            'items': self.raw_data.get('tech_support_institutions_support'),
                            'description': self.raw_data_getter('tech_support_institutions_support_specify')
                        }
                    ]
                },
                'monitoring': {
                    'title': 'Monitoring and evaluation',
                    'intended': monitoring_intention
                },
                'research': {
                    'title': 'Research',
                    'items': self.raw_data.get('tech_support_research_topics'),
                    'description': self.raw_data_getter('tech_support_research_details')
                }
            }
        }
