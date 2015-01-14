from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


class User(AbstractBaseUser, PermissionsMixin):
    """
    The model representing a user of QCAT. This is basically a local
    replication of the user database of :term:`WOCAT` which handles the
    authentication. Therefore, no password is stored.

    The user model has the following fields:
        * email (varchar, acts as username)
        * name (varchar)
        * last_login (timestamp, automatically generated)
        * date_joined (timestamp, automatically generated)
        * is_superuser (boolean)
        * password (varchar, empty)

    .. todo::
        How to handle the privileges with regard to different
        configurations (e.g. moderator in WOCAT, editor in UNCCD)
    """
    email = models.EmailField(
        verbose_name='email address', unique=True, max_length=255)
    name = models.CharField(max_length=100, null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def is_active(self):
        """
        Indicates if a user account is currently active. Always returns
        True because any user in the database (and thus logged in
        through
        :class:`accounts.authentification.WocatAuthenticationBackend`)
        is considered as being active.

        Returns:
            ``bool``. Always returns ``True``.
        """
        return True

    @property
    def is_staff(self):
        """
        Handles the access to the Django administration interface.

        The following users have access to the administration interface:

            * Superusers (``is_superuser`` set to True)
            * Members of the following :term:`User Groups`:
                * :ref:`usergroups-administrators`

        Returns:
            ``bool``. Returns ``True`` if a user can access the
            administration interface, else ``False``.
        """
        if self.is_superuser is True:
            return True
        for group in self.groups.all():
            if group.name in ['Administrators', 'Translators']:
                return True
        return False

    def get_full_name(self):
        """
        A full representation of the user.

        Returns:
            ``str``. The email address of the user.
        """
        return self.email

    def get_short_name(self):
        """
        A short representation of the user.

        Returns:
            ``str``. The email address of the user.
        """
        return self.email

    def __str__(self):
        return self.email

    @staticmethod
    def create_new(email, name=''):
        """
        Creates and returns a new user.

        Args:
            ``email`` (str): The email address of the user.

            ``name`` (str): The name of the user.

        Returns:
            :class:`accounts.models.User`. The newly created user.
        """
        user = User.objects.create(email=email, name=name)
        return user

    def update(self, name, privileges=[]):
        """
        Handles the one-way synchronization of the user database by
        updating the values.

        Args:
            ``name`` (str): The name of the user.

            ``privileges`` (list): A list of privileges of the user.

            .. todo::
                Actually handle privileges.
        """
        self.name = name

#     def is_authenticated(self):
#         """
#         Indicates if a user is authenticated. This is a way to tell if
#         the user has been authenticated in templates and therefore
#         always returns True.

#         Returns:
#             ``bool``. Always returns ``True``.
#         """
#         return True
