from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.utils.timezone import now
import requests
from requests.exceptions import BaseHTTPError
from .conf import settings


class WocatAuthenticationBackend(ModelBackend):
    """
    The class to handle the authentication through :term:`WOCAT`.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        """
        Custom authentication. Returns a user if authentication
        successful.

        The basic workflow is:
        - post username and password into the actual form on the wocat.net site
        - if credentials are valid, a cookie is returned
        - with given cookie, the user_id from wocat.net (typo3) can be resolved
        - with the user_id, the user data can be accessed.

        If any of these steps fail, the authentication fails. Improved exception
        handling will be implemented if requested (should be done, but no time
        is assigned for this task).

        Args:
            password:
            username:

        """
        # Login the user on the remote system.
        session_id = self.remote_login(username, password)
        if not session_id:
            return None

        user_id = self.get_user_id(session_id)
        if not user_id:
            return None

        # Get the users data from the API.
        user_data = get_user_information(user_id)
        if not user_data:
            return None

        # Get django user
        user, created = get_user_model().objects.get_or_create(
                pk=user_id, defaults={'last_login': now()}
        )

        # Update and save the django user with the latest info.
        user.typo3_session_id = session_id
        update_user(user, user_data)

        # TODO: Handle privileges and permissions

        return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None

    def remote_login(self, username, password):
        """
        Login given user on the remote system (typo3).

        Args:
            username: string
            password: string

        Returns: None or a valid session_id (upon successful login)

        """
        try:
            response = requests.post(
                url=settings.AUTH_LOGIN_FORM,
                data={
                    'user': username,
                    'pass': password,
                    'logintype': settings.ACCOUNT_LOGIN_TYPE,
                    'pid': settings.ACCOUNT_PID
                }
            )
        # Catch all exceptions from the request.
        # This could be more granular, if required.
        except BaseHTTPError:
            return None

        return response.cookies.get_dict().get(settings.AUTH_COOKIE_NAME)


    def get_user_id(self, session_id):
        """
        Validate a session ID against the Typo3 REST API of WOCAT.

        Args:
            session_id (str): The session ID as found in the cookie.

        Returns:
            ``None`` or ``int``. Returns the user ID if the session is
            valid, ``None`` if it is not.
        """
        api_login_request = api_login()
        if api_login_request is None:
            return None

        session_request = requests.post(
            url='{}get_session'.format(settings.AUTH_API_URL),
            data={'id': session_id},
            cookies=api_login_request.cookies
        )

        if session_request.status_code != requests.codes.ok:
            return None

        session_data = session_request.json()

        if not session_data.get('success') or not session_data.get('login'):
            return None

        return session_data.get('userid')


def get_user_information(user_id):
    """
    Get the information of a user through the Typo3 REST API of WOCAT.

    Args:
        ``user_id`` (int): The id of the user to query.

    Returns:
        ``dict``. A dict with the user information retrieved from the
        API. If no information was found, an empty dict is returend.
    """
    api_login_request = api_login()
    if api_login_request is None:
        return None

    user_request = requests.post(
        '{}get_user'.format(settings.AUTH_API_URL), data={'id': user_id},
        cookies=api_login_request.cookies)

    if user_request.status_code != 200:
        return None

    user_data = user_request.json()
    if not user_data.get('success'):
        return None

    return user_data


def api_login():
    """
    Log in to the Typo3 REST API of WOCAT.

    Returns:
        ``requests.models.Response``. The response of the login if it
        was successful. The coookies of this response can be used for
        following calls. Returns ``None`` if the login was not successful.
    """
    data = {
        "username": settings.AUTH_API_USER,
        "apikey": settings.AUTH_API_KEY,
    }
    login_request = requests.post(
        '{}auth/login'.format(settings.AUTH_API_URL), data=data)
    if login_request.status_code != 200:
        return None
    if login_request.json().get('status') != 'logged-in':
        return None
    return login_request


def update_user(user, user_information):
    """
    Update a user. This function serves to bundle and eventually
    preprocess the user information from the WOCAT Authentication
    backend and pass it to the update function of the user.

    Args:
        ``user`` (accounts.models.User): The User object.

        ``user_information` (dict): The user dictionary as retrieved
          from :func:`get_user_information`
    """
    if user_information:
        usergroups = [
            g.get('name') for g in user_information.get('usergroup', [])]
        user.update(
            email=user_information.get('username'),
            lastname=user_information.get('last_name'),
            firstname=user_information.get('first_name'),
            usergroups=usergroups)


def search_users(name=''):
    """
    Search for users through the Typo3 REST API of WOCAT.

    Kwargs:
        ``name`` (str): The name of the User to search.

    Args:
        name:

    Returns:
        ``dict``. A dict with the search results retrieved from the API.
        If the query was not successful, an empty dictionary is
        returned.
    """
    api_login_request = api_login()
    if api_login_request is None:
        return {}

    data = {
        'name': name,
    }
    search_request = requests.post(
        '{}get_users'.format(settings.AUTH_API_URL), data=data,
        cookies=api_login_request.cookies)

    if search_request.status_code != 200:
        return {}

    search_data = search_request.json()
    if not search_data.get('success'):
        return {}

    return search_data


def get_logout_url(redirect):
    """
    Return the logout URL of WOCAT as specified in the settings.

    Args:
        ``redirect`` (str): A redirect URL to return to after successful
        logout.

        .. important::
            Make sure to provide the full URL (starting with ``http://``
            for the redirect to function properly.)

    Returns:
        ``str``. The URL of the logout form.
    """
    return '{}?logintype=logout&redirect_url={}'.format(
        settings.AUTH_LOGIN_FORM, redirect)
