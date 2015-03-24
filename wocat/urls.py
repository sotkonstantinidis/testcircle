from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'wocat.views.home', name='wocat_home'),
)
