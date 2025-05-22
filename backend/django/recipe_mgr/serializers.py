
from rest_framework         import serializers
from rest_framework.fields  import IntegerField
from common.rest            import FlexibleFloatField, SerializerWithCustomFields

from blogs.serializers      import BlogSerializer

from planning_mgr.models    import DishRecipe, MealSlot


from recipe_mgr.helpers     import food_conversions
from recipe_mgr.models      import Food, Recipe, Ingredient, FoodConversion, RecipeRating, CookbookRecipe
from recipe_mgr.models      import FoodType, DishType, CookingMethod, RawState, RecipeTag, FoodSeasonality
from recipe_mgr.models      import Ustensil, UstensilCategory, FoodTag, FoodTagSet, RecipeInstruction


from hippocrate.models.recipestorage    import MainRecipeStorage

import copy

class RecipeRatingSerializer(SerializerWithCustomFields):
    class Meta:
        model = RecipeRating
        exclude = []

    def fill_additional_data(self, rating, result):
        result['username'] = rating.user.first_name
        result['recipename'] = rating.recipe.name

class FoodTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodType
        exclude = []

class FoodTagSerializer(serializers.ModelSerializer):

    class Meta:
        model = FoodTag
        fields = ('name', 'id', 'photo', 'url_key', 'can_be_disliked')

class FoodTagSerializerWithNb(FoodTagSerializer):
    nb_food = IntegerField()
    class Meta:
        model = FoodTag
        fields = FoodTagSerializer.Meta.fields + ('nb_food', )

class FoodSerializer(SerializerWithCustomFields):

    class Meta:
        model = Food
        exclude = []

    def __init__(self, objs=None, with_season=False, **kargs):
        self.with_season = with_season
        super().__init__(objs, **kargs)

    def fill_additional_data(self, food, result):
        if self.with_season:
            try:
                season = food.season
                result['seasonal'] = True
            except FoodSeasonality.DoesNotExist:
                result['seasonal'] = False

class FoodTagSetWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodTagSet
        exclude = []

class FoodTagSetSerializer(serializers.ModelSerializer):
    food    = FoodSerializer()

    class Meta:
        model = FoodTagSet
        exclude = []

class CookingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingMethod
        exclude = []

class RawStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawState
        exclude = []

class IngredientSerializer(serializers.ModelSerializer):
    food = FoodSerializer(read_only=True)

    class Meta:
        model = Ingredient
        exclude = []

class RecipeInstructionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeInstruction
        exclude = []

class NewIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        exclude = []

    def is_valid(self, *args, **kargs):
        self.initial_data = dict(self.initial_data.items())
        from recipe_mgr.views.ingredient import IngredientViewSet
        food_id = self.initial_data.get('food')
        food = Food.objects.prefetch_related('conversions', 'food_nutrients').get(pk = food_id)
        if self.initial_data.get('default_conversion', None) is None:
            self.initial_data['default_conversion'] = IngredientViewSet._get_default_conversion(food)
        if self.initial_data.get('raw_state', None) is None:
            self.initial_data['raw_state'] = IngredientViewSet._get_default_raw_state(food)
        if self.initial_data.get('cooking_method', None) is None:
            self.initial_data['cooking_method'] = IngredientViewSet._get_default_cooking_method(food)
        return super().is_valid(*args, **kargs)


class FoodConversionSerializer(serializers.ModelSerializer):
    value = FlexibleFloatField()
    class Meta:
        model = FoodConversion
        exclude = []

class DishTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DishType
        exclude = []

class RecipeTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeTag
        exclude = []

class UstensilCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UstensilCategory
        exclude = []

class UstensilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ustensil
        exclude = []

# Django Rest framework doesn't handle correctly writable nested attributes
# This should come very soon
# https://github.com/tomchristie/django-rest-framework/issues/395
#
# Using PrimaryKeyRelatedField instead  (which maybe is cleaner after all)

