import logging
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
    Put selected setting variables to the template.
    """
    file_read_timeout = 5
    cache_key = 'next_maintenance'
    if request.user and request.user.is_authenticated():
        # maybe: block editing depending on this variable as well.
        next_maintenance = cache.get(key=cache_key)
        if next_maintenance is None:
            with open(settings.NEXT_MAINTENANCE) as f:
                next_maintenance = f.read()
                cache.set(key=cache_key, value=next_maintenance, timeout=file_read_timeout)

        if next_maintenance:
            try:
                next_maintenance_time = parse_datetime(next_maintenance)
            except ValueError:
                next_maintenance_time = None

            if not next_maintenance_time or next_maintenance_time < now():
                with open(settings.NEXT_MAINTENANCE, 'w') as f:
                    f.flush()
                    cache.set(key=cache_key, value='', timeout=file_read_timeout)
            else:
                text = _('Caution: Maintenance will start soon ({}), this page '
                         'will not be available for a couple of minutes.<br>'
                         'If you are working on a questionnaire, please make '
                         'sure to save your work!'.format(naturaltime(next_maintenance_time)
                ))
                messages.add_message(request, messages.WARNING, text, extra_tags='safe')

    setting_values = [
        'WARN_HEADER',
        'IS_ACTIVE_FEATURE_MODULE',
        'PIWIK_SITE_ID',
        'GOOGLE_WEBMASTER_TOOLS_KEY',
    ]
    return {value: getattr(settings, value) for value in setting_values}
