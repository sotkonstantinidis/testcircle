from django.conf.urls import url, patterns

from .views import SummaryPDFCreateView

urlpatterns = patterns(
    '',
    url(r'^(?P<id>[\d]+)/summary/$',
        SummaryPDFCreateView.as_view(),
        name='questionnaire_summary'),
)
