from django.db import models
from django.utils import timezone


class User(models.Model):
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
