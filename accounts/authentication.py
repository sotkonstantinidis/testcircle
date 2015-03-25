from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db import connection
from django.conf import settings


class WocatAuthenticationBackend(ModelBackend):
    """
    The class to handle the authentication through :term:`WOCAT`.
    """

    def authenticate(self, token=None):
        """
        Custom authentication. Returns a user if authentication successful.
        """
        User = get_user_model()

        queried_user = self._do_auth(token)

        if not queried_user:
            return None

        try:
            # Check if the user exists in the local database
            user = User.objects.get(email=queried_user[0])
        except User.DoesNotExist:
            # Create a user in the local database
            user = User.create_new(email=queried_user[0])

        except:
            return None

        privileges = queried_user[1].split(',')
        fullname = ' '.join([queried_user[2], queried_user[3]])
        user.update(name=fullname, privileges=privileges)

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _do_auth(self, token):
        """
        Do the actual WOCAT login. The login is based on the username
        and password and upon successful login, it should either return
        - the session_id which can be used to query the user information
          and permission groups
        - the session_id along with the user information and permission
          groups in a single response.

        Returns None or a tuple with:

        - (str) username (= email)
        - (str) groups: comma-separated list of groups (~privileges)
        - (int) firstname
        - (str) lastname
        """
        # TODO: Privileges!

        if not token:
            return None

        # Check token
        cursor = connection.cursor()
        try:
            cursor.execute(
                "SELECT username, status, first_name, last_name FROM "
                "wocat_users WHERE ses_id = %s",
                [token])
            users = cursor.fetchall()

            if len(users) < 1:
                # No user found
                return None

            return users[0]

        except:
            """
            In DEBUG mode, try also to authenticate through an external
            typo3 database. This is used for local development when the
            foreign authentication table is not available locally.
            """
            if settings.DEBUG is True and 'typo3' in settings.DATABASES:
                from django.db import connections
                cursor = connections['typo3'].cursor()
                try:
                    cursor.execute(
                        "SELECT username, status, first_name, last_name FROM "
                        "wocat_users WHERE ses_id = %s",
                        [token])
                    users = cursor.fetchall()

                    if len(users) < 1:
                        # No user found
                        return None

                    return users[0]
                except:
                    pass

            return None
