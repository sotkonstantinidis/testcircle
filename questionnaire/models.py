import json
from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django_pgjson.fields import JsonBField
from uuidfield import UUIDField


class Questionnaire(models.Model):
    """
    The model representing a Questionnaire instance. This is the common
    denominator for all version (:class:`QuestionnaireVersion`) of a
    Questionnaire.
    """
    data = JsonBField()
    created = models.DateTimeField(auto_now=True)
    uuid = UUIDField(auto=True)
    blocked = models.BooleanField(default=False)
    active = models.ForeignKey(
        'QuestionnaireVersion', related_name='active_questionnaire', null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='QuestionnaireMembership')
    configurations = models.ManyToManyField('configuration.Configuration')

    def get_absolute_url(self):
        return reverse('questionnaire_view', args=[self.id])

    @staticmethod
    def create_new(data):
        questionnaire = Questionnaire.objects.create(data=data)
        return questionnaire

    def __str__(self):
        return json.dumps(self.data)


class QuestionnaireVersion(models.Model):
    """
    The model representing a version of a :class:`Questionnaire`. For a
    single Questionnaire, multiple versions can exist.
    """
    data = JsonBField()
    created = models.DateTimeField(auto_now=True)
    version = models.IntegerField()
    questionnaire = models.ForeignKey('Questionnaire')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    status = models.ForeignKey('Status')


class Status(models.Model):
    """
    The model representing the status of a
    :class:`QuestionnaireVersion`. The status is based on the review
    process and defines which versions are visible to the public.
    """
    keyword = models.CharField(max_length=63, unique=True)
    description = models.TextField(null=True)


class QuestionnaireMembership(models.Model):
    """
    The model representing the membership of a :class:`User` in a
    :class`Questionnaire` and his roles (:class:`QuestionnaireRole`).
    """
    questionnaire = models.ForeignKey('Questionnaire')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    role = models.ForeignKey('QuestionnaireRole')


class QuestionnaireRole(models.Model):
    """
    The model representing the roles of a user in a
    :class:`QuestionnaireMembership` which reflects the permissions he
    has when it comes to editing a :class:`Questionnaire`.
    """
    keyword = models.CharField(max_length=63, unique=True)
    description = models.TextField(null=True)
