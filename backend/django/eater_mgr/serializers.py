from rest_framework             import serializers
from profile_mgr.serializers    import ProfileSerializer
from eater_mgr.models           import Eater

class EaterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Eater
        exclude = []

    profile = ProfileSerializer()
