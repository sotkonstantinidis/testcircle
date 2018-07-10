from functional_tests.pages.base import QcatPage
from functional_tests.pages.mixins import EditMixin, DetailMixin, ListMixin


class Sample2015Mixin:
    CATEGORIES = [
        ('cat_0', 'Category 0'),
        ('cat_1', 'Category 1'),
        ('cat_2', 'Category 2'),
        ('cat_3', 'Category 3'),
        ('cat_4', 'Category 4'),
        ('cat_5', 'Category 5'),
    ]


class SampleNewPage(Sample2015Mixin, EditMixin, QcatPage):
    route_name = 'sample:questionnaire_new'


class SampleEditPage(Sample2015Mixin, EditMixin, QcatPage):
    route_name = 'sample:questionnaire_edit'


class SampleDetailPage(Sample2015Mixin, DetailMixin, QcatPage):
    route_name = 'sample:questionnaire_details'


class SampleListPage(ListMixin, QcatPage):
    route_name = 'sample:questionnaire_list'
