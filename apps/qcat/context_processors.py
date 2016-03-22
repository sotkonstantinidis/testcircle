from django.conf import settings


def template_settings(request):
    """
    Put selected setting variables to the template.
    """
    return {
        'WARN_HEADER': settings.WARN_HEADER,
        'PIWIK_SITE_ID': settings.PIWIK_SITE_ID
    }
