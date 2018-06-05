from functional_tests.pages.base import QcatPage
from functional_tests.pages.mixins import EditMixin


class Technologies2015Mixin:
    CATEGORIES = [
        ('tech__1', 'General information'),
        ('tech__2', 'Description of the SLM Technology'),
        ('tech__3', 'Classification of the SLM Technology'),
        ('tech__4', 'Technical specifications, implementation activities, '
                    'inputs, and costs'),
        ('tech__5', 'Natural and human environment'),
        ('tech__6', 'Impacts and concluding statements'),
        ('tech__7', 'References and links'),
    ]

    CATEGORIES_TRANSLATED = [
        ('tech__1', 'Información general'),
        # Not all categories needed. Used only to check if translation is shown.
    ]


class TechnologiesNewPage(Technologies2015Mixin, EditMixin, QcatPage):
    route_name = 'technologies:questionnaire_new'
