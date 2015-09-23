from django.contrib import messages
from django.contrib.auth import (
    logout as django_logout,
)
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from qcat.utils import url_with_querystring
from accounts.authentication import (
    get_login_url,
    get_logout_url,
    get_session_cookie_name,
    get_user_information,
    search_users,
    update_user,
)
from accounts.models import User


def welcome(request):
    """
    The landing page of a user after he logged in. Update the user
    details and redirect to the page provided or "home".

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response (through redirect)
    """
    home = reverse('home')
    redirect = request.GET.get('next', home)

    # In case the user was not logged in properly route him to "home"
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))
    session_id = request.COOKIES.get(get_session_cookie_name())
    if session_id is None:
        return HttpResponseRedirect(reverse('home'))

    # Update the user information
    user = request.user
    user_info = get_user_information(user.id)
    update_user(user, user_info)

    messages.info(
        request, 'Welcome {}'.format(user_info.get('first_name')))

    return HttpResponseRedirect(redirect)


def login(request):
    """
    Show the login form or log in and redirect if the user is already
    authenticated. The actual authentication is handled by the
    authentication backend as specified in the settings (
    ``settings.AUTH_LOGIN_FORM``).

    .. seealso::
        :func:`accounts.authentication.get_login_url`

    After login, the user is sent to the welcome page where he is logged
    in in Django. Afterwards, he is redirected to the provided page
    (``next``) or to "home".

    * If the user is already logged in by Django: Redirect to the
      provided URL or to "home".

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

    # Prevent that the URL is already encoded by inserting it afterwards
    welcome_url = url_with_querystring(
        reverse('welcome'), next='REDIRECT_URL')
    welcome_url = welcome_url.replace('REDIRECT_URL', redirect)

    return render(
        request, 'login.html', {
            'redirect_url': request.build_absolute_uri(welcome_url),
            'login_url': get_login_url(),
            'show_notice': redirect != reverse('home')
        })


def logout(request):
    """
    Log the user out. The actual logout is handled by the authentication
    backend as specified in the settings (``settings.AUTH_LOGIN_FORM``).

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    redirect = reverse('home')

    django_logout(request)

    ses_id = request.COOKIES.get(get_session_cookie_name())
    if ses_id is not None:
        return HttpResponseRedirect(
            get_logout_url(request.build_absolute_uri(redirect)))

    return HttpResponseRedirect(redirect)


def user_search(request):
    """
    JSON view to search for users. The search is handled by the
    authentication backend as specified in the settings
    (``settings.AUTH_LOGIN_FORM``).

    Args:
        ``request`` (django.http.HttpRequest): The request object with
        optional GET parameter ``name``.

    Returns:
        ``JsonResponse``. A rendered JSON response.
    """
    search = search_users(name=request.GET.get('name', ''))
    if not search:
        search = {
            'success': False,
            'message': 'Error: The user database cannot be queried right now.'
        }

    return JsonResponse(search)


@require_POST
@login_required
def user_update(request):
    """
    JSON view to create or update a user. The user is queried through
    the authentication backend as specified in the settings
    (``settings.AUTH_LOGIN_FORM``).

    Args:
        ``request`` (django.http.HttpRequest): The request object with
        POST parameter ``uid`` (the user ID).

    Returns:
        ``JsonResponse``. A rendered JSON response.
    """
    ret = {
        'success': False,
    }

    user_uid = request.POST.get('uid')
    if user_uid is None:
        ret['message'] = 'No user ID (uid) provided.'
        return JsonResponse(ret)

    # Try to find the user in the authentication DB
    user_info = get_user_information(user_uid)
    if not user_info:
        ret['message'] = 'No user with ID {} found in the authentication '
        'database.'.format(user_uid)
        return JsonResponse(ret)

    # Update (or insert) the user details in the local database
    user, created = User.objects.get_or_create(pk=user_uid)
    update_user(user, user_info)

    ret = {
        'name': user.get_display_name(),
        'success': True,
    }
    return JsonResponse(ret)


def details(request, id):
    """
    View for the details of a user. Also does an update of the user
    information against the authentication backend.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``id`` (int): The ID of the user.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    user = get_object_or_404(User, pk=id)

    # Update the user details
    user_info = get_user_information(user.id)
    update_user(user, user_info)

    return render(request, 'details.html', {
        'detail_user': user,
    })
