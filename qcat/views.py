from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render


def home(request):

    ses_id = request.COOKIES.get('fe_typo_user')
    if ses_id is not None and not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('login'))

    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')
