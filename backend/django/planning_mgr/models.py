
from collections                import OrderedDict

from django.db                  import models
from django.core.validators     import MaxValueValidator, MinValueValidator
from django.utils               import timezone

import datetime

from operator                   import attrgetter

from common.date                import tz_aware
from common.model               import NamedModel

from eater_mgr.models           import Eater

from recipe_mgr.models          import DishType
from recipe_mgr.models          import Recipe
from recipe_mgr.models          import RecipeTag, FoodTag

from user_mgr.models            import User

from optalim.log import logger


class MetaPlanning(models.Model):
    """
    Default set of days which will be copied when generating new days
    """
    user                = models.ForeignKey(User, models.CASCADE)
    creation_date       = models.DateTimeField(auto_now_add=True, blank=True)
    modification_date   = models.DateTimeField(auto_now_add=True, blank=True)

    def set_modified(self, time_value=None):
        if time_value is None:
            time_value = timezone.now()
        self.modification_date = time_value
        self.save()

    sorted_days = property(lambda x: sorted(x.days.all(), key=lambda y: y.date))

class Planning(MetaPlanning):
    """
    Block of days on which hippocrate is called,
    and for which indicators are generated
    """
    def start_date(self):
        days = self.days.all()
        return sorted(days, key=attrgetter('date'))[0].date


class Day(models.Model):
    class Meta:
        unique_together = ("date", "user")

    planning            = models.ForeignKey(MetaPlanning, models.CASCADE, related_name="days")
    date                = models.DateField(db_index=True)
    user                = models.ForeignKey(User, models.CASCADE, related_name="days")
    creation_date       = models.DateTimeField(auto_now_add=True, blank=True)
    modification_date   = models.DateTimeField(auto_now_add=True, blank=True)
    skipped             = models.BooleanField(blank=True, null=True)  # False -> Has been created, True -> Has been explicitely skipped
    shopping_list       = models.ForeignKey('shopping_mgr.ShoppingList', models.SET_NULL, null=True, related_name="days")

    weekday = property(lambda x: x.date.weekday())

    @property
    def ordered_meal_slots(self):
        if self.pk is None:
            return []
        return sorted(self.meal_slots.all(), key=lambda y: y.time)

    def is_filled(self):
        """
        Returns True if this day has been filled with recipes
        """
        for meal_slot in self.meal_slots.all():
            if not meal_slot.is_cooked:
                continue
            for dish in meal_slot.dishes.all():
                if not dish.optional and dish.dishrecipe_set.count() == 0:
                    return False
        return True

    def is_validated(self):
        return self.skipped is not None and not self.skipped

    def is_skipped(self):
        return self.skipped is not None and self.skipped

    @staticmethod
    def metaplanning_date(week_day):
        """
        From a weekday [0-6], returns the date of a metaplanning day
        """
        # Important : the metaplanning days are from Jan 1st (a Monday) to Jan 7th (a sunday)
        return tz_aware(datetime.datetime(2007, 1, week_day + 1))

    def requires_update(self, user):
        if user is None:
            user = self.user
        if not self.user.meta_planning:
            return False
        return self.creation_date < self.user.meta_planning.modification_date

class MealPlace(models.Model):
    key                 = models.CharField(max_length = 32)

    def __str__(self):
        return self.key

    def is_external(self):
        return self.key == "away"

class MealType(NamedModel, models.Model):
    key                 = models.CharField(max_length = 16)
    name                = models.CharField(max_length = 32)
    nickname            = models.CharField(max_length = 16)
    dish_types          = models.ManyToManyField(DishType, through = "MealDishOption")
    time                = models.TimeField()
    default_place       = models.ForeignKey(MealPlace, models.CASCADE)
    default_suggest     = models.BooleanField(default = True)  # If False, there will be no suggestion for this meal. Only possible if all the dishrecipes are set and forced.
    static_recipe_options = models.ManyToManyField(Recipe)     # Recipes displayed in a static configuration mode
    force_suggest       = models.BooleanField(default = False) # If True, the meals can only be suggested, not static