class PartialRecipeSerializer(SerializerWithCustomFields):

    ingredients = serializers.PrimaryKeyRelatedField(read_only=True, many = True)
    ustensils   = serializers.PrimaryKeyRelatedField(read_only=True, many=True, allow_empty = True)
    tags        = serializers.PrimaryKeyRelatedField(read_only=True, many=True, allow_empty = True)

    MIN_MAX = {'price': (1, 5),
               'difficulty': (1, 5),
               'prep_minutes': (0, 240),
               'cook_minutes': (0, 240),
               'rest_minutes': (0, 4000),
               'nb_people': (1, 20)}

    class Meta:
        model = Recipe
        exclude = []

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.with_food_tags = True  # Set of all ingredients food_tags

    def validate(self, attrs):
        for key, minmax in self.MIN_MAX.items():
            if key not in attrs:
                continue
            if attrs[key] < minmax[0] or attrs[key] > minmax[1]:
                raise serializers.ValidationError('%s should be between %s and %s' % (key, minmax[0], minmax[1]))
        return attrs

    def fill_additional_data(self, recipe, result):
        super().fill_additional_data(recipe, result)
        result['speed'] = MealSlot.get_speed(recipe)
        if self.with_food_tags:
            result["food_tags"] = list(MainRecipeStorage.get(recipe.id).food_tag_ids)

class ReviewRecipeSerializer(PartialRecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'id', 'url_key', 'creation_date')

    def fill_additional_data(self, recipe, result):
        super().fill_additional_data(recipe, result)
        result['author'] = {'id': recipe.author.id, 'first_name': recipe.author.first_name}

class QuickRecipeSerializer(PartialRecipeSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'id', 'url_key')

class RecipeIngredientSerializer(object):
    @staticmethod
    def serialize(recipes):
        res = []
        for recipe in recipes:
            item = {}
            for field in ('id', 'name', 'price', 'prep_minutes', 'rest_minutes', 'status',
                          'cook_minutes', 'url_key', 'difficulty', 'nb_people', 'author_id',
                          'avg_rating', 'nb_ratings'):
                item[field] = getattr(recipe, field)
            ingredients = []
            for ingredient in recipe.ingredients.all():
                ingredients.append({'food': {'name': ingredient.food.name}})
            item['ingredients'] = ingredients
            item['photo'] = recipe.photo_url
            item['speed'] = MealSlot.get_speed(recipe)
            res.append(item)
        return res

class FullRecipeSerializer(PartialRecipeSerializer):
    ingredients     = IngredientSerializer(many = True)
    instructions    = RecipeInstructionSerializer(many = True)

class RatioRecipeSerializer(PartialRecipeSerializer):
    """
    Serializer of a recipe, with a ratio.
    Will retrieve :
    * the details of the recipe
    * the name of the ingredients
    * foreach ingredient, the value with the best conversions
    """
    instructions    = RecipeInstructionSerializer(many = True)

    def __init__(self, recipes, ratio = None, include_usage=True, with_blog=False, **kargs):
        super().__init__(recipes, **kargs)
        self.ratio = ratio
        self.include_usage = include_usage
        self.with_blog = with_blog  # If True, requires a select_related('blog') on recipe.author

    def _add_usage(self, recipe, result):
        result["usage"] = len(recipe.dishrecipe_set.all())

    def _add_ingredients(self, recipe, result):
        serialized_ingredients = []
        for ingredient in recipe.ingredients.all():
            grams = ingredient.grams
            if self.ratio is not None:
                # Applying custom ratio
                grams *= self.ratio
            else:
                # Applying recipe native ratio
                grams *= recipe.nb_people

            # If no ratio : Use default conversion, the one that has been used to enter the recipe
            # If custom ratio : test and compare conversions
            best_conversion, basic_conversion = food_conversions(ingredient.food, grams,
                                                             default_conversion=ingredient.default_conversion,
                                                             use_only_default=self.ratio is None)

            serialized_ingredients.append(
               {'name': ingredient.food.name,
                'food_id': ingredient.food_id,
                'food': {'name': ingredient.food.name},
                'grams': grams,
                'raw_state_name': ingredient.raw_state.name,
                'conversions': {'best': best_conversion,
                                'basic': basic_conversion}
                })
        result['ingredients'] = serialized_ingredients
        if self.ratio is not None:
            result['ratio'] = self.ratio
        else:
            result['ratio'] = recipe.nb_people

    def fill_additional_data(self, recipe, result):
        super().fill_additional_data(recipe, result)
        self._add_ingredients(recipe, result)
        if self.include_usage:
            self._add_usage(recipe, result)
        if self.with_blog:
            # requires a select_related('blog') on recipe.author
            blog = recipe.author._state.fields_cache.get('blog')
            if blog:
               result['blog'] = BlogSerializer(blog).data


class CookbookRecipeSerializer(SerializerWithCustomFields):
    class Meta:
        model = CookbookRecipe
        exclude = []
