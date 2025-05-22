# -*- coding: utf-8 -*-
from django.db                  import models
from django.core.cache          import cache
from django.core.validators     import MaxValueValidator, MinValueValidator
from django.dispatch            import receiver

from collections                import defaultdict

from optalim.settings           import TESTING
from common.model               import NamedModel, AutoUrlKeyModel, enable_auto_url_key, auto_delete_file
from nutrient.models            import FoodNutrient
from user_mgr.models            import User
from location_mgr.models        import Location

import copy
from optalim.log import logger

class FoodSource(NamedModel, models.Model):
    """
    Where do the food / nutrients come from?  CNF/CIQUAL/...
    """
    name                = models.CharField(max_length=30)
    copyright_info      = models.TextField()

class FoodType(NamedModel, models.Model):
    """
    Type of food used by hippocrate to compute nutrient alterations
    """
    name                = models.CharField(max_length=200)
    source              = models.ForeignKey(FoodSource, models.PROTECT, null=True, blank=True)
    hierarchy_code      = models.CharField(max_length=10, null=True, blank=True) # '23', '23.5' (sub-category of 23)
    fresh_expiry        = models.IntegerField(null=True, blank=True, default=None) # Number of days before fresh food expire (overriden by Food.fresh_expiry)
    usually_stored      = models.BooleanField(default=False) # Indicates if the food should be added in the shopping list by default

@enable_auto_url_key
@auto_delete_file('photo')
class FoodTag(NamedModel, AutoUrlKeyModel, models.Model):
    """
    Hierarchic categories of food objects
    """
    name                = models.CharField(max_length=200)
    children            = models.ManyToManyField("FoodTag", related_name="parents")
    can_be_disliked     = models.BooleanField(default=True)
    photo               = models.ImageField(upload_to='food_tag/photo', null=True)
    foods               = models.ManyToManyField("Food", through="FoodTagSet", related_name="food_tags")

    def cached_parents_ids(self, none_if_not_existing=False):
        res = cache.get('food_tag_parents_%i' % self.id)
        if res is None and not none_if_not_existing:
            logger.warning('No parents for food tag %s in cache. The server must be restarted' % self.name)
            return set()
        return res

    def cache_parents_ids(self, value):
        cache.set('food_tag_parents_%i' % self.id, value, None)

    @staticmethod
    def cache_recipes(recipe_ids):
        cache.set('food_tag:recipes', recipe_ids, None)

    @staticmethod
    def cached_recipes():
        return cache.get('food_tag:recipes')

    def get_children(self, including_self=False):
        """
        Returns the list of all the children hierarchy of a given food_tag
        """
        res = set()
        for food_tag in self.children.all():
            res.add(food_tag)
            res = res.union(food_tag.get_children())
        if including_self:
            res.add(self)
        return res

    @property
    def photo_url(self):
        if not self.photo:
            return None
        return self.photo.url

class RawState(NamedModel, models.Model):
    """
    Initial state of raw food (frozen, canned)
    """
    name                = models.CharField(max_length=50)

    @classmethod
    def fresh_id(cls):
        if not hasattr(cls, '__fresh_id') or cls.__fresh_id is None:
            cls.__fresh_id = RawState.objects.get(name="frais").id
        return cls.__fresh_id

    @classmethod
    def clear_cached(cls):
        cls.__fresh_id = None

class Food(NamedModel, models.Model):
    """
    Main object for food
    """
    parent              = models.ForeignKey("Food", models.PROTECT, null=True, blank=True)  # Is this food a specific variety of another food?
    food_source         = models.ForeignKey(FoodSource, models.PROTECT, null=True, blank=True)
    name                = models.CharField(max_length=150)
    full_name           = models.CharField(max_length=200)
    enabled             = models.BooleanField(default=True)
    type                = models.ForeignKey(FoodType, models.PROTECT, related_name="foods")
    shopping_category   = models.ForeignKey("shopping_mgr.ShoppingCategory", models.PROTECT)
    tags                = models.ManyToManyField(FoodTag, through='FoodTagSet')
    original            = models.CharField(max_length=50, null=True, blank=True) # Ids in the source database  (CIQUAL, CNF, ...) --  for future traceability
    has_nutrients       = models.BooleanField(default=True)  # Must have nutrients
    fresh_expiry        = models.IntegerField(null=True, blank=True, default=None) # Number of days before fresh food expire (overrides FoodType.fresh_expiry)

    # Default values used when creating an ingredient
    default_conversion      = models.ForeignKey("FoodConversion", models.SET_NULL, null = True, default = None, related_name = "default_foods")
    default_raw_state       = models.ForeignKey("RawState", models.SET_NULL, null = True, default = None)
    default_cooking_method  = models.ForeignKey("CookingMethod", models.SET_NULL, null = True, default = None)

    def available_raw_states(self):
        """
        Returns the RawStats that can be applied to this food  (through FoodNutrient)
        """
        raw_states_ids = FoodNutrient.objects.filter(food_id=self.id).values('raw_state').distinct()
        return RawState.objects.filter(id__in=raw_states_ids)

    def available_cooking_methods(self):
        """
        Returns the CookingMethods that can be applied to this food  (through FoodNutrient)
        """
        cooking_methods_ids = FoodNutrient.objects.filter(food_id=self.id).values('cooking_method').distinct()
        return CookingMethod.objects.filter(id__in=cooking_methods_ids)

