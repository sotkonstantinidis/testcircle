import contextlib

from django.conf import settings
from django.core.urlresolvers import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from configuration.cache import get_configuration
from questionnaire.models import Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Basic serializer for the questionnaire model.
    """

    # Field name in the configuration for the 'title' of a questionnaire. The
    # first matching field will be used. This value is cached.
    title_fields = ['name']
    # Field name in the configuration for the 'excerpt' of a questionnaire.
    # All matching fields will be used and concatenated to a single string.
    # This value is cached.
    excerpt_fields = ['foo']

    # Non-model fields that are used for the serializer.
    title = serializers.SerializerMethodField()
    excerpt = serializers.SerializerMethodField()
    api_url = serializers.SerializerMethodField()
    public_url = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ('id', 'title', 'excerpt', 'created', 'updated', 'api_url',
                  'public_url', )

    def _get_json_values_for_keys(self, obj, keys):
        """
        The values hold lists of dictionaries. The searched keys are in these
        dictionaries. Return these values, concatenated as string.

        Args:
            obj: questionnaire.models.Questionnaire
            keys: list

        Returns:
            string: Values of keys in data.
        """
        configuration = get_configuration(obj.code)
        pass

    def get_title(self, obj):
        """
        Get the name of given object.
        Args:
            obj: questionnaire.models.Questionnaire

        Returns:
            string
        """
        configuration = get_configuration(obj.code)
        # A dict with multiple languages is returned.
        names = configuration.get_questionnaire_name(obj.data)

        # Try to get language in following order:
        # - explicitly passed argument in the querystring
        # - request language
        # - default language from django.
        request = self.context.get('request')
        default_language = settings.LANGUAGES[0][0]
        if not request:
            return names[default_language]
        language = request.query_params.get('lang') or request.LANGUAGE_CODE
        return names.get(language, names.get(default_language))

    def get_excerpt(self, obj):
        """
        Args:
            obj: questionnaire.models.Questionnaire

        Returns: string
        """
        return self._get_json_values_for_keys(obj, self.excerpt_fields)

    def get_api_url(self, obj):
        """
        Args:
            obj: questionnaire.models.Questionnaire

        Returns:
            string: URL of the API detail view for given object.
        """
        return reverse('questionnaires-api-detail',
                       kwargs={'pk': obj.id},
                       request=self.context.get('request'))

    def get_public_url(self, obj):
        """
        Args:
            obj: questionnaire.models.Questionnaire

        Returns:
            string: URL of object on qcat.wocat.net,
                    empty string if lookup fails.
        """
        request = self.context.get('request')
        # We need the request and its build_absolute_uri method.
        if request:
            with contextlib.suppress(NoReverseMatch):
                return request.build_absolute_uri(obj.get_absolute_url())
