
from collections            import defaultdict
from django.core.cache      import cache

from common.boost           import to_dict, to_list, from_dict, from_list

from hippocrate_cpp.core        import RecipeData as RecipeDataC, LongToDoubleHash, IdVector, DoubleVector
from hippocrate_cpp.core        import RecipeDataIndexer

from nutrient.helpers       import RecipeNutrientCalculator
from nutrient.models        import Nutrient

from optalim.config         import Config

from recipe_mgr.models      import Recipe, FoodTag

from optalim.log import logger

# List of fields to prefetch when loading a recipe from DB to calculate the RecipeData
RECIPE_DATA_PREFETCH = ('ingredients__default_conversion',
                        'dish_types',
                        'ingredients__food__tags',
                        'ingredients__food__food_nutrients')

class RecipeData(RecipeDataC):

    # index in state -> class of value
    _BOOST_DICTS   = {3: LongToDoubleHash} # Foodgrams

    _BOOST_LISTS   = {4: IdVector,
                      5: IdVector,
                      6: IdVector,
                      7: IdVector,
                      8: IdVector,
                      9: IdVector,
                      10: DoubleVector, # Data
                      11: IdVector,# Ustensils
                      14: IdVector} # defined_data_ids


    def __getstate__(self):
        """
        Converts the wrapped vectors/map into python list/dicts, so that it is easily pickable
        """
        to_dump = super().__getstate__()
        res = list(to_dump)
        for i in range(len(res)):
            if i in self._BOOST_DICTS:
                res[i] = to_dict(res[i])
            elif i in self._BOOST_LISTS:
                res[i] = to_list(res[i])
        return tuple(res)

    def __setstate__(self, data):
        """
        Converts back into the wrapped C++ vectors/map
        """
        data = list(data)
        for i, cls in self._BOOST_DICTS.items():
            data[i] = from_dict(data[i], cls)
        for i, cls in self._BOOST_LISTS.items():
            data[i] = from_list(data[i], cls)
        super().__setstate__(tuple(data))

class RdataVisitor(object):
    """
    Class that initialize some data in RecipeData
    """
    def iter_data_keys(self, builder):
        """
        Return all the keys stored in recipe_data
        @warning: Beware of the order, it MUST be the same as store_data
        """
        raise NotImplementedError

    def store_data(self, builder, recipe, rdata):
        """
        Store data in RecipeData
        @warning: Beware of the order, it MUST be the same as iter_data_keys
        """
        raise NotImplementedError

class RdataNutrients(RdataVisitor):
    """
    Initialize nutrients
    """
    def get_nutrients(self):
        return list(Nutrient.objects.filter(enabled=True).order_by('id'))

    def iter_data_keys(self, builder):
        yield from (n.key for n in builder.nutrients)

    def store_data(self, builder, recipe, rdata):
        nutrient_per_id = dict((n.id, n) for n in builder.nutrients)

        nutrients_calculator = RecipeNutrientCalculator(recipe).compute()
        nutrient_values = nutrients_calculator.aggregated_nutrients
        #nutrient_availability = nutrients_calculator.nutrients_data_availability

        for n_id, value in nutrient_values.items():
            if n_id not in nutrient_per_id:
                # This nutrient is not enabled, skip it
                continue
            rdata.add_data(nutrient_per_id[n_id].key, value)

class RdataAttributes(RdataVisitor):
    """
    Initialize RecipeData by copying attributes of Recipe
    """
    ATTRIBUTES = ('price', 'prep_minutes', 'cook_minutes',
                  'rest_minutes', 'difficulty')

    def iter_data_keys(self, builder):
        yield from self.ATTRIBUTES

    def store_data(self, builder, recipe, rdata):
        for attr in self.ATTRIBUTES:
            rdata.add_data(attr, getattr(recipe, attr))

class RdataFoodTags(RdataVisitor):
    """
    Fills the recipeData food tags
    + Calculation of meat/fish  (data)
    """
    PROTEINS_TO_FOODTAG = {"fish": "Poisson",
                           "meat": "Viande"}


    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self._food_tag_cache = None

    def food_tag_id_from_name(self, name):
        if self._food_tag_cache is None:
            self._food_tag_cache = {}
            fts = FoodTag.objects.filter(name__in=self.PROTEINS_TO_FOODTAG.values())
            for ft in fts:
                self._food_tag_cache[ft.name] = ft.id

            for protein_name in self.PROTEINS_TO_FOODTAG.values():
                if protein_name not in self._food_tag_cache:
                    logger.warning("No such food tag for proteins (DISABLED) : %s" % protein_name)
        return self._food_tag_cache.get(name, None)

    def iter_data_keys(self, builder):
        yield from sorted(self.PROTEINS_TO_FOODTAG.keys())

    def store_data(self, builder, recipe, rdata):
        """
        Iterate on recipe ingredient foodtags and check for presence of meat/fish
        """
        food_tag_quantities = self.get_food_tags_quantities(recipe)

        for foodTagId in sorted(food_tag_quantities.keys()):
            rdata.food_tag_ids.append(foodTagId)

        for foodTagId, grams in food_tag_quantities.items():
            if grams >= 100:
                rdata.main_food_tag_ids.append(foodTagId)
            if grams > 30:
                rdata.suggested_food_tag_ids.append(foodTagId)

        # Filling quantity of proteins
        for protein_key, protein_food_tag_name in self.PROTEINS_TO_FOODTAG.items():
            foodTagId = self.food_tag_id_from_name(protein_food_tag_name)
            if foodTagId is None:
                continue
            quantity = food_tag_quantities[foodTagId]
            rdata.add_data(protein_key, quantity)

    def get_food_tags_quantities(self, recipe):
        """
        From a recipe, retrieves all the food tags of each ingredients (including parent food tags)
        @return: {id: quantity}
        """
        # Food tag -> grams
        food_tag_quantities = defaultdict(float)

        for ingredient in sorted(recipe.ingredients.all(), key=lambda x: x.id):
            for foodTag in sorted(ingredient.food.tags.all(), key=lambda x: x.id):
                ingredient_tags = set([foodTag.id])
                ingredient_tags = ingredient_tags.union(foodTag.cached_parents_ids())

                for tag_id in ingredient_tags:
                    food_tag_quantities[tag_id] += ingredient.grams

        return food_tag_quantities