class FoodTagSet(models.Model):
    """
    Used to add hierarchic categories (meat > red meat) to food objects
    """
    food                = models.ForeignKey(Food, models.CASCADE, related_name="tagsets")
    tag                 = models.ForeignKey(FoodTag, models.CASCADE)
    # Indicates if the tag concerns a component of the food and not the food itself.
    # Example : an apple turnover contains apple but is not an apple. So for the "tag" apple, "component" will be True.
    component           = models.BooleanField(default = False)

class FoodSeasonality(models.Model):
    """
    Specifying a season where the food is available in a given location.
    By default it is _always_ available
    """
    food            = models.OneToOneField(Food, models.CASCADE, related_name="season")
    start_month     = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    end_month       = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])

    def valid_monthes(self):
        """
        Returns the list of valid monthes (integers)
        """
        if self.end_month > self.start_month:
            return list(range(self.start_month, self.end_month + 1))
        # New year is within the validity period
        return list(range(1, self.end_month + 1)) + list(range(self.start_month, 13))

class CookingMethod(NamedModel, models.Model):
    """
    Way of cooking (fried, raw, boiled, ...)
    """
    name = models.CharField(max_length=200)

class FoodConversion(models.Model):
    """
    Way of converting a food in something else than grams
    """
    food                = models.ForeignKey(Food, models.CASCADE, db_index=True, related_name='conversions')
    unit                = models.CharField(max_length=200)
    unit_plural         = models.CharField(max_length=200)
    value               = models.FloatField()
    shopping_compatible = models.BooleanField(default=True) # Is this a valid conversion for the shopping list
    splittable          = models.BooleanField(default=True) # Can this conversion be used with float values?
    loss_coeff          = models.FloatField(default = 0, # Percentage which is not eaten (e.g. banana peel)
                                            validators=[MinValueValidator(0),
                                                        MaxValueValidator(1)])

