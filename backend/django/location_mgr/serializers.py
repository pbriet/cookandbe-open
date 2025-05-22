from rest_framework       import serializers
from location_mgr.models  import Location, Address

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = []

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        exclude = []
