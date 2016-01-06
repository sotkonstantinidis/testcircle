from configurations import values


class DevMixin:
    DEBUG = values.BooleanValue(True)
    TEMPLATE_DEBUG = values.BooleanValue(True)
    CACHES = values.CacheURLValue('dummy://')
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


class ProdMixin:
    DEBUG = values.BooleanValue(False)
    TEMPLATE_DEBUG = values.BooleanValue(False)


class OpBeatMixin:
    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + (
            'opbeat.contrib.django',
        )

    OPBEAT = {
        'ORGANIZATION_ID': values.Value(environ_name='OPBEAT_ORGANIZATION_ID'),
        'APP_ID': values.Value(environ_name='APP_ID'),
        'SECRET_TOKEN': values.Value(environ_name='OPBEAT_SECRET_TOKEN')
    }

    @property
    def MIDDLEWARE_CLASSES(self):
        return super().MIDDLEWARE_CLASSES + (
        'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    )
