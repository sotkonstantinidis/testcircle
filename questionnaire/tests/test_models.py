from django.db.utils import DataError
from django.test import TestCase

from questionnaire.models import Questionnaire


class QuestionnaireModelTest(TestCase):

    def test_requires_data(self):
        questionnaire = Questionnaire()
        with self.assertRaises(DataError):
            questionnaire.full_clean()

    def test_has_primary_key(self):
        questionnaire = Questionnaire(data={})
        self.assertTrue(hasattr(questionnaire, 'id'))

    def test_create_new_returns_new_object(self):
        returned = Questionnaire.create_new(data={'foo': 'bar'})
        new_questionnaire = Questionnaire.objects.get(pk=1)
        self.assertEqual(returned, new_questionnaire)

    def test_create_new_sets_data(self):
        questionnaire = Questionnaire.create_new(data={})
        self.assertEqual(questionnaire.data, {})
