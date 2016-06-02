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
    list_data = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    serializer_config = serializers.SerializerMethodField()
    status = serializers.ReadOnlyField(source='status_property')
    translations = serializers.ListField()
    flags = serializers.ListField(source='flags_property')
    url = OutgoingMethodIncomingRawField(read_only=False, allow_null=True)

    class Meta:
        model = Questionnaire
        fields = ('code', 'compilers', 'configurations', 'created', 'data',
                  'editors', 'links', 'list_data', 'name', 'serializer_config',
                  'status', 'translations', 'updated', 'url', 'flags', )

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

        elif data != empty and data.get('serializer_config'):
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

        links = {lang: [] for lang in self.language_codes}

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
        internal_value = super().to_internal_value(data)
        # Add fields to rep that are defined, but not yet set and require the
        # configuration.
        internal_value['serializer_config'] = self.get_serializer_config(None)
        internal_value['list_data'] = self.get_list_data(data['data'], False)
        internal_value['name'] = self.get_name(data['data'], False)
        return internal_value

    def to_list_values(self, **kwargs):
        """
        Prepare validated_data to work with get_list_values.
        """
        if self.validated_data:
            # Prevent circular import
            from questionnaire.utils import prepare_list_values
            return prepare_list_values(
                data=self.validated_data, config=self.config, **kwargs
            )
