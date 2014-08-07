import json
from django.contrib.gis.db import models
from django_pgjson.fields import JsonBField


class Document(models.Model):
    json = JsonBField()
    created = models.DateTimeField(auto_now=True)

    def __str__(self):
        return json.dumps(self.json)
