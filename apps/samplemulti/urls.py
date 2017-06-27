from django.conf.urls import url, patterns
from django.views.generic import TemplateView

from questionnaire.views import QuestionnaireEditView, QuestionnaireStepView, \
    QuestionnaireView, QuestionnaireLinkSearchView, QuestionnaireListView

urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name='samplemulti/home.html'), name='home'),
    url(r'^view/(?P<identifier>[^/]+)/$',
        QuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'samplemulti.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', QuestionnaireEditView.as_view(url_namespace=__package__),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$', QuestionnaireEditView.as_view(url_namespace=__package__),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        QuestionnaireStepView.as_view(url_namespace=__package__), name='questionnaire_new_step'),
    url(r'^search/links/$', QuestionnaireLinkSearchView.as_view(
        configuration_code=__package__), name='questionnaire_link_search'),
    url(r'^list/$', QuestionnaireListView.as_view(configuration_code=__package__),
        name='questionnaire_list'),
    url(r'^list_partial/$', QuestionnaireListView.as_view(configuration_code=__package__),
        name='questionnaire_list_partial'),
)