class RecipeDataBuilder(object):

    RECIPE_DATA_VISITORS = [RdataAttributes, RdataNutrients, RdataFoodTags]

    def __init__(self):
        self.nutrients = list(Nutrient.objects.filter(enabled=True).order_by('id'))
        self.visitors = [v() for v in self.RECIPE_DATA_VISITORS]

    def init_indexer(self):
        """
        Initialize the RecipeDataIndexer singleton, that stores the dictionnary
        key -> data_id

        MUST BE CALLED ONCE, AND BEFORE ANY USE OF build_recipe
        """
        indexer = RecipeDataIndexer.getInstance()
        indexer.reset()
        for visitor in self.visitors:
            for key in visitor.iter_data_keys(self):
                indexer.add_to_index(key)

    def build(self, recipe_id, recipe=None, nutrient_values=None):
        """
        Returns a RecipeData object from a recipe_id.
        If recipe is None, retrieving it from the database directly
        @param nutrient_values: used for test purposes

        MUST BE CALLED AFTER init_indexer
        """
        if recipe is None:
            recipe = Recipe.objects.prefetch_related(*RECIPE_DATA_PREFETCH).get(pk=recipe_id)

        recipe_data = RecipeData(recipe.id)
        recipe_data.name = recipe.name
        recipe_data.status = recipe.status
        recipe_data.internal = recipe.internal
        recipe_data.nb_ingredients = len(recipe.ingredients.all())
        recipe_data.perceived_healthy = recipe.perceived_healthy

        recipe_data.allocate_data()
        for visitor in self.visitors:
            visitor.store_data(self, recipe, recipe_data)

        for ingredient in sorted(recipe.ingredients.all(), key=lambda x: x.id):
            # Filling quantity per food
            if ingredient.food_id not in recipe_data.foods:
                recipe_data.foods[ingredient.food_id] = 0
            recipe_data.foods[ingredient.food_id] += ingredient.grams

            # Filling cooking_method_ids
            if ingredient.cooking_method_id not in recipe_data.cooking_method_ids:
                recipe_data.cooking_method_ids.append(ingredient.cooking_method_id)


        dish_types = list(recipe.dish_types.all())
        if recipe.status == Recipe.STATUS_PUBLISHED and len(dish_types) == 0:
            logger.critical("Recipe with no dish_type : %s (%s)" % (recipe.name, recipe.id))
        for dish_type in sorted(dish_types, key=lambda x: x.id):
            recipe_data.dish_type_ids.append(dish_type.id)

        for ustensil in recipe.ustensils.all():
            recipe_data.ustensils.append(ustensil.id)

        return recipe_data


    def get_or_build_many(self, recipe_ids):
        """
        Retrieves from cache or calculate the RecipeData for a list of recipe ids
        WARNING : the result is unordered
        """
        keys = ['recipe:data:%i' % recipe_id for recipe_id in recipe_ids]
        cached_recipes = cache.get_many(keys)
        cached_recipes = dict((recipe.recipe_id, recipe) for recipe in cached_recipes.values())
        uncached_recipe_ids = set(recipe_ids).difference(cached_recipes.keys())
        if len(uncached_recipe_ids):
            logger.info("%i recipes cached / %i to calculate" % (len(cached_recipes), len(uncached_recipe_ids)))

        computed_recipes = {}
        if len(uncached_recipe_ids):
            recipe_count = len(uncached_recipe_ids)
            percent5 = recipe_count // 20
            db_recipes = Recipe.objects.prefetch_related(*RECIPE_DATA_PREFETCH).\
                                        filter(id__in=uncached_recipe_ids)

            # Computing non cached recipes
            recipes_to_cache = {}
            for i, recipe in enumerate(db_recipes):
                if percent5 > 0 and (i + 1) % percent5 == 0:
                    logger.info("%i %%" % (100 * (i + 2) / recipe_count))
                rdata = self.build(recipe.id, recipe)
                recipes_to_cache['recipe:data:%i' % recipe.id] = rdata
                computed_recipes[recipe.id] = rdata

            if len(recipes_to_cache):
                if any([r.is_published for r in db_recipes]):
                    # Contains published recipes, store them in the cache undefinitely
                    timeout = None
                else:
                    # User recipes : store them 1h
                    timeout = 3600
                cache.set_many(recipes_to_cache, timeout)

        return list(cached_recipes.values()) + list(computed_recipes.values())
