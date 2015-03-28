import json
from uuid import uuid4
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
    uuid = models.CharField(max_length=64, default=uuid4)
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


class QuestionnaireTranslation(models.Model):
    """
    Represents a many-to-many relationship between Questionnaires and
    languages with additional fields. Each translation of a
    Questionnaire gets an entry to allow a quick overview in which
    languages a Questionnaire is available. Additional fields mark the
    language in which the Questionnaire was originally entered.
    """
    questionnaire = models.ForeignKey('Questionnaire')
    language = models.CharField(max_length=63, choices=settings.LANGUAGES)
    original_language = models.BooleanField(default=False)


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


class File(models.Model):
    """
    The model representing a file uploaded by a user.

    Please note that the file itself is not stored in the database, this
    model just contains the filenames of all of its thumbnails and some
    meta information (size, file type).
    """
    uuid = models.CharField(max_length=64)
    uploaded = models.DateTimeField(auto_now=True)
    content_type = models.CharField(max_length=64)
    size = models.BigIntegerField(null=True)
    thumbnails = JsonBField()

    @staticmethod
    def create_new(content_type, size=None, thumbnails={}, uuid=None):
        """
        Create and return a new file.

        Args:
            ``content_type`` (str): The mime type (e.g. ``image/png``) of
            the file.

        Kwargs:
            ``size`` (int): The size of the file.

            ``thumbnails`` (dict): A dictionary pointing to the
            thumbnails based on their predefined dimensions. Example::

              {
                "header_big": "e0791bc0-e05d-4a03-8ab9-f5f9c2615cac",
                "header_small": "23592f37-cd5b-43db-9376-04c5d805429d"
              }

            ``uuid`` (str): The UUID for the file. If not provided, a
            random UUID will be generated.

        Returns:
            ``questionnaire.models.File``. The created File model.
        """
        if uuid is None:
            uuid = uuid4()
        return File.objects.create(
            uuid=uuid, content_type=content_type, size=size,
            thumbnails=thumbnails)

    def get_url(self, thumbnail=None):
        """
        Return the URL of a file object. If thumbnail is provided,
        return the respective URL.

        Args:
            ``thumbnail`` (str or None). The name of the thumbnail for
            which the URL shall be returned. If not specified, the
            original file will be returned.

        Returns:
            ``str`` or ``None``. The relative URL of the file object or
            ``None`` if the thumbnail was not found.
        """
        from questionnaire.upload import (
            get_url_by_filename,
            get_file_extension_by_content_type,
        )
        uid = self.uuid
        if thumbnail is not None:
            uid = self.thumbnails.get(thumbnail)
            if uid is None:
                return None
        if thumbnail is not None:
            file_extension = 'jpg'
        else:
            file_extension = get_file_extension_by_content_type(
                self.content_type)
        if file_extension is None:
            return None
        filename = '{}.{}'.format(uid, file_extension)
        return get_url_by_filename(filename)

    def get_interchange_urls(self):
        """
        Return the URLs for all the thumbnail sizes of the file. This
        value can be used by foundation as the ``data-interchange``
        value to allow interchange of images.

        Also adds ``large`` as last thumbnail size. This size contains
        the original image as it was uploaded.

        Returns:
            ``str``. A string with the interchange files. Can be used as
            such in ``<img data-interchange="">``.
        """
        ret = []
        for thumbnail_format in settings.UPLOAD_IMAGE_THUMBNAIL_FORMATS:
            ret.append('[{}, ({})]'.format(self.get_url(
                thumbnail=thumbnail_format[0]), thumbnail_format[0]))
        ret.append('[{}, ({})]'.format(self.get_url(), 'large'))
        return ''.join(ret)
