import json

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
            for index, image in enumerate(image_urls[:2]):
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

    def references(self):
        return {
            "title": _("References"),
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
                'conclusion', 'references']

    def location(self):
        return {
            "title": _("Location"),
            "partials": {
                "map": {
                    "url": self.raw_data.get('location_map_data').get('img_url')
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
                        'location_map_data'
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
                    "url": self.raw_data.get('location_map_data').get('img_url')
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
                        'location_map_data'
                    ).get('coordinates'),
                    "initiation": {
                        "title": _("Initiation date"),
                        "text": self.raw_data_getter('location_initiation_year') or _("unknown")
                    },
                    "termination": {
                        "title": _("Year of termination"),
                        "text": self.raw_data_getter('location_termination_year') or '*'
                    },
                    "type": {
                        "title": _("Type of Approach"),
                        "items": self.raw_data.get('location_type')
                    }
                }
            }
        }
