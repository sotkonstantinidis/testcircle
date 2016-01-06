from configurations import values


class DevMixin:
    DEBUG = values.BooleanValue(True)
    TEMPLATE_DEBUG = values.BooleanValue(True)
    CACHES = values.CacheURLValue('dummy://')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


class ProdMixin:
    DEBUG = values.BooleanValue(False)
    TEMPLATE_DEBUG = values.BooleanValue(False)
