# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import empty

from configuration.cache import get_configuration
from configuration.configuration import QuestionnaireConfiguration
from configuration.models import Configuration

from .models import Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Serializes the questionnaire with given configuration.
    """
    compilers = serializers.ListField()
    configurations = serializers.ListField(source='configurations_property')
    data = serializers.DictField()
    editors = serializers.ListField()
    reviewers = serializers.ListField()
    links = serializers.ListField(source='links_property')
    list_data = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    original_locale = serializers.CharField()
    serializer_config = serializers.SerializerMethodField()
    status = serializers.ListField(source='status_property')
    translations = serializers.ListField()
    flags = serializers.ListField(source='flags_property')
    url = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ('code', 'compilers', 'configurations', 'created', 'data',
                  'editors', 'links', 'list_data', 'name', 'original_locale', 'reviewers',
                  'serializer_config', 'status', 'translations', 'updated',
                  'url', 'flags', )

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

        super().__init__(instance=instance, data=data, **kwargs)

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
        # Remove language from url, as this is 'None' if executed from command
        # line, or whichever active language if called from the search-admin panel.
        # See: https://redmine.cde.unibe.ch/issues/1716
        url = obj.get_absolute_url()
        return url[url.find('/', 1):]

    def to_internal_value(self, data):
        internal_value = dict(super().to_internal_value(data))
        # Add fields to rep that are defined, but not yet set and require the
        # configuration.
        internal_value['serializer_config'] = self.get_serializer_config(None)
        internal_value['list_data'] = self.get_list_data(data['data'], False)
        internal_value['name'] = self.get_name(data['data'], False)
        internal_value['url'] = data.get('url', '')
        replace_property_keys = filter(lambda item: item.endswith('_property'), internal_value.keys())
        for key in replace_property_keys:
            internal_value[key.replace('_property', '')] = internal_value.pop(key)
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