class MealDishOption(models.Model):
    meal_type           = models.ForeignKey(MealType, models.CASCADE, related_name="dish_options")
    dish_type           = models.ForeignKey(DishType, models.CASCADE)
    min_budget_check    = models.IntegerField(default = 2, null=True) # Checked in metaplanning if budget > X
    min_speed_check     = models.IntegerField(default = 2, null=True) # Checked in metaplanning if speed > X
    default_optional    = models.BooleanField(default = False)  # True if the dish type can be removed by Darwin as it please
    default_recipe      = models.ForeignKey(Recipe, models.SET_NULL, null=True)  # If not suggested by Optalim, what is the default "generic" recipe

class MealSlot(models.Model):
    """
    Meal of a planning (dinner, lunch, breakfast, ...)
    """
    SPEED_VALIDATORS = [MinValueValidator(1), MaxValueValidator(4)] # From 1 (express) to 4 (any time)

    time                = models.TimeField()
    speed               = models.IntegerField(default=2, validators=SPEED_VALIDATORS)
    day                 = models.ForeignKey(Day, models.CASCADE, related_name="meal_slots")
    budget              = models.IntegerField(default = None, null = True)
    eaters              = models.ManyToManyField(Eater, through='MealSlotEater')
    meal_type           = models.ForeignKey(MealType, models.CASCADE)
    meal_place          = models.ForeignKey(MealPlace, models.CASCADE)
    suggest             = models.BooleanField(default = True)

    ordered_dishes      = property(lambda x: sorted(x.dishes.all(), key=lambda y: y.dish_type_id))

    # Foreach level of speed :
    # - What is the max constraint per meal  (penality)
    # - On the minor dishes  (all except starters, main courses and sides), how to filter recipes
    SPEED_INFOS = OrderedDict((key, value) for key, value in (
        (1, {'max_per_meal':            {'prep_minutes': 10, 'rest_minutes': 5,  'cook_minutes': 15},
             'max_minor_recipe_filter': {'prep_minutes': 2,  'rest_minutes': 0,  'cook_minutes': 0}
            }),
        (2, {'max_per_meal':            {'prep_minutes': 15, 'rest_minutes': 10, 'cook_minutes': 25},
             'max_minor_recipe_filter': {'prep_minutes': 5,  'rest_minutes': 0,  'cook_minutes': 5}
            }),
        (3, {'max_per_meal':            {'prep_minutes': 30, 'rest_minutes': 30, 'cook_minutes': 40},
             'max_minor_recipe_filter': {'prep_minutes': 10, 'rest_minutes': 0,  'cook_minutes': 10}
            }),
        (4, {'max_per_meal':            {'prep_minutes': 60, 'rest_minutes': 60, 'cook_minutes': 120},
             'max_minor_recipe_filter': {'prep_minutes': 15, 'rest_minutes': 20, 'cook_minutes': 30}
            }),
        (5, None) # No limits
    ))

    def _cooking_speed_infos(self):
        return self.SPEED_INFOS[self.speed]

    @classmethod
    def get_speed(cls, recipe):
        for speed, infos in cls.SPEED_INFOS.items():
            if infos is None:
                return speed
            for attrName, minutes in infos['max_per_meal'].items():
                if getattr(recipe, attrName) > minutes:
                    break
            else:
                return speed
        assert False, "Should have found the speed by now... " + str(recipe.__dict__)
        return len(cls.SPEED_INFOS) + 1

    @classmethod
    def get_speed_from_values(cls, prep_minutes, rest_minutes, cook_minutes):
        dico = {'prep_minutes': prep_minutes, 'rest_minutes': rest_minutes,
                'cook_minutes': cook_minutes}
        for speed, infos in cls.SPEED_INFOS.items():
            if infos is None:
                return speed
            for minutes_type, value in infos['max_per_meal'].items():
                if dico[minutes_type] > value:
                    break
            else:
                return speed
        return len(cls.SPEED_INFOS) + 1


    cooking_speed_infos = property(_cooking_speed_infos)
    unlimited_speed     = property(lambda s: s.SPEED_INFOS[s.speed] is None)

    @property
    def is_eaten(self):     return self.meal_place.key != "donoteat"
    @property
    def is_external(self):  return self.meal_place.is_external()
    @property
    def is_cooked(self):    return self.meal_place.key in ("home", "lunchpack")

    @property
    def meal_name(self):
        return self.meal_type.name

    def __str__(self):
        if isinstance(self.ordered_dishes, list):
            # Already a list in a prefetch query
            dishes_str = [str(dish) for dish in self.ordered_dishes]
        else:
            dishes_str = [str(dish) for dish in self.ordered_dishes.all()]
        return ";".join(dishes_str)