class DishType(NamedModel, models.Model):
    """
    Starter, first course, main course, dessert, full-meal, ...
    """
    name                = models.CharField(max_length = 64)
    system              = models.BooleanField(default = False)
    standard_calories   = models.IntegerField(null=True)  # What is the standard calories input for this dish_type
    monotonous          = models.BooleanField(default = False) # If true, try to have only 1 recipe for all the dishes
    # speciality          = models.ForeignKey(Speciality)

    DT_BREAKFAST_BASE    = "Petit déjeuner (base)"
    DT_STARTER           = "Entrée"
    DT_MAIN_COURSE       = "Plat principal"
    DT_FULL_COURSE       = "Plat complet"
    DT_SIDE              = "Accompagnement"
    DT_CHEESE            = "Fromage"
    DT_DESSERT           = "Dessert"
    DT_SNACK             = "Snack"
    DT_SNACK_SALTED      = "Snack salé"
    DT_SNACK_SWEET       = "Snack sucré"
    DT_BEVERAGE          = "Boisson"
    DT_BEVERAGE_HOT      = "Boisson chaude"
    DT_BEVERAGE_COLD     = "Boisson froide"
    DT_MILKY             = "Laitage"
    DT_FRUIT             = "Fruit"
    DT_BREAD             = "Pain"
    DT_EXTERNAL          = "Extérieur"
    DT_CUSTOM            = "Personnalisé"

    default_dish_keys = (DT_BREAKFAST_BASE, DT_STARTER, DT_MAIN_COURSE,DT_FULL_COURSE,
                         DT_SIDE, DT_CHEESE, DT_DESSERT, DT_SNACK, DT_SNACK_SALTED,
                         DT_SNACK_SWEET, DT_BEVERAGE, DT_BEVERAGE_COLD, DT_BEVERAGE_HOT,
                         DT_MILKY, DT_FRUIT, DT_BREAD, DT_EXTERNAL, DT_CUSTOM)

    __preloaded_dish_types = {}

    # Dictionnary {dish_type_id -> sub_dish_type_ids}
    CACHED_SUB_DTS = defaultdict(list)

    def has_static_ratio(self):
        """
        If True, ratio is and _must be_ always one in the DishRecipes
        """
        return self.name in (self.DT_CUSTOM, self.DT_EXTERNAL)

    def is_activated_by_default(self):
        return self.name in (self.DT_MAIN_COURSE, self.DT_FULL_COURSE, self.DT_SIDE)

    @classmethod
    def reset(cls):
        cls.__preloaded_dish_types = {}
        cls.CACHED_SUB_DTS = defaultdict(list)

    @classmethod
    def __preload_dish_types(cls):
        """
        Retrieve and store some dish type objects
        (classics)
        """
        per_name = dict((dt.name, dt) for dt in cls.objects.all())

        for dish_type_name in cls.default_dish_keys:
            dish = per_name[dish_type_name]
            cls.__preloaded_dish_types[dish_type_name] = dish

    @classmethod
    def get_dt(cls, dt):
        """
        Returns a DishType object from one of the DT_* options
        DishType.get_dt(DishType.DT_DESSERT)
        """
        if dt not in cls.__preloaded_dish_types:
            cls.__preload_dish_types()
        return cls.__preloaded_dish_types[dt]


    def _get_sub_dishtype_ids(self):
        """
        If this is an aggregated dish type, returns a list of sub dishtype ids
        THIS METHOD CACHES ALL THE VALUES AT FIRST CALL
        """
        if len(self.CACHED_SUB_DTS) == 0:
            for agg in DishTypeAggregation.objects.all():
                self.CACHED_SUB_DTS[agg.master_dish_type_id].append(agg.sub_dish_type_id)
            for key in self.CACHED_SUB_DTS.keys():
                self.CACHED_SUB_DTS[key].sort()

        return self.CACHED_SUB_DTS[self.id]

    sub_dishtype_ids = property(_get_sub_dishtype_ids)

class DishTypeAggregation(models.Model):
    """
    Define a given dish_type_id as an aggregation of several subsidiary dish_type_ids.

    Example: Lasagna will be of type "full dish", aggregation of "side dish" and "main dish" types.
    """
    master_dish_type    = models.ForeignKey(DishType, models.CASCADE, related_name="aggregations_as_master")
    sub_dish_type       = models.ForeignKey(DishType, models.CASCADE, related_name="aggregations_as_sub")

    def __str__(self):
        return self.master_dish_type.name + ":" + self.sub_dish_type.name

class DishTypeUnion(models.Model):
    """
    Define a given dish_type id is either one or another dish_type_id
    Example: a drink is either a "cold drink" or a "hot drink"
    """
    master_dish_type    = models.ForeignKey(DishType, models.CASCADE, related_name="unions_as_master")
    sub_dish_type       = models.ForeignKey(DishType, models.CASCADE, related_name="unions_as_sub")

    def __str__(self):
        return self.master_dish_type.name + ":" + self.sub_dish_type.name

@enable_auto_url_key
class RecipeTag(NamedModel, AutoUrlKeyModel, models.Model):
    """
    Tag of recipes (meat, meat in sauce, ...)
    """
    name        = models.CharField(max_length=200)
    parent      = models.ForeignKey("RecipeTag", models.PROTECT, null=True, blank=True)

