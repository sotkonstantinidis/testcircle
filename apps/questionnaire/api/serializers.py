import contextlib

from django.core.urlresolvers import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

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

    def get_title(self, obj):
        """
        Get the name of given object.
        Args:
            obj: questionnaire.models.Questionnaire

        Returns:
            string
        """
        return 'foo'

    def get_excerpt(self, obj):
        """
        Args:
            obj: questionnaire.models.Questionnaire

        Returns: string
        """
        return 'bar'

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
        with contextlib.suppress(NoReverseMatch):
            return obj.get_absolute_url()