class Dish(models.Model):
    """
    Part of a meal (first course, main course, dessert, ...)
    """
    order               = models.IntegerField() # Position of the dish in the meal
    meal_slot           = models.ForeignKey(MealSlot, models.CASCADE, related_name="dishes")
    recipes             = models.ManyToManyField(Recipe, through='DishRecipe')
    dish_type           = models.ForeignKey(DishType, models.CASCADE)  # Can be an aggregated dishtype
    optional            = models.BooleanField(default=False)  # Should this dish always have recipes assigned ?
    activated           = models.BooleanField(default=True) # Is it displayed to the user and included in the shopping list

    def get_ordered_recipes(self):
        drs = DishRecipe.objects.filter(dish=self)
        drs = sorted(drs, key=lambda x: x.order)
        return [dr.recipe for dr in drs]

    def _splitted_dish_type_ids(self):
        """
        Returns the list of dish type ids without aggregations
        """
        sub_dishtype_ids = list(self.dish_type.sub_dishtype_ids)
        if len(sub_dishtype_ids):
            # Le dish type est aggrégé -> récupération des sous-dish types
            return sub_dishtype_ids
        else:
            return [self.dish_type_id]

    # WARNING: using this property might produce low performances, i.e. cancel the effet of a prefetch_related
    ordered_recipes       = property(get_ordered_recipes)

    splitted_dishtype_ids = property(_splitted_dish_type_ids)

    def __str__(self):
        return "Dish (" + str(self.dish_type) + ")"

class DishRecipeFilter(models.Model):
    """
    Applying a recipe filter on one dish
    """
    dish            =   models.ForeignKey(Dish, models.CASCADE, related_name="dish_recipe_filters")
    dish_type       =   models.ForeignKey(DishType, models.CASCADE) # Is applied on this part of the dish only
    recipe_tag      =   models.ForeignKey(RecipeTag, models.CASCADE)

class DishFoodFilter(models.Model):
    """
    Applying a food filter on one dish
    """
    dish            =   models.ForeignKey(Dish, models.CASCADE, related_name="dish_food_filters")
    dish_type       =   models.ForeignKey(DishType, models.CASCADE) # Is applied on this part of the dish only
    food_tag        =   models.ForeignKey(FoodTag, models.CASCADE)

class NotNow(models.Model):
    """
    Saving that a user doesn't want this recipe for the moment
    """
    user            =   models.ForeignKey(User, models.CASCADE, related_name="not_nows")
    recipe          =   models.ForeignKey(Recipe, models.CASCADE)
    created_at      =   models.DateTimeField(auto_now=True)

class MealSlotEater(models.Model):
    """
    Diner taking part in the meal
    """
    meal_slot           = models.ForeignKey(MealSlot, models.CASCADE, related_name="meal_slot_eaters")
    eater               = models.ForeignKey(Eater, models.CASCADE)

class DishRecipe(models.Model):
    """
    Recipe chosen by the planning generator algorithm for a given dish
    """
    # Theoretically, should be models.OneToOneField(Dish), but by doing so Dish.dish_recipe will break if there is not dish (instead of returning null)
    dish                = models.ForeignKey(Dish, models.CASCADE)
    recipe              = models.ForeignKey(Recipe, models.CASCADE)
    ratio               = models.FloatField()
    user                = models.ForeignKey(User, models.SET_NULL, default = None, null = True) # None == Hippocrate
    validated           = models.BooleanField(default = False) # It's been validated by the user
    order               = models.IntegerField(default = 0)  # If multiple recipes in one dish --  order
    fully_filtered      = models.BooleanField(default = True) # Is the DishRecipe compliant to all the filters applied on him ?
    in_shopping_list    = models.BooleanField(default = True) # Dish Recipe is included in the shopping list if it is True and that the dish is activated

    planning = property(lambda x: x.dish.meal_slot.day.planning)

    @staticmethod
    def clone(original_dish_recipe, new_dish):
        # Retrieving a copy
        dish_recipe = DishRecipe.objects.get(pk = original_dish_recipe.id)
        # Erasing id to generate new object
        dish_recipe.pk = None
        dish_recipe.dish = new_dish
        dish_recipe.save()
        return dish_recipe


class FoodProvider(NamedModel, models.Model):
    """
    In prevision of future partnership providing food (eg: vegetable basket)
    """
    name                = models.CharField(max_length = 64)
