"""
Prepare data as required for the summary frontend templates.
"""
import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.utils.translation import ugettext_lazy as _
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from configuration.configuration import QuestionnaireConfiguration
from configuration.models import Project, Institution
from questionnaire.models import Questionnaire, QuestionnaireLink
from .parsers import QuestionnaireParser, TechnologyParser, \
    ApproachParser, Technology2018Parser


class SummaryRenderer:
    """
    - Load summary-config according to configuration
    - annotate and aggregate values
    - add 'module' hint to create markup upon
    - sort data

    Add values / fields by following these steps:
    - in the config-json, add the summary_type and unique label.
      e.g. "summary": {
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
    parser = QuestionnaireParser
    n_a = _('n.a.')

    def __init__(self, config: QuestionnaireConfiguration,
                 questionnaire: Questionnaire, quality: str,
                 base_url: str, **data):
        """
        Load full (raw) data in the same way that it is created for the API and
        apply data transformations/parsing to self.data.
        """
        self.raw_data = self.parser(
            config=config, summary_type=self.summary_type,
            questionnaire=questionnaire, n_a=self.n_a, **data
        ).data
        self.questionnaire = questionnaire
        self.quality = quality
        self.base_url = base_url

    @property
    def summary_type(self):
        """
        The name of the summary type, i.e. 'full', 'onepage'
        """
        raise NotImplementedError

    @property
    def content(self):
        """
        This is a mapping for the structure of the summary and the fields from
        the configuration with the content-types (that are important to generate
        the markup in the frontend).
        The keys such as 'header_image_image' must be set for the summary_type
        in the configuration-json.
        """
        raise NotImplementedError

    def render(self):
        """
        Render all contents, as defined by the @content property.

        """
        for section in self.content:
            method = getattr(self, section)()
            yield render_to_string(
                template_name=method['template_name'],
                context={
                    'content': method.get('partials', {}),
                    'title': method.get('title', ''),
                    'base_url': self.base_url
                }
            )


class GlobalValuesMixin:
    """
    Mixin for globally configured values

    """
    def raw_data_getter(self, key: str, value='value') -> str:
        """
        Get the first 'value' for given key from the data.
        """
        try:
            value = self.raw_data[key][0][value] if value else self.raw_data[key]
            return value or ''
        except (AttributeError, TypeError, KeyError, IndexError):
            return ''

    def string_from_list(self, key: str) -> str:
        """
        Concatenate a list of values from the data to a single string.
        """
        try:
            return ', '.join(self.raw_data[key][0].get('values', []))
        except (IndexError, KeyError):
            return ''

    def get_list_values_with_other(self, key_list_values: str, key_other: str) -> list:
        """
        Append 'other' to any list containing a dict with the keys 'highlight' 
        and 'text'
        """
        base = list(self.raw_data.get(key_list_values))
        other = self.raw_data_getter(key_other)
        if other:
            base.append({
                'highlighted': True,
                'text': other
            })
        return base

    def header_image(self):
        """
        If the header image is empty, use the first element from the default
        pictures element.
        """
        image = self.raw_data_getter('header_image_image')
        if image:
            photographer = self.raw_data_getter('header_image_photographer')
            text = '{caption} {name}'.format(
                caption=self.raw_data_getter('header_image_caption'),
                name='({})'.format(photographer) if photographer else ''
            )
        else:
            image_urls = self.raw_data_getter('images_image', value='')
            text = ''
            if image_urls:
                # use first element from photos, and remove it from the photos
                # element, so the images on display are the 'next' images.
                image_element = self.raw_data['images_image'].pop(0)
                image = image_element['value']
                text = self.get_image_caption(0)
                self.raw_data['images_caption'].pop(0)
                self.raw_data['images_photographer'].pop(0)

        return {
            'template_name': 'summary/block/header_image.html',
            'partials': {
                'image': {
                    'url': self.get_thumbnail_url(
                        image=image,
                        option_key='header_image'
                    )
                },
                'caption': {
                    'text': text
                },
                'wocat_logo_url': '{base_url}{logo}'.format(
                    base_url=self.base_url.rstrip('/'),
                    logo=static('assets/img/wocat_logo_text_shadow.svg')
                )
            }
        }

    def title(self):
        return {
            'template_name': 'summary/block/title.html',
            'partials': {
                'title': self.raw_data_getter('title_name'),
                'country': self.raw_data_getter('country'),
                'local_name': self.raw_data_getter('title_name_local'),
            }
        }

    def images(self):
        # note: data from images_image may be popped in header_image.
        image_urls = self.raw_data_getter('images_image', value='')
        images = []
        if image_urls:
            # first element is the header image, show max. 2 images.
            # Some files may not return a thumbnail and should therefore not be
            # used. Continue to loop all "images" until 2 thumbnails were
            # returned
            for index, image_data in enumerate(image_urls):
                if len(images) >= 2:
                    continue
                # If the file is a PDF, then use the preview_image instead of
                # the actual document
                if image_data['content_type'] == 'application/pdf':
                    image = image_data.get('preview_image', '')
                else:
                    image = image_data.get('value', '')
                url = self.get_thumbnail_url(
                        image=image,
                        option_key='half_height'
                    )
                if not url:
                    continue
                images.append({
                    'url': url,
                    'caption': self.get_image_caption(index)
                })
        return {
            'template_name': 'summary/block/two_images_with_caption.html',
            'partials': {
                'images': images
            }
        }

    def get_image_caption(self, index: int) -> str:
        caption = self._get_caption_info('caption', index)
        photographer = self._get_caption_info('photographer', index)
        return '{caption}{photographer}'.format(
            caption=caption or '',
            photographer=' ({})'.format(photographer) if photographer else ''
        ) or '-'

    def _get_caption_info(self, key: str, index: int) -> str:
        try:
            items = self.raw_data_getter('images_{}'.format(key), value='')[index]
            return items.get('value', '')
        except IndexError:
            return ''

    def conclusion(self):
        land_users_view = _("land user's view")
        compilers_view = _("compiler’s or other key resource person’s view")

        # Combine answers from two questions: strengths compiler and landuser
        pro_compilers = self._get_conclusion_row(
            rows=self.raw_data_getter('strengths_compiler', value='')
        )
        pro_landusers = self._get_conclusion_row(
            rows=self.raw_data_getter('strengths_landuser', value='')
        )
        # combine answers from two questions: weaknesses compiler + landuser -
        # and get the 'overcome' value as subtext
        weakness_compiler = {
            'title': compilers_view,
            'items': []
        }
        weakness_landuser = {
            'title': land_users_view,
            'items': []
        }
        weaknesses_datasets = [
            (weakness_landuser, 'weaknesses_landuser', 'weaknesses_landuser_overcome'),
            (weakness_compiler, 'weaknesses_compiler', 'weaknesses_compiler_overcome'),
        ]
        for container, key_name, overcome_name in weaknesses_datasets:
            for index, item in enumerate(self.raw_data_getter(key_name, value='')):
                subtext = self.raw_data_getter(overcome_name, value='')[index].get('value', '')
                container['items'].append({
                    'text': item['value'],
                    'subtext': subtext,
                })

        return {
            'template_name': 'summary/block/conclusion.html',
            'title': _('Conclusions and lessons learnt'),
            'partials': {
                'pro': {
                    'label': _('Strengths'),
                    'items': [
                        {
                            'title': land_users_view,
                            'items': pro_landusers
                        },
                        {
                            'title': compilers_view,
                            'items': pro_compilers
                        },
                    ]
                },
                'contra': {
                    'label': _('Weaknesses/ disadvantages/ risks'),
                    'subtext': _('how to overcome'),
                    'items': [weakness_landuser, weakness_compiler]
                }
            }
        }

    def _get_conclusion_row(self, rows: []):
        for row in rows:
            yield {'text': row['value']}

    def references(self):
        return {
            'template_name': 'summary/block/references.html',
            'title': _('References'),
            'partials': {
                'meta': {
                    'created': {
                        'title': _('Date of documentation'),
                        'value': self.questionnaire.created
                    },
                    'updated': {
                        'title': _('Last update'),
                        'value': self.questionnaire.updated
                    }
                },
                'compiler': {
                    'title': _('Compiler'),
                    'css_class': 'bullets',
                    'items': self.get_reference_person(role_name='QUESTIONNAIRE_COMPILER')
                },
                'reviewer': {
                    'title': _('Reviewer'),
                    'css_class': 'bullets',
                    'items': self.get_reference_person(role_name='QUESTIONNAIRE_REVIEWER')
                },
                'people': {
                    'title': _('Resource persons'),
                    'css_class': 'bullets',
                    'items': self.get_reference_resource_persons()
                },
                'more': {
                    'title': _('Full description in the WOCAT database'),
                    'css_class': 'bullets',
                    'items': self.get_reference_links()
                },
                'links': {
                    'title': _('Linked SLM data'),
                    'css_class': 'bullets',
                    'items': self.get_reference_linked_questionnaires()
                },
                'references': {
                    'title': _('Key references'),
                    'css_class': 'bullets',
                    'items': list(self.get_reference_articles())
                },
                'web_references': {
                    'title': _('Links to relevant information which is available online'),
                    'css_class': 'bullets',
                    'items': list(self.get_reference_web())
                },
                'project_institution': {
                    'title': _('Documentation was faciliated by'),
                    'projects': {
                        'title': _('Project'),
                        'items': self.get_projects(),
                    },
                    'institutions': {
                        'title': _('Institution'),
                        'items': self.get_institutions(),
                    }
                }
            }
        }

    def get_reference_person(self, role_name: str) -> []:
        members = self.questionnaire.questionnairemembership_set.filter(
            role=getattr(settings, role_name)
        ).select_related('user')
        if members.exists():
            return [
                {'text': '{name} ({email})'.format(
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
        person_emails = self.raw_data_getter(
            'references_person_email', value=''
        )
        person_user_id = self.raw_data_getter(
            'references_resourceperson_user_id', value=''
        )
        person_types_other = self.raw_data_getter(
            'references_person_type_other', value=''
        )

        for index, person in enumerate(resoureperson_types):
            if person_user_id[index] and isinstance(person_user_id[index], dict):
                name = person_user_id[index].get('value')
                try:
                    email = get_user_model().objects.get(
                        id=person_user_id[index]['user_id']
                    ).email
                except ObjectDoesNotExist:
                    email = ''
            elif len(person_firstnames) >= index and len(person_lastnames) >= index:
                name = '{first_name} {last_name}'.format(
                    first_name=person_firstnames[index].get('value') or '',
                    last_name=person_lastnames[index].get('value') or ''
                )
                email=person_emails[index].get('value') or ''
            else:
                continue

            if person.get('values'):
                person_type = ', '.join(person.get('values', []))
            else:
                person_type = person_types_other[index].get('value', '')

            yield {'text': '{name}{email} - {type}'.format(
                name=name,
                email=' ({})'.format(email) if email else '',
                type=person_type)}

    def get_reference_links(self):
        text = '<a href="{base_url}{url}">{base_url}{url}</a>'.format(
            base_url=self.base_url.rstrip('/'),
            url=self.questionnaire.get_absolute_url())

        link_items = [
            {'text': text}
        ]

        vimeo_id = self.raw_data.get('references_vimeo_id')
        if vimeo_id and vimeo_id[0].get('value'):
            vimeo_url = 'https://player.vimeo.com/video/{}'.format(
                vimeo_id[0].get('value')
            )
            link_items.append({
                'text': '{video}: <a href="{vimeo_url}">{vimeo_url}</a>'.format(
                    video=_('Video'), vimeo_url=vimeo_url)
            })
        return link_items or [{'text': self.n_a}]

    def get_reference_linked_questionnaires(self):
        links = QuestionnaireLink.objects.filter(
            from_questionnaire=self.questionnaire,
            to_questionnaire__is_deleted=False
        )
        if not links.exists():
            yield {'text': self.n_a}
        for link in links:
            yield {'text': '{config}: {name} <a href="{base_url}{url}">{base_url}{url}</a>'.format(
                config=link.to_questionnaire.configuration.code.title(),
                name=link.to_questionnaire.get_name(),
                base_url=self.base_url.rstrip('/'),
                url=link.to_questionnaire.get_absolute_url())
            }

    def get_reference_articles(self):
        titles = self.raw_data.get('references_title', [])
        sources = self.raw_data.get('references_source', [])

        for index, title in enumerate(titles):
            if title.get('value'):
                yield {'text': '{title}: {source}'.format(
                    title=title['value'],
                    source=sources[index].get('value') or '' if sources[index] else '')}

    def get_projects(self):
        ids = self.raw_data.get('project_institution_project', [])
        return self._get_project_institutions(Project, *ids)

    def get_institutions(self):
        ids = self.raw_data.get('project_institution_institution', [])
        return self._get_project_institutions(Institution, *ids)

    def _get_project_institutions(self, model, *elements):
        ids = [item['value'] for item in elements]
        objects = model.objects.filter(id__in=ids)
        object_list = [{'title': elem, 'logo': ''} for elem in objects]
        return object_list or [{'title': self.n_a}]

    def get_reference_web(self):
        titles = self.raw_data_getter('references_links_title', value='')
        urls = self.raw_data_getter('references_links_url', value='')
        for index, title in enumerate(titles):
            yield {
                'title': title.get('value'),
                'url': urls[index].get('value')
            }

    def get_thumbnail_url(self, image: str, option_key: str) -> str:
        """
        Images can be either very large images or even pdf files. Create an
        optimized thumbnail and return its url.
        """
        if not image:
            return ''

        # full name is required to prevent a SuspiciousOperation error
        full_name = '{root}/{image}'.format(
            root=settings.MEDIA_ROOT,
            image=image[len(settings.MEDIA_URL):]
        )
        try:
            thumbnail = get_thumbnailer(full_name).get_thumbnail(
                settings.THUMBNAIL_ALIASES['summary'][self.quality][option_key],
                silent_template_exception=True
            )
        except InvalidImageFormatError:
            return ''

        # Use 'abspath' to remove '..' from path.
        media_path = os.path.abspath(settings.MEDIA_ROOT)
        #  Strip away the media folder info - only the last part is required for the url.
        file_path = thumbnail.url[thumbnail.url.find(media_path) + len(media_path):]
        return f'{self.base_url.rstrip("/")}{settings.MEDIA_URL}{file_path}'

    def get_location_values(self, *fields):
        for field in fields:
            value = self.raw_data_getter(field)
            if value:
                yield value


class TechnologyFullSummaryRenderer(GlobalValuesMixin, SummaryRenderer):
    """
    Configuration for 'full' technology summary.
    """
    parser = TechnologyParser
    summary_type = 'full'

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'images',
                'classification', 'technical_drawing', 'establishment_costs',
                'natural_environment', 'human_environment', 'impacts',
                'cost_benefit', 'climate_change', 'adoption_adaptation',
                'conclusion', 'references']

    def header_image(self):
        data = super().header_image()
        if self.raw_data_getter('header_image_sustainability') == _('Yes'):
            data['partials']['note'] = _(
                'This technology is problematic with regard to land '
                'degradation, so it cannot be declared a sustainable land '
                'management technology')
        return data

    def location(self):
        year = self.raw_data_getter('location_implementation_year')
        decade = self.string_from_list('location_implementation_decade')
        spread = self.string_from_list('location_spread')
        spread_area = self.string_from_list('location_spread_area')
        if spread_area:
            spread = f'{spread} ({_("approx.")} {spread_area})'

        return {
            'template_name': 'summary/block/location.html',
            'title': _('Location'),
            'partials': {
                'description': {
                'title': _('Description'),
                    'lead': self.raw_data_getter('definition'),
                    'text': self.raw_data_getter('description')
                },
                'map': {
                    'url': self.get_thumbnail_url(
                        image=self.raw_data.get('location_map_data', {}).get('img_url'),
                        option_key='map'
                    )
                },
                'infos': {
                    'location': {
                        'title': _('Location'),
                        'text': ', '.join(self.get_location_values(
                            'location_further', 'location_state_province', 'country')
                        )
                    },
                    'sites': {
                        'title': _('No. of Technology sites analysed'),
                        'text': self.string_from_list('location_sites_considered')
                    },
                    'geo_reference_title': _('Geo-reference of selected sites'),
                    'geo_reference': self.raw_data.get(
                        'location_map_data', {}
                    ).get('coordinates') or [self.n_a],
                    'spread': {
                        'title': _('Spread of the Technology'),
                        'text': spread
                    },
                    'date': {
                        'title': _('Date of implementation'),
                        'text': '{year}{decade}'.format(
                            year=year,
                            decade='; {}'.format(decade) if year and decade else decade
                        )
                    },
                    'introduction': {
                        'title': _('Type of introduction'),
                        'items': self.get_list_values_with_other(
                            'location_who_implemented',
                            'location_who_implemented_other'
                        )
                    }
                }
            }
        }

    def classification(self):
        try:
            slm_group = self.raw_data_getter(
                'classification_slm_group', value=''
            )[0].get('values')
            # structure as required for an unordered list.
            slm_group = [{'text': text} for text in slm_group]
        except (KeyError, IndexError):
            slm_group = [{'text': self.n_a}]

        slm_group_other = self.raw_data_getter('classification_slm_group_other')
        if slm_group_other:
            slm_group.append({'text': slm_group_other})

        # append various 'other' fields
        purpose = list(self.raw_data.get('classification_main_purpose'))
        purpose_other = self.raw_data_getter('classification_main_purpose_other')
        if purpose_other:
            purpose.append({'highlighted': True, 'text': purpose_other})
        water_supply = list(self.raw_data.get('classification_watersupply'))
        water_supply_other = self.raw_data_getter('classification_watersupply_other')
        if water_supply_other:
            water_supply.append({'highlighted': True, 'text': water_supply_other})

        return {
            'template_name': 'summary/block/classification.html',
            'title': _('Classification of the Technology'),
            'partials': {
                'main_purpose': {
                    'title': _('Main purpose'),
                    'partials': purpose
                },
                'landuse': {
                    'title': _('Land use'),
                    'partials': self.raw_data.get('classification_landuse')
                },
                'water_supply': {
                    'title': _('Water supply'),
                    'partials': {
                        'list': water_supply,
                        'text': [
                            {
                                'title': _('Number of growing seasons per year'),
                                'text': self.string_from_list('classification_growing_seasons') or self.n_a
                            },
                            {
                                'title': _('Land use before implementation of the Technology'),
                                'text': self.raw_data_getter('classification_lu_before') or self.n_a
                            },
                            {
                                'title': _('Livestock density'),
                                'text': self.raw_data_getter('classification_livestock') or self.n_a
                            }
                        ]
                    }
                },
                'purpose': {
                    'title': _('Purpose related to land degradation'),
                    'partials': self.raw_data.get('classification_purpose')
                },
                'degredation': {
                    'title': _('Degradation addressed'),
                    'partials': self.raw_data.get('classification_degradation')
                },
                'slm_group': {
                    'title': _('SLM group'),
                    'partials': slm_group
                },
                'measures': {
                    'title': _('SLM measures'),
                    'partials': self.raw_data.get('classification_measures') or self.n_a
                }
            }
        }

    def technical_drawing(self):
        drawing_files = self.raw_data.get('tech_drawing_image', [])
        drawing_authors = self.raw_data.get('tech_drawing_author', [])
        main_drawing = {}
        additional_drawings = []

        for index, file in enumerate(drawing_files):
            preview = file.get('preview_image')
            if preview:
                try:
                    author = drawing_authors[index]['value']
                except (KeyError, IndexError):
                    author = ''

                author_title = _('Author: {}').format(author) if author else ''

                if index == 0:
                    main_drawing = {
                        'url': self.get_thumbnail_url(preview, 'flow_chart'),
                        'author': author_title
                    }
                else:
                    additional_drawings.append({
                        'url': self.get_thumbnail_url(preview, 'flow_chart_half_height'),
                        'caption': author_title
                    })

        return {
            'template_name': 'summary/block/specifications.html',
            'title': _('Technical drawing'),
            'partials': {
                'title': _('Technical specifications'),
                'text': self.raw_data_getter('tech_drawing_text'),
                'main_drawing': main_drawing,
                'images': additional_drawings
            }
        }

    def establishment_costs(self):
        base = self.string_from_list('establishment_cost_calculation_base')

        perarea_size = self.raw_data_getter('establishment_perarea_size')
        perarea_conversion = self.raw_data_getter('establishment_perarea_unit_conversion')

        perunit_unit = self.raw_data_getter('establishment_perunit_unit')
        perunit_volume = self.raw_data_getter('establishment_perunit_volume')

        # chose explanation text according to selected calculation type.
        extra = ''
        if perarea_size:
            conversion_text = _('; conversion factor to one hectare: <b>1 ha = {}</b>').format(perarea_conversion)
            extra = _(' (size and area unit: <b>{}</b>{})').format(
                perarea_size,
                conversion_text if perarea_conversion else ''
            )
        if perunit_unit:
            perunit_text = _('unit: <b>{}</b>').format(perunit_unit)
            extra = ' ({}{})'.format(
                perunit_text,
                ' volume, length: <b>{}</b>'.format(perunit_volume) if perunit_volume else ''
            )

        title_addendum = ''
        if perarea_size or perunit_unit:
            title_addendum = ' (per {})'.format(perarea_size or perunit_unit)

        calculation = '{base}{extra}'.format(
            base=base,
            extra=extra
        )
        usd = self.string_from_list('establishment_dollar')
        national_currency = self.raw_data_getter('establishment_national_currency')
        currency = usd or national_currency or self.n_a
        wage = self.raw_data_getter('establishment_average_wage') or _('n.a')
        exchange_rate = self.raw_data_getter('establishment_exchange_rate') or _('n.a')

        return {
            'template_name': 'summary/block/establishment_and_maintenance.html',
            'title': _('Establishment and maintenance: activities, inputs and costs'),
            'partials': {
                'introduction': {
                    'title': _('Calculation of inputs and costs'),
                    'items': [
                        _('Costs are calculated: {}').format(calculation),
                        _('Currency used for cost calculation: <b>{}</b>').format(currency),
                        _('Exchange rate (to USD): 1 USD = {} {}').format(
                            exchange_rate,
                            national_currency if national_currency else ''
                        ),
                        _('Average wage cost of hired labour per day: {}').format(wage)
                    ],
                    'main_factors': self.raw_data_getter('establishment_determinate_factors') or self.n_a,
                    'main_factors_title': _('Most important factors affecting the costs')
                },
                'establishment': {
                    'title': _('Establishment activities'),
                    'list': list(self._get_establishment_list_items('establishment')),
                    #'comment': self.raw_data_getter('establishment_input_comments'),
                    'table': {
                        'title': _('Establishment inputs and costs{}').format(title_addendum),
                        'total_cost_estimate': self.raw_data_getter(
                            'establishment_total_estimation'
                        ),
                        'total_cost_estimate_title': _(
                            'Total establishment costs (estimation)'
                        ),
                        'unit': perunit_unit,
                        'currency': currency,
                        **self.raw_data.get('establishment_input', {}),
                    }
                },
                'maintenance': {
                    'title': _('Maintenance activities'),
                    'list': list(self._get_establishment_list_items('maintenance')),
                    #'comment': self.raw_data_getter('establishment_maintenance_comments'),
                    'table': {
                        'title': _('Maintenance inputs and costs{}').format(title_addendum),
                        'total_cost_estimate': self.raw_data_getter(
                            'establishment_maintenance_total_estimation'
                        ),
                        'total_cost_estimate_title': _(
                            'Total maintenance costs (estimation)'
                        ),
                        'unit': perunit_unit,
                        'currency': currency,
                        **self.raw_data.get('maintenance_input', {}),
                    }
                }
            }
        }

    def _get_establishment_list_items(self, content_type: str):
        """
        Combine measure type and timing for identical question groups.
        """
        activity = 'establishment_{}_activities'.format(content_type)
        timing = 'establishment_{}_timing'.format(content_type)
        timing_title = _('Timing/ frequency')
        for index, activity in enumerate(self.raw_data.get(activity, [])):

            try:
                addendum = f' ({timing_title}: {self.raw_data[timing][index]["value"]})'
            except (KeyError, IndexError):
                addendum = ''

            yield {
                'text': '{activity}{addendum}'.format(
                    activity=activity['value'] or '',
                    addendum=addendum
                )}

    def natural_environment(self):
        specifications = ''
        climate_zone_text = self.raw_data_getter('natural_env_climate_zone_text')
        rainfall = self.raw_data_getter('natural_env_rainfall_annual')
        rainfall_specifications = self.raw_data_getter('natural_env_rainfall_specifications')
        meteostation = self.raw_data_getter('natural_env_rainfall_meteostation')

        if rainfall:
            rainfall = _('Average annual rainfall in mm: {}').format(rainfall)
        if meteostation:
            meteostation = _('Name of the meteorological station: {}').format(meteostation)

        for text in [rainfall, rainfall_specifications, meteostation, climate_zone_text]:
            if text:
                specifications += text + '\n'

        return {
            'template_name': 'summary/block/natural_environment.html',
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
                    'text': specifications or self.n_a
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
            'template_name': 'summary/block/human_environment.html',
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
                    'items': self.get_list_values_with_other(
                        'human_env_sedentary_nomadic',
                        'human_env_sedentary_nomadic_other'
                    )
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
                    'items': self.get_list_values_with_other(
                        'human_env_ownership',
                        'human_env_ownership_other'
                    )
                },
                'land_rights': {
                    'title': _('Land use rights'),
                    'items': self.get_list_values_with_other(
                        'human_env_landuser_rights',
                        'human_env_landuser_rights_other'
                    )
                },
                'water_rights': {
                    'title': _('Water use rights'),
                    'items': self.get_list_values_with_other(
                        'human_env_wateruser_rights',
                        'human_env_wateruser_rights_other'
                    )
                },
                'access': {
                    'title': _('Access to services and infrastructure'),
                    'items': self.raw_data.get('human_env_services')
                }
            }
        }

    def impacts(self):
        return {
            'template_name': 'summary/block/impacts.html',
            'title': _('Impacts'),
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
                }
            }
        }

    def cost_benefit(self):
        return {
            'template_name': 'summary/block/cost_benefit_analysis.html',
            'title': _('Cost-benefit analysis'),
            'partials': {
                'establishment': {
                    'title': _('Benefits compared with establishment costs'),
                    'items': self.raw_data.get(
                        'impacts_establishment_costbenefit')
                },
                'maintenance': {
                    'title': _('Benefits compared with maintenance costs'),
                    'items': self.raw_data.get(
                        'impacts_maintenance_costbenefit')
                },
                'comment': self.raw_data_getter('tech_costbenefit_comment')
            }
        }

    def climate_change(self):
        return {
            'template_name': 'summary/block/climate_change.html',
            'title': _('Climate change'),
            'labels': {
                'left': _('Climate change/ extreme to which the Technology is exposed'),
                'right': _('How the Technology copes with these changes/extremes')
            },
            'partials': self.raw_data.get('climate_change'),
        }
    
    def adoption_adaptation(self):
        return {
            'template_name': 'summary/block/adoption_adaptation.html',
            'title': _('Adoption and adaptation'),
            'partials': {
                'adopted': {
                    'title': _('Percentage of land users in the area who have adopted the Technology'),
                    'items': self.raw_data.get('adoption_percentage')
                },
                'adopted_no_incentive': {
                    'title': _('Of all those who have adopted the Technology, how many have done so without receiving material incentives?'),
                    'items': self.raw_data.get('adoption_spontaneously')
                },
                'quantify': {
                    'title': _('Number of households and/ or area covered'),
                    'text': self.raw_data_getter('adoption_quantify')
                },
                'adaptation': {
                    'title': _('Has the Technology been modified recently to adapt to changing conditions?'),
                    'items': self.raw_data.get('adoption_modified')
                },
                'condition': {
                    'title': _('To which changing conditions?'),
                    'items': self.get_list_values_with_other(
                        'adoption_condition',
                        'adoption_condition_other'
                    )
                },
                'comments': self.raw_data_getter('adoption_comments')
            }
        }


class Technology2018FullSummaryRenderer(TechnologyFullSummaryRenderer):

    parser = Technology2018Parser

    def technical_drawing(self):
        # No more separate repeating drawing-questiongroup and single
        # specifications text questiongroup. Instead, repeating questiongroups
        # with drawing and specifications together.
        drawing_files = self.raw_data.get('tech_drawing_image', [])
        drawing_authors = self.raw_data.get('tech_drawing_author', [])
        drawing_texts = self.raw_data.get('tech_drawing_text', [])

        drawings = []

        for index, file in enumerate(drawing_files):
            preview = file.get('preview_image')
            if preview:
                try:
                    author = drawing_authors[index]['value']
                except (KeyError, IndexError):
                    author = ''

                try:
                    text = drawing_texts[index]['value']
                except (KeyError, IndexError):
                    text = ''

                author_title = f"{_('Author:')} {author}" if author else ''

                drawings.append({
                    'url': self.get_thumbnail_url(preview, 'flow_chart'),
                    'author': author_title,
                    'text': text,
                })

        return {
            'template_name': 'summary/tech_2018/block/specifications.html',
            'title': _('Technical drawing'),
            'partials': {
                'title': _('Technical specifications'),
                'drawings': drawings,
            }
        }

    def get_reference_resource_persons(self):
        """
        Resource persons is either a dictionary with only one element or a list
        which always contains a type and either a user-id or a first/last name.
        The order of type and name correlates, so starting from the type the
        users details are appended.

        Changes in edition 2018: e-mail was removed.
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
        person_types_other = self.raw_data_getter(
            'references_person_type_other', value=''
        )

        for index, person in enumerate(resoureperson_types):
            if person_user_id[index] and isinstance(person_user_id[index], dict):
                name = person_user_id[index].get('value')
            elif len(person_firstnames) >= index and len(person_lastnames) >= index:
                name = '{first_name} {last_name}'.format(
                    first_name=person_firstnames[index].get('value') or '',
                    last_name=person_lastnames[index].get('value') or ''
                )
            else:
                continue

            if person.get('values'):
                person_type = ', '.join(person.get('values', []))
            else:
                person_type = person_types_other[index].get('value', '')

            yield {'text': '{name} - {type}'.format(
                name=name,
                type=person_type)}

    def location(self):
        location_data = super().location()

        # Use new template
        location_data['template_name'] = 'summary/tech_2018/block/location.html'

        # New question about precise area was added. Use this value if
        # available, else the approximate range (as before).
        spread_area_precise = self.raw_data_getter(
            'location_spread_area_precise')
        if spread_area_precise:
            spread = self.string_from_list('location_spread')
            location_data['partials']['infos']['spread']['text'] = \
                f'{spread} ({spread_area_precise} {_("km²")})'

        # New question about location in permanently protected area was added.
        protected_area = self.raw_data_getter('location_protected_area')
        protected_area_specify = self.raw_data_getter('location_protected_area_specify')
        if protected_area_specify:
            protected_area = f'{protected_area}: {protected_area_specify}'
        location_data['partials']['infos']['protected_area'] = {
            'title': _('In a permanently protected area?'),
            'text': protected_area,
        }

        return location_data

    def classification(self):
        classification_data = super().classification()

        # Use new template
        classification_data['template_name'] = 'summary/tech_2018/block/classification.html'

        # Current land use: Add new question about mixed land use
        classification_data['partials']['landuse'] = {
            'title': _('Current land use'),
            'partials': {
                'landuse': {
                    'list': self.raw_data.get('classification_landuse'),
                },
                'mixed': {
                    'text': 'Foo',
                }
            },
        }

        # Add new section about initial land use
        classification_data['partials']['landuse_initial'] = {
            'title': _('Initial land use'),
            'partials': {}
        }

        # Remove questions about growing seasons (moved), initial land use
        # (moved) and livestock density (deleted).
        del classification_data['partials']['water_supply']['partials']['text']

        return classification_data


