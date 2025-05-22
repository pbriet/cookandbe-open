
from django.core.validators     import MaxValueValidator, MinValueValidator
from django.db                  import models

from common.model               import NamedModel

from user_mgr.models            import User

class Nutrient(NamedModel, models.Model):
    """
    Nutrient: vitamin, calcium, ...
    """
    key                 = models.CharField(max_length=50, unique=True)
    name                = models.CharField(max_length=200)
    short_name          = models.CharField(max_length=50)
    unit                = models.CharField(max_length=20)
    infoods_tagname     = models.CharField(max_length=10) # International standard
    ciqual_id           = models.IntegerField(null=True, blank=True)  # Traceability
    cnf_id              = models.IntegerField(null=True, blank=True)  # Traceability
    enabled             = models.BooleanField(default=True)

    NUT_CALORIES    = "energiekilocalories"

    __preloaded_nutrients = {}

    @classmethod
    def reset(cls):
        cls.__preloaded_nutrients = {}

    @classmethod
    def __preload_nutrients(cls):
        """
        Retrieve and store all nutrient objects
        """
        for nut in cls.objects.all():
            cls.__preloaded_nutrients[nut.key] = nut

    @classmethod
    def get_nut(cls, nut_key):
        """
        Returns a in-memory cached nutrient
        """
        if nut_key not in cls.__preloaded_nutrients:
            cls.__preload_nutrients()
        return cls.__preloaded_nutrients[nut_key]

class FoodNutrient(models.Model):
    """
    Properties of a food
    """
    food                = models.ForeignKey('recipe_mgr.Food', models.CASCADE, editable=False, related_name="food_nutrients")
    nutrient            = models.ForeignKey(Nutrient, models.CASCADE, editable=False)
    amount_per_gram     = models.FloatField()
    std_err             = models.FloatField(null=True, blank=True)
    cooking_method      = models.ForeignKey('recipe_mgr.CookingMethod', models.CASCADE)
    raw_state           = models.ForeignKey('recipe_mgr.RawState', models.CASCADE)

    class Meta:
        unique_together = ('food', 'nutrient', 'cooking_method', 'raw_state')


class NutrientCookAlteration(models.Model):
    """
    How cooking affects nutrient (ratios), compared to no cooking
    """
    cooking_method      = models.ForeignKey('recipe_mgr.CookingMethod', models.CASCADE)
    nutrient            = models.ForeignKey(Nutrient, models.CASCADE)

    # I don't think the ratio can be higher than 100% --  but maybe I'm wrong ?
    ratio               = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

class NutrientRawStateAlteration(models.Model):
    """
    How raw state affects nutrient (ratios), comparing to "Fresh"
    """
    raw_state           = models.ForeignKey('recipe_mgr.RawState', models.CASCADE)
    nutrient            = models.ForeignKey(Nutrient, models.CASCADE)

    # I don't think the ratio can be higher than 100% --  but maybe I'm wrong ?
    ratio               = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(1)])

class CookingMethodEffect(models.Model):
    """
    Global effect of a cooking method applied to a Food category
    """
    food_type           = models.ForeignKey('recipe_mgr.FoodType', models.CASCADE)
    cooking_method      = models.ForeignKey('recipe_mgr.CookingMethod', models.CASCADE)
    weight_ratio        = models.FloatField(validators=[MinValueValidator(0)])



class NutrientPack(models.Model):
    nutrients           = models.ManyToManyField(Nutrient)
    key                 = models.CharField(max_length=20)
    title               = models.CharField(max_length=200)
    description         = models.TextField()
    warning             = models.TextField(blank=True)
    order               = models.IntegerField()
    can_be_unchecked    = models.BooleanField(default=False)