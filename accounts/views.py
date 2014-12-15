from django.contrib.auth import (
    authenticate,
    login as django_login,
    logout as django_logout,
)
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _

# from accounts.authentication import WocatAuthenticationBackend
from accounts.forms import LoginForm


def login(request):
    """
    Show the login form and handle the form submission to log users in.
    After login, redirect users to where they came from or to the home
    page by default.
    """
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('home'))

    msg = None
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'])
            if user is not None:
                django_login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(reverse('home'))
            else:
                msg = _('The username and/or password you entered were not '
                        'correct.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'msg': msg})


def logout(request):
    """
    Log the user out, then redirect to home page.
    """
    if request.user.is_authenticated():
        django_logout(request)
    return HttpResponseRedirect(reverse('home'))
