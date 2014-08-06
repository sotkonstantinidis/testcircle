from django.conf.urls import patterns, include, url
# from django.contrib import admin

urlpatterns = patterns(
    '',

    url(r'^$', 'qcat.views.home', name='home'),

    # View to change language
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # url(r'^admin/', include(admin.site.urls)),
)
