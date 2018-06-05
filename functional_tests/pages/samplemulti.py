from selenium.webdriver.common.by import By

from functional_tests.pages.base import QcatPage
from functional_tests.pages.mixins import EditMixin
from functional_tests.pages.questionnaire import QuestionnaireStepPage


class Samplemulti2015Mixin:
    CATEGORIES = [
        ('mcat_1', 'MCategory 1'),
    ]


class SamplemultiNewPage(Samplemulti2015Mixin, EditMixin, QcatPage):
    route_name = 'samplemulti:questionnaire_new'


class SamplemultiStepPage(QuestionnaireStepPage):
    LOC_QUESTION_MQG01_MKEY01 = (By.NAME, 'mqg_01-0-original_mkey_01')
