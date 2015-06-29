import json
from uuid import uuid4
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django_pgjson.fields import JsonBField

from configuration.models import Configuration
from search.index import put_questionnaire_data


STATUSES = (
    (1, _('Draft')),
    (2, _('Pending')),
    (3, _('Approved')),
    (4, _('Rejected')),
)


class Questionnaire(models.Model):
    """
    The model representing a Questionnaire instance. This is the common
    denominator for all version (:class:`QuestionnaireVersion`) of a
    Questionnaire.
    """
    data = JsonBField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    uuid = models.CharField(max_length=64, default=uuid4)
    blocked = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUSES)
    version = models.IntegerField()
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='QuestionnaireMembership')
    configurations = models.ManyToManyField('configuration.Configuration')
    links = models.ManyToManyField(
        'self', through='QuestionnaireLink', symmetrical=False,
        related_name='linked_to+', null=True)

    class Meta:
        ordering = ['-updated']

    def get_absolute_url(self):
        return reverse('questionnaire_view_details', args=[self.id])

    @staticmethod
    def create_new(
            configuration_code, data, previous_version=None, status=1):
        """
        Create and return a new Questionnaire.

        Args:
            ``configuration_code`` (str): The code of the configuration.
            An active configuration with the given code needs to exist.
            The configuration is linked to the questionnaire.

            ``data`` (dict): The questionnaire data.

        Kwargs:
            ``previous_version`` (questionnaire.models.Questionnaire):
            The previous version of the questionnaire.

            ``status`` (int): The status of the questionnaire to be
            created. Defaults to 1 (draft) if not set.

        Returns:
            ``questionnaire.models.Questionnaire``. The created
            Questionnaire.

        Raises:
            ``ValidationError``
        """
        if previous_version:
            # TODO. Calculate version and use same UUID as previous version.
            raise NotImplemented()
        else:
            version = 1
        if status not in [s[0] for s in STATUSES]:
            raise ValidationError('"{}" is not a valid status'.format(status))
        configuration = Configuration.get_active_by_code(configuration_code)
        if configuration is None:
            raise ValidationError(
                'No active configuration found for code "{}"'.format(
                    configuration_code))
        questionnaire = Questionnaire.objects.create(
            data=data, version=version, status=status)
        questionnaire.configurations.add(configuration)

        # TODO: This should happen on review!
        added, errors = put_questionnaire_data(
            configuration_code, [questionnaire])

        return questionnaire

    def get_id(self):
        return self.id

    def get_metadata(self):
        """
        Return some metadata about the Questionnaire.

        Returns:
            ``dict``. A dict containing the following metadata:

            * ``created``

            * ``updated``
        """
        return {
            'created': self.created,
            'updated': self.updated,
        }

    def add_link(self, questionnaire, symm=True):
        """
        Add a link to another Questionnaire. This actually creates two
        entries in the link table to make the reference symmetrical.

        https://charlesleifer.com/blog/self-referencing-many-many-through/

        Args:
            ``questionnaire`` (questionnaire.models.Questionnaire): The
            questionnaire to link to.

        Kwargs:
            ``symm`` (bool): Whether or not to add the symmetrical link
            (to avoid recursion).

        Returns:
            ``questionnaire.models.Questionnaire``. The updated
            questionnaire.
        """
        link, created = QuestionnaireLink.objects.get_or_create(
            from_questionnaire=self,
            from_status=self.status,
            to_questionnaire=questionnaire,
            to_status=questionnaire.status)
        if symm:
            # avoid recursion by passing `symm=False`
            questionnaire.add_link(self, symm=False)
        return questionnaire

    def remove_link(self, questionnaire, symm=True):
        """
        Remove a link to another Questionnaire. This actually removes
        both links (also the symmetrical one).

        https://charlesleifer.com/blog/self-referencing-many-many-through/

        Args:
            ``questionnaire`` (questionnaire.models.Questionnaire): The
            questionnaire to remove.

        Kwargs:
            ``symm`` (bool): Whether or not to remove the symmetrical
            link (to avoid recursion).
        """
        QuestionnaireLink.objects.filter(
            from_questionnaire=self,
            to_questionnaire=questionnaire).delete()
        if symm:
            # avoid recursion by passing `symm=False`
            questionnaire.remove_link(self, symm=False)

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

    class Meta:
        ordering = ['-original_language']


class QuestionnaireLink(models.Model):
    """

    """
    from_questionnaire = models.ForeignKey(
        'Questionnaire', related_name='from_questionnaire')
    from_status = models.IntegerField(choices=STATUSES)
    to_questionnaire = models.ForeignKey(
        'Questionnaire', related_name='to_questionnaire')
    to_status = models.IntegerField(choices=STATUSES)


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
