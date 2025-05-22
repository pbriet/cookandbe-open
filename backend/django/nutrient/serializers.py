from rest_framework         import serializers
from nutrient.models        import Nutrient, NutrientPack, CookingMethodEffect

class NutrientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nutrient
        fields = ('id', 'key', 'name', 'short_name', 'unit', 'infoods_tagname')

class CookingMethodEffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingMethodEffect
        exclude = []


class NutrientPackSerializer(serializers.ModelSerializer):
    class Meta:
        model = NutrientPack
        exclude = []

    nutrients = NutrientSerializer(many=True)