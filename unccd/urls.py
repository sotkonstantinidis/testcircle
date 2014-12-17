from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'unccd.views.home', name='unccd_home'),
)
