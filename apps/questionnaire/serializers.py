# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import empty

from configuration.cache import get_configuration
from configuration.configuration import QuestionnaireConfiguration
from configuration.models import Configuration
from configuration.utils import ConfigurationList

from .models import Questionnaire


class RestoreMethodField(serializers.SerializerMethodField):
    """
    SerializerMethodField is read_only, but deserialization is required as well.

    """
    def __init__(self, method_name=None, attribute=None, **kwargs):
        self.method_name = method_name
        self.attribute = attribute
        kwargs['source'] = '*'
        kwargs['read_only'] = False
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def get_attribute(self, instance):
        """
        For some methods, 'data' is required as parameter, even if the
        attribute is 'name' or such.
        """
        if not(isinstance(instance, Questionnaire)) and self.attribute:
            return instance.get(self.attribute)
        return super().get_attribute(instance)

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        """
        When restoring to an object, call the method with 'is_attribute'=False
        """
        method = getattr(self.parent, self.method_name)
        return method(value, is_attribute=isinstance(value, Questionnaire))


class OutgoingMethodIncomingRawField(serializers.SerializerMethodField):
    """
    Call serializer method when serializing, return raw element from dict when
    deserializing.
    """
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        kwargs['read_only'] = False
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def get_attribute(self, instance):
        """
        The whole instance is needed when serializing objects; deserializing
        only requires the field 'url'
        """
        self.source_attrs = [] if isinstance(instance, Questionnaire) \
            else self.field_name
        return super().get_attribute(instance)

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        """
        Serializing: call method (e.g. get_url)
        Deserializing: return string from dict.
        """
        return super().to_representation(value) if \
            isinstance(value, Questionnaire) else value


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Serializes the questionnaire with given configuration.
    """
    compilers = serializers.ListField()
    configurations = serializers.ListField(source='configurations_property')
    data = serializers.DictField()
    editors = serializers.ListField()
    links = OutgoingMethodIncomingRawField()
    list_data = RestoreMethodField(attribute='data')
    name = RestoreMethodField(attribute='data')
    serializer_config = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField(source='status_property')
    translations = serializers.ListField()
    url = OutgoingMethodIncomingRawField(read_only=False)

    class Meta:
        model = Questionnaire
        fields = ('code', 'compilers', 'configurations', 'created', 'editors',
                  'data', 'editors', 'links', 'list_data', 'name',
                  'serializer_config', 'status', 'translations', 'updated',
                  'url', )

    def __init__(self, instance=None, data=empty, **kwargs):
        """
        Keyword Args:
            config: configuration.QuestionnaireConfiguration

        Setup the correct config. If no config is passed, use the questionnaires
        default config. The config is required for some fields that can only
        be accessed on the actual configuration object.

        If a model instance is serialized, the 'instance' kwarg is passed.
        If an elasticsearch result is deserialized, the 'data' kwar is passed.
        """
        config = kwargs.pop('config', None)
        is_valid_config = isinstance(config, QuestionnaireConfiguration)

        # Set config
        if is_valid_config:
            self.config = config

        elif instance:
            config = instance.configurations.filter(
                questionnaireconfiguration__original_configuration=True
            )
            if config.exists():
                self.config = get_configuration(config.first().code)
            else:
                raise ValueError(_(u"Couldn't load configuration for "
                                   u"questionnaire."))

        elif data.get('serializer_config'):
            # Restore object from json data. Make sure the serializer_config
            # is valid / exists in the db.
            config = Configuration.get_active_by_code(data['serializer_config'])
            if not config:
                raise ValueError(_(u"Invalid configuration code stored in"
                                   u"elasticsearch."))

            self.config = get_configuration(data['serializer_config'])

        else:
            raise ValueError(_(u"Can't serialize questionnaire without a valid "
                               u"configuration."))

        # Helpers
        self.language_codes = dict(settings.LANGUAGES).keys()
        self.config_list = ConfigurationList()
        super().__init__(instance=instance, data=data, **kwargs)

    def get_links(self, obj):
        """
        Return a dict with URLs of the linked questionnaires.
        """
        # Prevent circular import
        from questionnaire.utils import get_link_display

        links = dict.fromkeys(self.language_codes, [])

        for link in obj.links.all():

            link_configuration_db = link.configurations.first()
            if link_configuration_db is None:
                continue

            link_configuration = self.config_list.get(
                link_configuration_db.code
            )

            name_data = link_configuration.get_questionnaire_name(link.data)

            try:
                original_language = link.questionnairetranslation_set.first()\
                    .language
            except AttributeError:
                original_language = None

            for language in self.language_codes:
                name = name_data.get(language, name_data.get(original_language))
                links[language].append(get_link_display(
                    link_configuration.keyword, name, link.code)
                )
        return dict(links)

    def get_list_data(self, obj, is_attribute=True):
        param = obj.data if is_attribute else obj
        return self.config.get_list_data([param])[0]

    def get_name(self, obj, is_attribute=True):
        param = obj.data if is_attribute else obj
        return self.config.get_questionnaire_name(param)

    def get_serializer_config(self, obj):
        """
        Store the config-id in the serialized data, so the same config can
        be used to deserialize the object, see __init__.
        """
        return self.config.keyword

    def get_url(self, obj):
        return obj.get_absolute_url()

    def to_internal_value(self, data):
        serializer_config = data.pop('serializer_config')
        internal_value = super(QuestionnaireSerializer, self).to_internal_value(data)
        # Add fields to rep that are defined, but not yet set.
        internal_value['serializer_config'] = serializer_config
        return internal_value
