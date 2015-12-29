from rest_framework import serializers

from questionnaire.models import Questionnaire


class QuestionnaireSerializer(serializers.ModelSerializer):
    """
    Simple serializer for the questionnaire model.
    """
    class Meta:
        model = Questionnaire
        fields = ('id', 'data', 'created', 'updated', )