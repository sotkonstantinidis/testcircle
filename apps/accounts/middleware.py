from django.conf import settings
from django.contrib.auth import logout, login, authenticate


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

        session_id = request.COOKIES.get(settings.AUTH_COOKIE_NAME)
        if session_id is not None:
            # There is a session ID, make sure it is valid
            user = authenticate(
                token=session_id, current_user=current_user)
            if user is not None:
                login(request, user)
            else:
                self.delete_auth_cookie = True
        else:
            # There is no session ID (anymore), log the user out to make sure
            if request.user.is_authenticated():
                logout(request)

    def process_response(self, request, response):
        """
        Function being called for each response. Used to delete a
        cookie.
        """
        if self.delete_auth_cookie is True:
            response.delete_cookie(settings.AUTH_COOKIE_NAME)
            self.delete_auth_cookie = False
        return response
