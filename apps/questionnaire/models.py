import json
from uuid import uuid4

from django.contrib.gis.db import models
from django.contrib.messages import WARNING, SUCCESS
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.utils.translation import ugettext as _, get_language
from django.utils import timezone
from django_pgjson.fields import JsonBField

from accounts.models import User
from configuration.cache import get_configuration
from configuration.models import Configuration
from .conf import settings
from .errors import QuestionnaireLockedException
from .querysets import StatusQuerySet


STATUSES = (
    (settings.QUESTIONNAIRE_DRAFT, _('Draft')),
    (settings.QUESTIONNAIRE_SUBMITTED, _('Submitted')),
    (settings.QUESTIONNAIRE_REVIEWED, _('Reviewed')),
    (settings.QUESTIONNAIRE_PUBLIC, _('Public')),
    (settings.QUESTIONNAIRE_REJECTED, _('Rejected')),
    (settings.QUESTIONNAIRE_INACTIVE, _('Inactive')),
)
STATUSES_CODES = (
    (settings.QUESTIONNAIRE_DRAFT, 'draft'),
    (settings.QUESTIONNAIRE_SUBMITTED, 'submitted'),
    (settings.QUESTIONNAIRE_REVIEWED, 'reviewed'),
    (settings.QUESTIONNAIRE_PUBLIC, 'public'),
    (settings.QUESTIONNAIRE_REJECTED, 'rejected'),
    (settings.QUESTIONNAIRE_INACTIVE, 'inactive'),
)

QUESTIONNAIRE_ROLES = (
    # Functional roles
    (settings.QUESTIONNAIRE_COMPILER, _('Compiler')),
    (settings.QUESTIONNAIRE_EDITOR, _('Editor')),
    (settings.QUESTIONNAIRE_REVIEWER, _('Reviewer')),
    (settings.QUESTIONNAIRE_PUBLISHER, _('Publisher')),
    # Content roles only, no privileges attached
    (settings.QUESTIONNAIRE_LANDUSER, _('Land User')),
    (settings.QUESTIONNAIRE_RESOURCEPERSON, _('Key resource person')),
)


