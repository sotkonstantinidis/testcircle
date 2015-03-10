from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'sample.views.home', name='sample_home'),
)
