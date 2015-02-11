import json
import uuid
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django_pgjson.fields import JsonBField
from configuration.models import Configuration


class Questionnaire(models.Model):
    """
    The model representing a Questionnaire instance. This is the common
    denominator for all version (:class:`QuestionnaireVersion`) of a
    Questionnaire.
    """
    data = JsonBField()
    created = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=64, default=uuid.uuid4)
    blocked = models.BooleanField(default=False)
    active = models.ForeignKey(
        'QuestionnaireVersion', related_name='active_questionnaire', null=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='QuestionnaireMembership')
    configurations = models.ManyToManyField('configuration.Configuration')

    def get_absolute_url(self):
        return reverse('questionnaire_view_details', args=[self.id])

    @staticmethod
    def create_new(configuration_code, data):
        """
        Create and return a new Questionnaire.

        Args:
            ``configuration_code`` (str): The code of the configuration.
            An active configuration with the given code needs to exist.
            The configuration is linked to the questionnaire.

            ``data`` (dict): The questionnaire data.

        Returns:
            ``questionnaire.models.Questionnaire``. The created
            Questionnaire.

        Raises:
            ``ValidationError``
        """
        configuration = Configuration.get_active_by_code(configuration_code)
        if configuration is None:
            raise ValidationError(
                'No active configuration found for code "{}"'.format(
                    configuration_code))
        questionnaire = Questionnaire.objects.create(data=data)
        questionnaire.configurations.add(configuration)
        return questionnaire

    def get_id(self):
        return self.id

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

    class Meta:
        verbose_name_plural = 'statuses'


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