@enable_auto_url_key
@auto_delete_file('photo')
class Recipe(NamedModel, AutoUrlKeyModel, models.Model):
    """
    Main object Recipe
    """
    name                = models.CharField(max_length=200)
    origin              = models.ForeignKey(Location, models.SET_NULL, null=True, blank=True)
    author              = models.ForeignKey(User, models.CASCADE, related_name="written_recipes")
    price               = models.IntegerField()
    prep_minutes        = models.IntegerField(default=15)
    rest_minutes        = models.IntegerField(default=0)
    cook_minutes        = models.IntegerField(default=15)
    difficulty          = models.IntegerField()
    copyright_free      = models.BooleanField(default=False) # If True, doesn't belong to Optalim
    source_url          = models.CharField(max_length=200, null=True, blank=True)  # Where does it come from
    nb_people           = models.IntegerField() # For how many people this recipe was _written_
                                                # WARNING, ingredients are always stored in a per-person basis
    dish_types          = models.ManyToManyField(DishType, through='RecipeDishType')
    internal            = models.BooleanField(default = False) # Won't be accessible through searches
    tags                = models.ManyToManyField(RecipeTag)
    ustensils           = models.ManyToManyField("Ustensil")
    summary             = models.TextField(null = True)
    photo               = models.ImageField(upload_to='recipe/photo', null=True)
    auto_photo          = models.BooleanField(default=True) # Is the photo auto-generated ?

    avg_rating          = models.FloatField(null=True)   # Average rating : calculated by a job
    nb_ratings          = models.IntegerField(default=0) # Nb ratings : calculated by a job

    perceived_healthy   = models.BooleanField(default=True)

    STATUS_CREATING     = 0 # Non validée par l'utilisateur
    STATUS_VALIDATED    = 1 # Validée par l'utilisateur
    STATUS_REVIEWING    = 2 # !!!   UNUSED  !!! ===> Demande de publication auprès de l'équipe
    STATUS_PUBLISHED    = 3 # Publiée par l'équipe
    STATUS_DICT = {"creating" : STATUS_CREATING,  "validated": STATUS_VALIDATED,
                   "reviewing": STATUS_REVIEWING, "published": STATUS_PUBLISHED}

    status              = models.IntegerField(default = STATUS_CREATING)

    # New way of publishing recipes : admins are browsing through private recipes to
    # find which ones are worthy being duplicated or not
    # The following attributes is slighlty conflicting with STATUS_REVIEWED, which is unused now
    reviewed            = models.BooleanField(default=False)

    # Some dates
    creation_date       = models.DateTimeField(auto_now_add = True)
    modification_date   = models.DateTimeField(auto_now = True)
    publication_date    = models.DateTimeField(null = True)
    publisher           = models.ForeignKey(User, models.PROTECT, null = True, default = None, related_name = "publications")

    # Attributes that should not be changed by users
    SYSTEM_ATTRIBUTES = ("publisher", "publication_date", "modification_date", "author", "creation_date")

    @property
    def photo_url(self):
        if not self.photo:
            return None
        return self.photo.url

    @property
    def is_published(self):
        return self.status >= self.STATUS_PUBLISHED

    def is_custom(self):
        dish_types = list(self.dish_types.all())
        return len(dish_types) == 1 and dish_types[0].name == DishType.DT_CUSTOM

    def clear_cached(self):
        """
        Remove the RecipeData from the cache.
        Nutrient values will be recalculated at the next hippocrate call
        """
        cache.delete('recipe:data:%i' % self.id)

    @staticmethod
    def clone(original_recipe):
        # Retrieving a copy
        recipe = copy.copy(original_recipe)
        # Erasing id to generate new object
        recipe.pk = None
        recipe.save()
        assert recipe.id is not None
        # Copying the photo
        if original_recipe.photo:
            if original_recipe.photo.file is None:
                recipe.photo = None
                recipe.save()
            else:
                recipe.photo = copy.copy(recipe.photo)
                if str(original_recipe.id) in original_recipe.photo.name:
                    photo_filename = original_recipe.photo.name.replace("%s" % original_recipe.id, "%s" % recipe.id)
                else:
                    photo_filename = original_recipe.photo.name[:-4] + '_%i.jpg' % recipe.id
                photo_filename = photo_filename.replace("recipe/photo", "")
                recipe.photo.save(photo_filename, original_recipe.photo, save=True)

        # Cloning simple many2many attributes
        recipe.tags.add(*(original_recipe.tags.all()))
        recipe.ustensils.add(*(original_recipe.ustensils.all()))
        # Cloning advanced many2many attributes
        for ingredient in original_recipe.ingredients.all():
            Ingredient.clone(recipe, ingredient)
        for instruction in original_recipe.instructions.all():
            RecipeInstruction.objects.create(recipe = recipe, text = instruction.text)
        for dish_type in original_recipe.dish_types.all():
            RecipeDishType.objects.create(recipe = recipe, dish_type = dish_type)
        return recipe