class Questionnaire(models.Model):
    """
    The model representing a Questionnaire instance. This is the common
    denominator for all version (:class:`QuestionnaireVersion`) of a
    Questionnaire.
    """
    data = JsonBField()
    data_old = JsonBField(null=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    uuid = models.CharField(max_length=64, default=uuid4)
    code = models.CharField(max_length=64, default='')
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        related_name='blocks_questionnaire',
        help_text=_(u"Set with the method: lock_questionnaire.")
    )
    status = models.IntegerField(choices=STATUSES)
    version = models.IntegerField()
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='QuestionnaireMembership')
    configurations = models.ManyToManyField(
        'configuration.Configuration', through='QuestionnaireConfiguration')
    links = models.ManyToManyField(
        'self', through='QuestionnaireLink', symmetrical=False,
        related_name='linked_to+')

    objects = models.Manager()
    with_status = StatusQuerySet.as_manager()

    class Meta:
        ordering = ['-updated']
        permissions = (
            ("review_questionnaire", "Can review questionnaire"),
            ("publish_questionnaire", "Can publish questionnaire"),
        )

    def get_absolute_url(self):
        return reverse(
            'questionnaire_view_details', kwargs={'identifier': self.code})

    def update_data(self, data, updated, configuration_code):
        """
        Helper function to just update the data of the questionnaire
        without creating a new instance.

        Args:
            ``data`` (dict): The data dictionary

            ``updated`` (timestamp): The timestamp of the update

            ``configuration_code`` (str): The configuration code.

        Returns:
            ``Questionnaire``
        """
        self.data = data
        self.updated = updated
        self.blocked = None
        self.save()

        # Update the users attached to the questionnaire
        self.update_users_from_data(configuration_code)

        return self

    @staticmethod
    def create_new(
            configuration_code, data, user, previous_version=None, status=1,
            created=None, updated=None):
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

            ``created`` (datetime): A specific datetime object to be set
            as created timestamp. Defaults to ``now`` if not set.

            ``updated`` (datetime): A specific datetime object to be set
            as updated timestamp. Defaults to ``now`` if not set.

        Returns:
            ``questionnaire.models.Questionnaire``. The created
            Questionnaire.

        Raises:
            ``ValidationError``
        """
        if updated is None:
            updated = timezone.now()
        if created is None:
            created = timezone.now()

        if previous_version:
            created = previous_version.created
            permissions = previous_version.get_permissions(user)
            code = previous_version.code
            version = previous_version.version

            if 'edit_questionnaire' not in permissions:
                raise ValidationError(
                    'You do not have permission to edit the questionnaire.')

            if previous_version.status == settings.QUESTIONNAIRE_PUBLIC:
                # Edit of a public questionnaire: Create new version
                # with the same code
                version = previous_version.version + 1

            elif previous_version.status == settings.QUESTIONNAIRE_DRAFT:
                # Edit of a draft questionnaire: Only update the data
                previous_version.update_data(
                    data, updated, configuration_code)
                return previous_version

            elif previous_version.status == settings.QUESTIONNAIRE_SUBMITTED:
                # Edit of a submitted questionnaire: Only update the data
                # User must be reviewer!
                if 'review_questionnaire' not in permissions:
                    raise ValidationError(
                        'You do not have permission to edit the '
                        'questionnaire.')
                previous_version.update_data(
                    data, updated, configuration_code)
                return previous_version

            elif previous_version.status == settings.QUESTIONNAIRE_REVIEWED:
                # Edit of a reviewed questionnaire: Only update the data
                # User must be publisher!
                if 'publish_questionnaire' not in permissions:
                    raise ValidationError(
                        'You do not have permission to edit the '
                        'questionnaire.')
                previous_version.update_data(
                    data, updated, configuration_code)
                return previous_version

            else:
                raise ValidationError(
                    'The questionnaire cannot be updated because of its status'
                    ' "{}"'.format(previous_version.status))
        else:
            from configuration.utils import create_new_code
            code = create_new_code(configuration_code, data)
            version = 1
        if status not in [s[0] for s in STATUSES]:
            raise ValidationError('"{}" is not a valid status'.format(status))
        configuration = Configuration.get_active_by_code(configuration_code)
        if configuration is None:
            raise ValidationError(
                'No active configuration found for code "{}"'.format(
                    configuration_code))
        questionnaire = Questionnaire.objects.create(
            data=data, code=code, version=version, status=status,
            created=created, updated=updated)

        # TODO: Not all configurations should be the original ones!
        QuestionnaireConfiguration.objects.create(
            questionnaire=questionnaire, configuration=configuration,
            original_configuration=True)

        # TODO: Not all translations should be the original ones!
        QuestionnaireTranslation.objects.create(
            questionnaire=questionnaire, language=get_language(),
            original_language=True)

        if previous_version:
            # Copy all the functional user roles from the old version
            user_roles = [settings.QUESTIONNAIRE_COMPILER,
                          settings.QUESTIONNAIRE_EDITOR,
                          settings.QUESTIONNAIRE_REVIEWER,
                          settings.QUESTIONNAIRE_PUBLISHER]
            for role in user_roles:
                for old_user in previous_version.get_users_by_role(role):
                    questionnaire.add_user(old_user, role)
        else:
            questionnaire.add_user(user, settings.QUESTIONNAIRE_COMPILER)
        questionnaire.update_users_from_data(
            configuration_code)

        return questionnaire

    def get_id(self):
        return self.id

    def get_permissions(self, current_user):
        """
        Return the permissions of a given user for the current
        questionnaire.

        The following rules apply:
            * Compilers and editors can edit questionnaires.

        Permissions to be returned are:
            * ``edit_questionnaire``
            * ``submit_questionnaire``
            * ``review_questionnaire``
            * ``publish_questionnaire``

        Args:
            ``current_user`` (User): The user.

        Returns:
            ``list``. A list with the permissions of the user for this
            questionnaire object.
        """
        permissions = []
        permission_groups = {
            settings.QUESTIONNAIRE_COMPILER: [{
                'status': [settings.QUESTIONNAIRE_DRAFT,
                           settings.QUESTIONNAIRE_PUBLIC],
                'permissions': ['edit_questionnaire']
            }, {
                'status': [settings.QUESTIONNAIRE_DRAFT],
                'permissions': ['submit_questionnaire']
            }],
            settings.QUESTIONNAIRE_EDITOR: [{
                'status': [settings.QUESTIONNAIRE_DRAFT,
                           settings.QUESTIONNAIRE_PUBLIC],
                'permissions': ['edit_questionnaire']
            }],
            settings.QUESTIONNAIRE_REVIEWER: [{
                'status': [settings.QUESTIONNAIRE_SUBMITTED],
                'permissions': ['edit_questionnaire', 'review_questionnaire']
            }],
            settings.QUESTIONNAIRE_PUBLISHER: [{
                'status': [settings.QUESTIONNAIRE_REVIEWED],
                'permissions': ['edit_questionnaire', 'publish_questionnaire']
            }]
        }
        # Check if defined rules apply to user and set a list with all
        # permissions
        for member_role, user in self.get_users(user=current_user):
            permission_group = permission_groups.get(member_role)
            if not permission_group:
                continue

            for access_level in permission_group:
                if self.status in access_level['status']:
                    permissions.extend(access_level['permissions'])

        user_permissions = current_user.get_all_permissions()
        if ('questionnaire.review_questionnaire' in user_permissions
                and self.status in [settings.QUESTIONNAIRE_SUBMITTED]):
            permissions.extend(['review_questionnaire', 'edit_questionnaire'])
        if ('questionnaire.publish_questionnaire' in user_permissions
                and self.status in [settings.QUESTIONNAIRE_REVIEWED]):
            permissions.extend(['publish_questionnaire', 'edit_questionnaire'])

        return list(set(permissions))

    def get_users(self, **kwargs):
        """
        Helper function to return the users of a questionnaire along
        with their role in this membership.

        Returns:
            ``list``. A list of tuples where each entry contains the
            following elements:

            - [0]: ``string``. The role of the membership.

            - [1]: ``accounts.models.User``. The user object.
        """
        users = []
        for membership in self.questionnairemembership_set.filter(**kwargs):
            users.append((membership.role, membership.user))
        return users

    def get_users_by_role(self, role):
        """
        Return all users of a questionnaire based on their role in the
        membership.

        Args:
            ``role`` (str): The role of the membership used as a filter.

        Returns:
            ``list``. A list of users.
        """
        users = []
        for user_role, user in self.get_users():
            if user_role == role:
                users.append(user)
        return users

    def add_user(self, user, role):
        """
        Add a user.

        Args:
            ``user`` (User): The user.

            ``role`` (str): The role of the user.
        """
        QuestionnaireMembership.objects.create(
            questionnaire=self, user=user, role=role)

    def remove_user(self, user, role):
        """
        Remove a user.

        Args:
            ``user`` (User): The user.

            ``role`` (str): The role of the user.
        """
        self.questionnairemembership_set.filter(user=user, role=role).delete()

    def update_users_from_data(self, configuration_code):
        """
        Based on the data dictionary, update the user links in the
        database. This usually happens after the form of the
        questionnaire was submitted.

        Args:
            ``configuration_code`` (str): The code of the configuration
              of the questionnaire which triggered the update.

            ``compiler`` (accounts.models.User): A user figuring as the
            compiler of the questionnaire.
        """
        questionnaire_configuration = get_configuration(configuration_code)
        user_fields = questionnaire_configuration.get_user_fields()

        # Collect the users appearing in the data dictionary.
        submitted_users = []
        for user_questiongroup in user_fields:
            for user_data in self.data.get(user_questiongroup[0], []):
                user_id = user_data.get(user_questiongroup[1])
                if user_id is None:
                    continue
                submitted_users.append((user_questiongroup[3], user_id))

        # Get the users which were attached before modifying the
        # questionnaire. Collect only those which can be changed through
        # the data dictionary (no functional user roles)
        previous_users = []
        for user_role, user in self.get_users():
            if user_role not in [settings.QUESTIONNAIRE_COMPILER,
                                 settings.QUESTIONNAIRE_EDITOR,
                                 settings.QUESTIONNAIRE_REVIEWER,
                                 settings.QUESTIONNAIRE_PUBLISHER]:
                previous_users.append((user_role, user))

        # Check which users are new (in submitted_users but not in
        # previous_users) and add them to the questionnaire.
        previous_users_found = []
        for submitted_user in submitted_users:
            user_found = False
            for previous_user in previous_users:
                if submitted_user[0] != previous_user[0]:
                    continue
                if str(submitted_user[1]) != str(previous_user[1].id):
                    continue

                user_found = True
                previous_users_found.append(previous_user)

            if user_found is False:
                user = User.objects.get(pk=submitted_user[1])
                self.add_user(user, submitted_user[0])

        # Check for users which were removed (in previous_users but not
        # found when looking through submitted_users) and remove them
        # from the questionnaire
        for removed_user in list(
                set(previous_users) - set(previous_users_found)):
            self.remove_user(removed_user[1], removed_user[0])

    def update_users_in_data(self, user):
        """
        Based on the links in the database, update the data dictionary
        of the questionnaire. This usually happens after a user's
        information (display name) changed.

        Args:
            ``user`` (accounts.models.User): The user to be updated in
            the data dictionary.
        """
        configurations = self.configurations.all()

        # Collect all the user fields of all configurations of the
        # questionnaire
        user_fields = []
        for config in configurations:
            questionnaire_configuration = get_configuration(config.code)
            user_fields.extend(questionnaire_configuration.get_user_fields())

        for user_field in user_fields:
            user_data_list = self.data.get(user_field[0], [])
            for user_data in user_data_list:
                user_id = user_data.get(user_field[1])
                if user_id and str(user_id) == str(user.id):
                    user_data.update({user_field[2]: user.get_display_name()})

        self.save()

    def get_metadata(self):
        """
        Return some metadata about the Questionnaire.

        Returns:
            ``dict``. A dict containing the following metadata:

            * ``created`` (timestamp)

            * ``updated`` (timestamp)

            * ``compilers`` (list): A list of dictionaries containing
              information about the compilers. Each entry contains the
              following data:

              * ``id``

              * ``name``

            * ``editors`` (list): A list of dictionaries containing information
            about the editors. The format is the same as for ``compilers``

            * ``code`` (string)

            * ``configurations`` (list)

            * ``translations`` (list)
        """
        compilers = []
        editors = []
        for compiler in self.members.filter(
                questionnairemembership__role=settings.QUESTIONNAIRE_COMPILER
        ):
            compilers.append({
                'id': compiler.id,
                'name': str(compiler),
            })
        for editor in self.members.filter(
            questionnairemembership__role=settings.QUESTIONNAIRE_EDITOR
        ):
            editors.append({
                'id': editor.id,
                'name': str(editor),
            })
        status = next((x for x in STATUSES if x[0] == self.status), (None, ''))
        status_code = next(
            (x for x in STATUSES_CODES if x[0] == self.status), (None, ''))
        return {
            'created': self.created,
            'updated': self.updated,
            'compilers': compilers,
            'editors': editors,
            'code': self.code,
            'configurations': [
                conf.code for conf in self.configurations.all()],
            'translations': [
                t.language for t in self.questionnairetranslation_set.all()],
            'status': (status_code[1], status[1])
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

    @classmethod
    def get_editable_questionnaires(cls, code, user=None):
        """
        After internal discussion: 'blocking' of questionnaires should happen
        for all items with the same code, not specific questionnaires only.

        Args:
            code: string
            user: accounts.models.User

        Returns:
            queryset

        """
        qs = cls.objects.filter(code=code)
        if user:
            return qs.filter(Q(blocked__isnull=True) | Q(blocked=user))
        else:
            return qs.filter(blocked__isnull=True)

    @classmethod
    def lock_questionnaire(cls, code, user):
        """
        If the questionnaire is not locked, or locked by given user: lock the
        questionnaire for this user - else raise an error.

        Args:
            code: string
            user: accounts.models.User
        """
        editable_questionnaires = cls.get_editable_questionnaires(
            code, user
        )
        if editable_questionnaires.exists():
            raise QuestionnaireLockedException(
                editable_questionnaires.first().blocked
            )
        editable_questionnaires.update(blocked=user)

    def can_edit(self, user):
        return self.get_editable_questionnaires(self.code, user).exists()

    def get_blocked_message(self, user):
        """
        The user that is locking the draft of the questionnaire.

        Args:
            user: accounts.models.User
        """
        editable_questionnaire = self.get_editable_questionnaires(
            self.code, user
        )
        if editable_questionnaire.exists():
            return SUCCESS, _(u"This questionnaire can be edited.")
        else:
            return WARNING, _(u"This questionnaire is "
                              u"locked for editing by {}".format(self.blocked))


class QuestionnaireConfiguration(models.Model):
    """
    Represents a many-to-many relationship between Questionnaires and
    Configurations with additional fields. Additional fields mark the
    configuration in which the Questionnaire was originally entered.
    """
    questionnaire = models.ForeignKey('Questionnaire')
    configuration = models.ForeignKey('configuration.Configuration')
    original_configuration = models.BooleanField(default=False)

    class Meta:
        ordering = ['-original_configuration']


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
    role = models.CharField(max_length=64, choices=QUESTIONNAIRE_ROLES)


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

    def get_interchange_urls_as_list(self):
        """
        Return the URLs for all the thumbnail sizes of the file. Similar
        to :func:`get_interchange_urls` but returns list of tuples
        instead of text.

        Returns:
            ``list``. A list of tuples with the interchange URLs and the
            sizes.
        """
        ret = []
        for thumbnail_format in settings.UPLOAD_IMAGE_THUMBNAIL_FORMATS:
            ret.append((self.get_url(
                thumbnail=thumbnail_format[0]), thumbnail_format[0]))
        ret.append((self.get_url(), 'large'))
        return ret