class ApproachesFullSummaryRenderer(GlobalValuesMixin, SummaryRenderer):
    """
    Configuration for 'full' approaches summary.
    """
    summary_type = 'full'
    parser = ApproachParser

    @property
    def content(self):
        return ['header_image', 'title', 'location', 'images',
                'aims', 'participation', 'technical_support', 'financing',
                'impacts', 'conclusion', 'references']

    def location(self):
        return {
            'template_name': 'summary/block/location_approach.html',
            'title': _('Location'),
            'partials': {
                'description': {
                    'title': _('Description'),
                    'lead': self.raw_data_getter('definition'),
                    'text': self.raw_data_getter('description')
                },
                'map': {
                    'url': self.get_thumbnail_url(
                        image=self.raw_data.get('location_map_data', {}).get('img_url'),
                        option_key='map'
                    )
                },
                'infos': {
                    'location': {
                        'title': _('Location'),
                        'text': ', '.join(self.get_location_values(
                            'location_further', 'location_state_province', 'country'
                        ))
                    },
                    'geo_reference_title': _('Geo-reference of selected sites'),
                    'geo_reference': self.raw_data.get(
                        'location_map_data', {}
                    ).get('coordinates') or [self.n_a],
                    'start_date': {
                        'title': _('Initiation date'),
                        'text': self.raw_data_getter(
                            'location_initiation_year') or self.n_a
                    },
                    'end_date': {
                        'title': _('Year of termination'),
                        'text': self.raw_data_getter(
                            'location_termination_year') or self.n_a
                    },
                    'introduction': {
                        'title': _('Type of Approach'),
                        'items': self.get_list_values_with_other(
                            'location_type',
                            'location_type_other'
                        )
                    }
                }
            }
        }

    def aims(self):
        return {
            'template_name': 'summary/block/aims.html',
            'title': _('Approach aims and enabling environment'),
            'partials': {
                'main': {
                    'title': _('Main aims / objectives of the approach'),
                    'text': self.raw_data_getter('aims_main') or self.n_a
                },
                'elements': [
                    {
                        'title': _('Conditions enabling the implementation of the Technology/ ies applied under the Approach'),
                        'items': self.raw_data.get('aims_enabling') or self.n_a
                    },
                    {
                        'title': _('Conditions hindering the implementation of the Technology/ ies applied under the Approach'),
                        'items': self.raw_data.get('aims_hindering') or self.n_a
                    }
                ]
            }
        }

    def participation(self):
        lead_agency = self.raw_data_getter('participation_lead_agency')
        author = self.raw_data_getter('participation_flowchart_author')
        flowchart_preview = ''
        flowchart_data = self.raw_data.get('participation_flowchart_file', [])
        if len(flowchart_data) >= 1:
            flowchart_preview = flowchart_data[0].get('preview_image', '')
        return {
            'template_name': 'summary/block/participation.html',
            'title': _('Participation and roles of stakeholders involved'),
            'partials': {
                'stakeholders': {
                    'title': _('Stakeholders involved in the Approach and their roles'),
                    'items': list(self.raw_data.get('participation_stakeholders')),
                    'addendum': {
                        'title': _('Lead agency'),
                        'text': lead_agency
                    }
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
                    'url': self.get_thumbnail_url(
                        image=flowchart_preview,
                        option_key='flow_chart'
                    ),
                    'author': _('Author: {}').format(author) if author else '',
                    'title': _('Flow chart'),
                    'text': self.raw_data_getter('participation_flowchart_text')
                },
                'decision_making': {
                    'title': _('Decision-making on the selection of SLM Technology'),
                    'elements': [
                        {
                            'title': _('Decisions were taken by'),
                            'items': self.get_list_values_with_other(
                                'participation_decisions_by',
                                'participation_decisions_by_other'
                            )
                        },
                        {
                            'title': _('Decisions were made based on'),
                            'items': self.get_list_values_with_other(
                                'participation_decisions_based',
                                'participation_decisions_based_other'
                            )
                        }
                    ]
                }
            }
        }

    def technical_support(self):
        return {
            'template_name': 'summary/block/technical_support.html',
            'title': _('Technical support, capacity building, and knowledge management'),
            'partials': {
                'activities': {
                    'title': _('The following activities or services have been part of the approach'),
                    'items': [
                        self.raw_data.get('tech_support_training_is_training'),
                        self.raw_data.get('tech_support_advisory_is_advisory'),
                        self.raw_data.get('tech_support_institutions_is_institution', {}).get('bool'),
                        self.raw_data.get('tech_support_monitoring_is_monitoring'),
                        self.raw_data.get('tech_support_research_is_research')
                    ]
                },
                'training': {
                    'title': _('Capacity building/ training'),
                    'elements': [
                        {
                            'title': _('Training was provided to the following stakeholders'),
                            'items': self.get_list_values_with_other(
                                'tech_support_training_who',
                                'tech_support_training_who_other'
                            )
                        },
                        {
                            'title': _('Form of training'),
                            'items': self.get_list_values_with_other(
                                'tech_support_training_form',
                                'tech_support_training_form_other'
                            )
                        }
                    ],
                    'list': {
                        'title': _('Subjects covered'),
                        'text': self.raw_data_getter('tech_support_training_subjects')
                    }
                },
                'advisory': {
                    'title': _('Advisory service'),
                    'elements': [
                        {
                            'title': _('Advisory service was provided'),
                            'items': self.get_list_values_with_other(
                                'tech_support_advisory_service',
                                'tech_support_advisory_service_other',
                            ),
                            'description': self.raw_data_getter('tech_support_advisory_description')
                        }
                    ]
                },
                'institution_strengthening': {
                    'title': _('Institution strengthening'),
                    'subtitle': {
                        'title': _('Institutions have been strengthened / established'),
                        'value': self.raw_data.get('tech_support_institutions_is_institution', {}).get('value'),
                    },
                    'level': {
                        'title': _('at the following level'),
                        'items': self.get_list_values_with_other(
                            'tech_support_institutions_level',
                            'tech_support_institutions_level_other'
                        ),
                        'description': self.raw_data_getter('tech_support_institutions_describe'),
                        'comment_title': _('Describe institution, roles and responsibilities, members, etc.'),
                    },
                    'support_type': {
                        'title': _('Type of support'),
                        'items': self.get_list_values_with_other(
                            'tech_support_institutions_support',
                            'tech_support_institutions_support_other'
                        ),
                        'description': self.raw_data_getter('tech_support_institutions_support_specify'),
                        'comment_title': _('Further details')
                    }
                },
                'monitoring': {
                    'title': _('Monitoring and evaluation'),
                    'comment': self.raw_data_getter('tech_support_monitoring_comment'),
                },
                'research': {
                    'title': _('Research'),
                    'subtitle': _('Research treated the following topics'),
                    'items': self.get_list_values_with_other(
                        'tech_support_research_topics',
                        'tech_support_research_topics_other'
                    ),
                    'description': self.raw_data_getter('tech_support_research_details')
                }
            }
        }

    def financing(self):
        return {
            'template_name': 'summary/block/financing.html',
            'title': _('Financing and external material support'),
            'partials': {
                'budget': {
                    'title': _('Annual budget in USD for the SLM component'),
                    'items': self.raw_data.get('financing_budget'),
                    'description': self.raw_data_getter('financing_budget_comments'),
                    'addendum': _('Precise annual budget: {}'.format(self.raw_data_getter('financing_budget_precise') or self.n_a))
                },
                'services': {
                    'title': _('The following services or incentives have been provided to land users'),
                    'items': [
                        self.raw_data.get('financing_is_financing'),
                        self.raw_data.get('financing_subsidies', {}).get('is_subsidised'),
                        self.raw_data.get('financing_is_credit'),
                        self.raw_data.get('financing_is_other'),
                    ]
                },
                'subsidies': {
                    **self.raw_data.get('financing_subsidies', {}).get('subsidies'),
                    'labour': {
                        'title': _('Labour by land users was'),
                        'items': self.raw_data.get('financing_labour')
                    },
                    'material_support': {
                        'title': _('Financial/ material support provided to land users'),
                        'text': self.raw_data_getter('financing_material_support'),
                    },
                    'credit': {
                        'title': _('Credit'),
                        'items': [
                            _('Conditions: {}').format(self.raw_data_getter(
                                'financing_credit_conditions') or self.n_a
                            ),
                            _('Credit providers: {}').format(self.raw_data_getter(
                                'financing_credit_provider') or self.n_a
                            ),
                            _('Credit receivers: {}').format(self.raw_data_getter(
                                'financing_credit_receiver') or self.n_a
                            )
                        ]
                    },
                    'other': {
                        'title': _('Other incentives or instruments'),
                        'text': self.raw_data_getter('financing_other_text') or self.n_a
                    }
                }
            }
        }

    def impacts(self):
        return {
            'template_name': 'summary/block/impacts_approach.html',
            'title': _('Impact analysis and concluding statements'),
            'partials': {
                'impacts': {
                    'title': _('Impacts of the Approach'),
                    'subtitle': _('Did the approach...'),
                    'items': self.raw_data.get('impacts_impacts'),
                },
                'motivation': {
                    'title': _('Main motivation of land users to implement SLM'),
                    'items': self.get_list_values_with_other(
                        'impacts_motivation',
                        'impacts_motivation_other'
                    ) or [{'text': self.n_a, 'highlighted': True}]
                },
                'sustainability': {
                    'title': _('Sustainability of Approach activities'),
                    'subtitle': _('Can the land users sustain what hat been implemented through the Approach (without external support)?'),
                    'items': self.raw_data.get('impacts_sustainability'),
                    'comment': self.raw_data_getter('impacts_sustainability_comments')
                }
            }
        }
