from model_mommy import mommy

from qcat.tests import TestCase
from questionnaire.models import Questionnaire


class QuestionnaireLookupsTest(TestCase):

    def setUp(self):
        self.bread = mommy.make(
            Questionnaire,
            data={"qg_name": [
                {"name": {"en": "BREAD", "fr": "baguette"},
                 "local_name": {"en": "loaf", "fr": "mini"}}]
            }
        )
        self.peas = mommy.make(
            Questionnaire,
            data={"qg_name": [
                {"name": {"en": "peas", "it": "pisello"},
                 "local_name": {"en": "mini beans"}}]
            }
        )

    def test_qs_name_lookup_name_en(self):
        qs = Questionnaire.objects.filter(data__qs_name='bread')
        self.assertEquals(qs.first(), self.bread)
        self.assertEquals(qs.count(), 1)

    def test_qs_name_lookup_name_fr(self):
        qs = Questionnaire.objects.filter(data__qs_name='baguette')
        self.assertEquals(qs.first(), self.bread)
        self.assertEquals(qs.count(), 1)

    def test_qs_name_lookup_local_name_en(self):
        qs = Questionnaire.objects.filter(data__qs_name='loaf')
        self.assertEquals(qs.first(), self.bread)
        self.assertEquals(qs.count(), 1)

    def test_qs_name_lookup_many(self):
        qs = Questionnaire.objects.filter(data__qs_name='mini')
        self.assertEquals(qs.count(), 2)
