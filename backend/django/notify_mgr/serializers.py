from rest_framework     import serializers, fields
from notify_mgr.models  import Information

class InformationSerializer(serializers.ModelSerializer):
    can_be_read = serializers.BooleanField()
    label       = serializers.CharField()
    
    class Meta:
        model = Information
        fields = ('id', 'title', 'content', 'action', 'priority', 'can_be_read', 'label')
        
