from django.db import models
from django.utils import timezone


class User(models.Model):
    """
    The model representing a user of QCAT. This is basically a local
    replication of the user database of :term:`WOCAT` which handles the
    authentication. Therefore, no password is stored.

    .. todo::
        How to handle the privileges with regard to different
        configurations (e.g. moderator in WOCAT, editor in UNCCD)
    """
    email = models.EmailField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    last_login = models.DateTimeField(default=timezone.now)
    REQUIRED_FIELDS = ()
    USERNAME_FIELD = 'email'

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def update(self, name, privileges=[]):
        """
        Handles the one-way synchronization of the user database.
        """
        self.name = name

    @staticmethod
    def create_new(email, name=''):
        user = User.objects.create(email=email, name=name)
        return user
