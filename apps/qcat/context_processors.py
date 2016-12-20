from django.conf import settings


def template_settings(request):
    """
    Put selected setting variables to the template.
    """
    setting_values = [
        'WARN_HEADER',
        'IS_ACTIVE_FEATURE_MODULE',
        'IS_ACTIVE_FEATURE_SUMMARY',
        'PIWIK_SITE_ID',
        'GOOGLE_WEBMASTER_TOOLS_KEY'
    ]
    return {value: getattr(settings, value) for value in setting_values}
