from django.contrib.auth import get_user_model

from accounts.connection import get_connection


class WocatAuthenticationBackend(object):
    """
    The class to handle the authentication through :term:`WOCAT`.
    """

    def authenticate(self, username, password):
        """
        Custom authentication. Returns a user if authentication successful.
        """
        User = get_user_model()
        queried_user = self._do_auth(username, password)

        if not queried_user:
            return None

        privileges = queried_user[1].split(',')

        try:
            # Check if the user exists in the local database
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            # Create a user in the local database
            user = User.create_new(email=username)

        user.update(name=queried_user[4], privileges=privileges)

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _do_auth(self, username, password):
        """
        Do the actual WOCAT login. The login is based on the username
        and password and upon successful login, it should either return
        - the session_id which can be used to query the user information
          and permission groups
        or
        - the session_id along with the user information and permission
          groups in a single response.

        Returns None or a tuple with:
        - (str) session id
        - (str) groups: comma-separated list of groups (~privileges)
        - (int) id
        - (str) username
        - (str) name
        """

        # TODO: Actually use password to check login!

        if not username or not password:
            return None

        # TODO
        # Temporary fix: Try to find the username in the current WOCAT
        # sessions.
        cursor = get_connection().cursor()
        cursor.execute(
            "SELECT fe_sessions.ses_id, fe_users.usergroup, fe_users.uid, "
            "fe_users.username, fe_users.name "
            "FROM fe_sessions JOIN fe_users "
            "ON fe_sessions.ses_userid = fe_users.uid "
            "WHERE fe_users.username = %s", [username])
        users = cursor.fetchall()

        if len(users) != 1:
            # No (or rather unlikely, too many) user found
            return None

        return users[0]
