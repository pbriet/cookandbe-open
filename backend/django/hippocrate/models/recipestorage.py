"""
This files stores some global variables containing the recipe data (recipes with calculated nutrients)
"""

from collections                import defaultdict
from django.core.cache          import cache

from hippocrate.models.recipe   import RecipeDataBuilder

from optalim.settings           import PRELOAD_RECIPES, TESTING

from recipe_mgr.models          import Recipe, FoodTag
from recipe_mgr.seasons         import SeasonManager

import time
from optalim.log import logger

class RecipeStorageNotInitialized(Exception):
    def __str__(self):
        return "MainRecipeStorage is not ready"


class MainRecipeStorage(object):
    __ready    = False
    __public   = {} # Recipe id -> Recipe data, published recipes only

    @classmethod
    def set_ready(cls, value=True):
        cls.__ready = value

    @classmethod
    def iter_stored_recipe_ids(cls):
        yield from cls.__public.keys()

    @classmethod
    def published_recipes(cls, filter_season=False):
        if not cls.__ready:
            raise RecipeStorageNotInitialized()
        if filter_season:
            seasonal_ids = SeasonManager.get_cached_seasonal_recipe_ids()
            if seasonal_ids is None:
                assert TESTING
                logger.warning("no seasonality cache in test : ignoring")
                return cls.__public.values()
            return [cls.get(s_id) for s_id in seasonal_ids]
        return cls.__public.values()

    @classmethod
    def get(cls, recipe_id):
        """
        Returns a RecipeData for a given recipe id :
        - from the memory if available (published recipe only)
        - otherwise, from the cache if available
        - otherwise, by calculating it (and storing it in the cache)
        """
        # Returns from the stored values if available
        if recipe_id in cls.__public:
            return cls.__public[recipe_id]
        # Non-published recipe ? Try to retrieve it from the cache
        res = RecipeDataBuilder().get_or_build_many([recipe_id])[0]
        if res.status == Recipe.STATUS_PUBLISHED:
            logger.warning("Published recipe not in MainRecipeStorage.__public : you should restart the server")
        return res

    @classmethod
    def init_indexer(cls):
        """
        Initialize the RecipeDataIndexer, by providing all the data keys required
        """
        RecipeDataBuilder().init_indexer()

    @classmethod
    def initialize(cls, rdata_list=None, force=False, reinit_cache=False):
        """
        If the index hasn't been initialized yet,
        fill it with RecipeData
        """
        cls.set_ready(False)
        cls.init_indexer()
        cls.__public, cls.__season = {}, {}
        if not force and not PRELOAD_RECIPES:
            cls.set_ready(True)
            logger.info("PRELOAD_RECIPES=False, recipes won't be loaded in memory")
            return
        logger.info("INITIALIZING GLOBAL RECIPE STORAGE...")
        start_t = time.time()
        if rdata_list is None:
            # Recipe ids to retrieve
            recipe_ids = [recipe.id for recipe in Recipe.objects.only("id").filter(status__gte = Recipe.STATUS_PUBLISHED)]
            rdata_list = RecipeDataBuilder().get_or_build_many(recipe_ids)
            rdata_list = sorted(rdata_list, key=lambda x: x.recipe_id)
            init_taste_recipes_cache(rdata_list)
        for rdata in rdata_list:
            cls.__public[rdata.recipe_id] = rdata

        cls.set_ready(True)
        logger.info("GLOBAL RECIPE STORAGE LOADED IN %ss" % round(time.time() - start_t, 1))

def _build_rdata(rdata_list):
    # From a Python list of RecipeData, builds a RecipeDataVector (C++ compliant)
    if type(rdata_list) is RecipeDataVector:
        return rdata_list
    res = RecipeDataVector()
    for rdata in rdata_list:
        res.append(rdata)
    return res

def init_taste_recipes_cache(rdata):
    """
    From a list of recipe data, init in the cache the dictionnary :
    { food_tag_id:recipe_count }

    I.e. the number of recipes that match a given food_tag
    """
    food_tag_recipes = defaultdict(list)

    for recipe_data in rdata:
        for food_tag_id in recipe_data.food_tag_ids:
            food_tag_recipes[food_tag_id].append(recipe_data.recipe_id)

    FoodTag.cache_recipes(dict(food_tag_recipes))
