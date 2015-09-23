import requests
from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import (
    authenticate as auth_authenticate,
    get_user_model,
    login as django_login,
    logout as django_logout,
)


class WocatAuthenticationMiddleware(object):
    """
    Middleware checking the (remote) authentication for each request.
    """

    def __init__(self):
        self.delete_auth_cookie = False

    def process_request(self, request):
        """
        Function being called for each request. Check if a session ID is
        present and if so, check if it is valid.
        """
        try:
            current_user = request.user
        except AttributeError:
            current_user = None

        session_id = request.COOKIES.get(get_session_cookie_name())
        if session_id is not None:
            # There is a session ID, make sure it is valid
            user = auth_authenticate(
                token=session_id, current_user=current_user)
            if user is not None:
                django_login(request, user)
            else:
                self.delete_auth_cookie = True
        else:
            # There is no session ID (anymore), log the user out to make sure
            if request.user.is_authenticated():
                django_logout(request)

    def process_response(self, request, response):
        """
        Function being called for each response. Used to delete a
        cookie.
        """
        if self.delete_auth_cookie is True:
            response.delete_cookie(get_session_cookie_name())
            self.delete_auth_cookie = False
        return response


class WocatAuthenticationBackend(ModelBackend):
    """
    The class to handle the authentication through :term:`WOCAT`.
    """

    def authenticate(self, token=None, current_user=None):
        """
        Custom authentication. Returns a user if authentication
        successful.
        """
        User = get_user_model()

        user_id = validate_session(token)
        if user_id is None:
            return None

        # If a user is already logged in, make sure the session ID
        # matches the current user. This also prevents having to query
        # the user again from the database.
        if current_user and str(current_user.id) == user_id:
            return current_user

        try:
            # Check if the user exists in the local database
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            # Create a user in the local database
            user_info = get_user_information(user_id)
            user = User.create_new(
                id=user_id, email=user_info.get('username'),
                lastname=user_info.get('last_name'),
                firstname=user_info.get('first_name'))

        except:
            return None

        # TODO: Handle privileges and permissions

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


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


def validate_session(session_id):
    """
    Validate a session ID against the Typo3 REST API of WOCAT.

    Args:
        ``session_id`` (str): The session ID as found in the cookie.

    Returns:
        ``None`` or ``int``. Returns the user ID if the session is
        valid, ``None`` if it is not.
    """
    api_login_request = api_login()
    if api_login_request is None:
        return None

    data = {
        'id': session_id,
    }
    session_request = requests.post(
        '{}get_session'.format(settings.AUTH_API_URL), data=data,
        cookies=api_login_request.cookies)

    if session_request.status_code != 200:
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

    data = {
        'id': user_id,
    }
    user_request = requests.post(
        '{}get_user'.format(settings.AUTH_API_URL), data=data,
        cookies=api_login_request.cookies)

    if user_request.status_code != 200:
        return {}

    user_data = user_request.json()
    if not user_data.get('success'):
        return {}

    return user_data


def search_users(name=''):
    """
    Search for users through the Typo3 REST API of WOCAT.

    Kwargs:
        ``name`` (str): The name of the User to search.

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


def get_login_url():
    """
    Return the login URL of WOCAT as specified in the settings.

    Returns:
        ``str``. The URL of the login form.
    """
    return settings.AUTH_LOGIN_FORM


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


def get_session_cookie_name():
    """
    Return the name of the cookie used for the authentication.
    """
    return 'fe_typo_user'
