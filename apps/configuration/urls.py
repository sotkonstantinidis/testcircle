from django.conf.urls import url, patterns

from .views import EditionNotesView

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', EditionNotesView.as_view(), name='release_notes'),
)
