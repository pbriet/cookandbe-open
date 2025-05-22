from rest_framework         import serializers, fields
from polls.models           import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        exclude = []

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = []

    choices    = ChoiceSerializer(many=True)
