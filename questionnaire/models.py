import json
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django_pgjson.fields import JsonBField


class Questionnaire(models.Model):
    json = JsonBField()
    created = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('questionnaire_view', args=[self.id])

    @staticmethod
    def create_new(json):
        questionnaire = Questionnaire.objects.create(json=json)
        return questionnaire

    def __str__(self):
        return json.dumps(self.json)
