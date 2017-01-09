import logging
from datetime import datetime

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


def template_settings(request):
    """
    Put selected setting variables to the template and check for maintenance
    announcements
    """
    maintenance_announcement = MaintenanceAnnouncement(request)

    setting_values = [
        'WARN_HEADER',
        'IS_ACTIVE_FEATURE_MODULE',
        'PIWIK_SITE_ID',
        'GOOGLE_WEBMASTER_TOOLS_KEY',
    ]
    return {
        **maintenance_announcement.overlay,
        **{value: getattr(settings, value) for value in setting_values}
    }


class MaintenanceAnnouncement:

    file_read_timeout = 5
    cache_key = 'next_maintenance'

    def __init__(self, request):
        self.request = request
        self.overlay = {}
        next_maintenance = self.get_next_maintenance()

        if next_maintenance:
            self.set_display_deploy_warning(next_maintenance)
            self.set_maintenance_overlay(next_maintenance)

    def get_next_maintenance(self) -> datetime:
        """
        Check if maintenance is planned and return the datetime
        """
        if self.request.user and self.request.user.is_authenticated():
            # maybe: block editing depending on this variable as well.
            next_maintenance = cache.get(key=self.cache_key)
            if next_maintenance is None:
                with open(settings.NEXT_MAINTENANCE) as f:
                    next_maintenance = f.read()
                    cache.set(
                        key=self.cache_key,
                        value=next_maintenance,
                        timeout=self.file_read_timeout
                    )

            if next_maintenance:
                try:
                    next_maintenance_time = parse_datetime(next_maintenance)
                except ValueError:
                    next_maintenance_time = None

                if not next_maintenance_time or next_maintenance_time < now():
                    with open(settings.NEXT_MAINTENANCE, 'w') as f:
                        f.flush()
                        cache.set(
                            key=self.cache_key,
                            value='',
                            timeout=self.file_read_timeout
                        )
                else:
                    return next_maintenance_time

        return None

    def set_display_deploy_warning(self, next_maintenance_time: datetime) -> None:
        """
        For all requests: set the django message, displayed as 'flash' on the
        website.
        """
        messages.add_message(
            self.request,
            messages.WARNING,
            self.get_full_maintenance_text(next_maintenance_time),
            extra_tags='safe'
        )

    def set_maintenance_overlay(self, next_maintenance_time: datetime) -> None:
        """
        Once per maintenance window and user: show an overlay that the user must
        actively dismiss once.
        """
        saw_warning = self.request.session.get('saw_deploy_warning', '')
        try:
            saw_warning = parse_datetime(saw_warning)
        except ValueError:
            saw_warning = None

        if not saw_warning or saw_warning < now():
            self.request.session['saw_deploy_warning'] = next_maintenance_time.isoformat()
            text = self.get_full_maintenance_text(next_maintenance_time)
            self.overlay.update({'maintenance_warn_overlay': text})
        elif saw_warning and saw_warning < now():
            del self.request.session['saw_deploy_warning']

    @staticmethod
    def get_full_maintenance_text(next_maintenance_time: datetime) -> str:
        return _('Caution: Maintenance will start soon ({}), this page will '
                 'not be available for a couple of minutes.<br>'
                 'If you are working on a questionnaire, please make sure to '
                 'save your work!'.format(naturaltime(next_maintenance_time)))