@receiver(models.signals.post_delete, sender = Recipe)
def delete_image_when_delete_recipe(sender, instance, *args, **kwargs):
    instance.photo.delete(False)


class RecipeRating(models.Model):
    """
    User ratings and comments on a given recipe
    """
    class Meta:
        unique_together = ('recipe', 'user',)

    user                = models.ForeignKey(User, models.CASCADE, related_name="recipe_ratings")
    recipe              = models.ForeignKey(Recipe, models.CASCADE, related_name="ratings")
    rating              = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment             = models.TextField(null=True, blank=True)
    moderated_at        = models.DateTimeField(null=True, blank=True)
    moderator           = models.ForeignKey(User, models.PROTECT, null=True)
    created_at          = models.DateTimeField(auto_now_add = True)

"""
class RecipeReview(models.Model):
    reviewer            = models.ForeignKey(User)
    recipe              = models.ForeignKey(Recipe)
    rating              = models.IntegerField()
    description         = models.IntegerField()
"""

class RecipeInstruction(models.Model):
    recipe              = models.ForeignKey(Recipe, models.CASCADE, related_name = "instructions")
    text                = models.TextField(blank=True)

class Ingredient(models.Model):
    """
    Part of a recipe
    Quantity for _one_ person (standard)

    The grams stored are relative to the default_conversion, i.e. it is without applyling loss coefficient
    e.g. "1 banana" = 100g, but 80g once peeled. 100 is the value stored.
    """
    food                = models.ForeignKey(Food, models.PROTECT)
    grams               = models.FloatField(validators=[MinValueValidator(0)])
    recipe              = models.ForeignKey(Recipe, models.CASCADE, related_name='ingredients')
    default_conversion  = models.ForeignKey(FoodConversion, models.PROTECT, related_name='ingredients') # Conversion used when creating the recipe
    raw_state           = models.ForeignKey(RawState, models.PROTECT)
    cooking_method      = models.ForeignKey(CookingMethod, models.PROTECT)
    previously_cooked   = models.BooleanField(default=False) # Is the food already pre-cooked  (fried, or boiled, or...)

    # Returns the ingredient quantity post-loss  (see FoodConversion)
    def get_grams_without_loss(self):
        if not hasattr(self, '__grams_without_loss'):
            self.__grams_without_loss = self.grams * (1 - self.default_conversion.loss_coeff)
        return self.__grams_without_loss

    grams_without_loss  = property(get_grams_without_loss)

    def get_best_conversions(self, ratio, nb_conversions=2, shopping_compatible_only=False):
        """
        Given a ratio, returns the best conversions for this ingredient
        """
        options = []
        for conversion in self.food.conversions.all():
            if shopping_compatible_only and not conversion.shopping_compatible:
                continue
            options.append(evaluate_conversion(conversion, self.grams * ratio, self.default_conversion))
        return sorted(options, key=lambda x: x['score'])[:nb_conversions]

    def __unicode__(self):
        return '%i grams of %s' % (self.grams, self.food.name)

    @staticmethod
    def clone(new_recipe, original_ingredient):
        # Retrieving a copy
        ingredient = copy.copy(original_ingredient)
        # Erasing id to generate new object
        ingredient.pk = None
        # Replacing recipe
        ingredient.recipe_id = new_recipe.id
        ingredient.save()
        return ingredient

class RecipeDishType(models.Model):
    """
    For which meal types a recipe is valid
    """
    recipe      = models.ForeignKey(Recipe, models.CASCADE)
    dish_type   = models.ForeignKey(DishType, models.CASCADE)

    class Meta:
        unique_together = ('recipe', 'dish_type',)

class UstensilCategory(NamedModel, models.Model):
    name            = models.CharField(max_length = 64)

class Ustensil(NamedModel, models.Model):
    """
    Tool for cooking
    """
    name            = models.CharField(max_length=200)
    category        = models.ForeignKey(UstensilCategory, models.PROTECT)
    default_check   = models.BooleanField(default=False)

class CookbookRecipe(models.Model):
    """
    Recipe added in a user cookbook
    """
    user            = models.ForeignKey(User, models.CASCADE, related_name="cookbook_recipes")
    recipe          = models.ForeignKey(Recipe, models.CASCADE, related_name="cookbook_selections")
    created_at      = models.DateTimeField(auto_now_add = True)

    class Meta:
        unique_together = ('user', 'recipe')

from recipe_mgr.helpers     import evaluate_conversion