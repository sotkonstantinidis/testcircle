from django.conf.urls import url, patterns
from django.views.generic import TemplateView

from .views import HomeView

urlpatterns = patterns(
    '',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^help/questionnaire/$', TemplateView.as_view(
        template_name='wocat/help/questionnaire_introduction.html'),
        name='help_questionnaire_introduction'),
    url(r'^view/(?P<identifier>[^/]+)/$', 'wocat.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^list/$', 'wocat.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'wocat.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)
