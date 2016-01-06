from rest_framework import serializers
from rest_framework.reverse import reverse

from questionnaire.models import Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Simple serializer for the questionnaire model.

    'Data' will probably be a nested serializer.
    """
    detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Questionnaire
        fields = ('id', 'data', 'created', 'updated', 'detail_url', 'version', )

    def get_detail_url(self, obj):
        return reverse('questionnaires-api-detail',
                       kwargs={'pk': obj.id},
                       request=self.context.get('request'))
