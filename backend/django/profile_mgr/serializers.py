
from rest_framework             import serializers, fields

from common.rest                import MinValueValidator, MaxValueValidator

from profile_mgr.models         import Profile, Taste, RestrictedFood, RecipeDislike

from recipe_mgr.serializers     import FoodTagSerializer

from planning_mgr.models        import MealType, MealPlace

from collections                import defaultdict

from eater_mgr.models           import Eater
from eater_mgr.ratios           import RatiosCalculator

class ProfileSerializer(serializers.ModelSerializer):
    is_main_profile = serializers.BooleanField(read_only = True)

    class Meta:
        model = Profile
        exclude = []
        extra_kwargs = {'weight': {'required': False, 'allow_null': True, 'validators': [MinValueValidator(1), MaxValueValidator(500)]},
                        'height': {'required': False, 'allow_null': True, 'validators': [MinValueValidator(10), MaxValueValidator(300)]},
                        }

    def to_representation(self, instance):
        results = super().to_representation(instance)
        if instance is None:
            return results
        if isinstance(instance, list):
            iter_elts = (instance, results)
        else:
            iter_elts = ([instance], [results])

        profiles = list(iter_elts[0])
        assert len(profiles) > 0, "no profile for this user"
        user = profiles[0].creator
        ratios = RatiosCalculator(user).profile_ratios

        for (profile, result) in zip(*iter_elts):
            result["ratio"] = ratios[profile.id]
            result["imc"] = round(profile.imc, 1)
            eater = Eater.objects.filter(user=profile.creator, profile=profile)
            if eater.count() == 0: eater = None
            else:                  eater = list(eater)[0]
            result["regular_eater"] = eater and eater.regular
        return results

class TasteSerializer(serializers.ModelSerializer):
    food_tag = FoodTagSerializer()
    class Meta:
        model = Taste
        exclude = []

class TasteWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taste
        exclude = []

class RecipeDislikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeDislike
        exclude = []

class RestrictedFoodSerializer(serializers.ModelSerializer):
    food_tag = FoodTagSerializer()
    class Meta:
        model = RestrictedFood
        exclude = []

class AttendanceSerializer(object):
    @staticmethod
    def serialize(attendances):
        res     = {"days" : [],
                   "places" : dict((place.id, place.key) for place in MealPlace.objects.all()),
                   "meals"  : sorted(list({"id" : meal.id, "name" : meal.name} for meal in MealType.objects.all()), key=lambda x: x['id']),
                  }
        for week_day, meal_data in attendances.items():
            day = dict()
            for meal_type, meal_place in meal_data.items():
                day[meal_type.id] = meal_place.key
            res["days"].append(day)
        return res

    @staticmethod
    def deserialize(data):
        mealTypes   = dict((meal.id, meal) for meal in MealType.objects.all())
        mealPlaces  = dict((place.key, place) for place in MealPlace.objects.all())
        attendances = defaultdict(dict)
        for week_day, day_data in enumerate(data["days"]):
            for meal_id, place_key in day_data.items():
                attendances[week_day][mealTypes[int(meal_id)]] = mealPlaces[place_key]
        return attendances

class ProfileMetricSerializer(object):
    @staticmethod
    def serialize(profile_metric):
        return {"key": profile_metric.key,
                "name": profile_metric.name,
                "unit": profile_metric.unit,
                "description": profile_metric.description}