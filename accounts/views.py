from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


def login(request):
    """
    Show the login form or log in and redirect if the user is already
    authenticated. The actual authentication is handled by WOCAT (see
    ``login_url``). Based on the session id of the user
    (``fe_typo_user``), the user is also logged in in Django.

    * If the user is already logged in by Django: Redirect to the
      provided URL or to "home".

    * If the user is not logged in by Django, but has a Session ID: If
      it is valid, the user is logged in to Django and redirected. If
      the Session ID is not valid, it is deleted and a message is shown.

    * If the user is not logged in by Django and has no Session ID set,
      the login form is shown.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    redirect = request.GET.get('next', reverse('home'))

    if request.user.is_authenticated():
        return HttpResponseRedirect(redirect)

    res = render(
        request, 'login.html', {
            'redirect_url': request.build_absolute_uri(redirect),
            'login_url': 'https://www.wocat.net/en/sitefunctions/login.html',
            'show_notice': redirect != reverse('home')
        })

    ses_id = request.COOKIES.get('fe_typo_user')
    if ses_id is not None:
        user = authenticate(token=ses_id)
        if user is not None:
            django_login(request, user)
            return HttpResponseRedirect(redirect)
        else:
            res.delete_cookie('fe_typo_user')
            messages.warning(
                request,
                'Login failed. Token may be invalid. Please try again.')

    return res


def logout(request):
    """
    Log the user out, then redirect to home page. Deletes the WOCAT
    session ID of the user (``fe_typo_user``)

    Because the WOCAT logout function does not delete the session
    cookie, a redirect back here is necessary to delete it manually.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    if request.user.is_authenticated():
        django_logout(request)

        return HttpResponseRedirect(
            'https://www.wocat.net/en/sitefunctions/login.'
            'html?logintype=logout&redirect_url={}'.format(
                request.build_absolute_uri(reverse('logout'))))

    next_url = request.build_absolute_uri(
        request.GET.get('next', reverse('home')))

    res = HttpResponseRedirect(next_url)
    res.delete_cookie('fe_typo_user')
    return res
