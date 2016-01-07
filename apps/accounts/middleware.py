from django.conf import settings
from django.contrib.auth import logout, login
from .client import typo3_client

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
        session_id = request.COOKIES.get(settings.AUTH_COOKIE_NAME)

        if request.user.is_authenticated():
            if not session_id or not typo3_client.get_user_id(session_id):
                # There is an invalid session ID, mark it for removal.
                logout(request)
                self.delete_auth_cookie = True

        elif session_id:
            user_id = typo3_client.get_user_id(session_id)
            user = typo3_client.get_and_update_django_user(user_id, session_id)
            if user_id and user:
                login(request, user)

    def process_response(self, request, response):
        """
        Function being called for each response. Used to delete a
        cookie.
        """
        if self.delete_auth_cookie is True:
            response.delete_cookie(settings.AUTH_COOKIE_NAME)
            self.delete_auth_cookie = False
        return response
