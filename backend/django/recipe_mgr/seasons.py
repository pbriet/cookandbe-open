from django.core.cache      import cache

from common.date            import today

from optalim.settings       import TESTING

from recipe_mgr.models      import Recipe, FoodSeasonality, RawState

from optalim.log import logger

class SeasonManager(object):

    @classmethod
    def load_food_seasonality(cls, force=False):
        """
        Preload from the database all the food seasonalities
        """
        if not force and hasattr(cls, '__food_seasons'):
            return
        this_day = today()
        # Food id -> is this a season for this food
        cls.__food_seasons = {}
        for food_season in FoodSeasonality.objects.all():
            cls.__food_seasons[food_season.food_id] = this_day.month in food_season.valid_monthes()

    @classmethod
    def update_recipe_value(cls, recipe):
        """
        Calculate whether a recipe is seasonal or not, stores it in the cache and returns the boolean (True = seasonal)
        """
        cls.load_food_seasonality()
        seasonal = True
        for ingredient in recipe.ingredients.filter(raw_state_id=RawState.fresh_id()):
            if not cls.__food_seasons.get(ingredient.food_id, True):
                # Recipe contains a non-seasonal ingredient
                seasonal = False
                break

        cache.set('recipe:seasonality:%i' % recipe.id, seasonal, None)
        return seasonal

    @classmethod
    def is_seasonal(cls, recipe_id, update_if_missing=False):
        """
        From a recipe id, returns True if it's seasonal
        """
        res = cache.get('recipe:seasonality:%i' % recipe_id)
        if res is None and update_if_missing:
            return cls.update_recipe_value(Recipe.objects.prefetch_related('ingredients__food').get(pk=recipe_id))
        return res

    @classmethod
    def seasonality_dict(cls):
        """
        Returns a dictionnary of all recipes : {recipe_id: boolean}
        """
        # recipe:seasonality:<recipe_id> contains a boolean whether it's seasonal or not
        stored_recipe_keys = cache.keys('recipe:seasonality:*')
        stored_recipes = dict((int(key.replace('recipe:seasonality:', '')), value) for key, value in cache.get_many(stored_recipe_keys).items())
        return stored_recipes

    @classmethod
    def get_cached_seasonal_recipe_ids(cls):
        res = cache.get('seasonality:recipe_id_list')
        if res is not None or TESTING:
            return res
        logger.warning("Seasonality is not defined in the cache- Updating on the fly : a connection might hang")
        return cls.update_all()

    @classmethod
    def update_all(cls):
        """
        Update seasonality information for all recipes in the database
        """
        seasonal_recipe_ids = set()

        cls.load_food_seasonality(force=True)
        for recipe in Recipe.objects.filter(internal=False).prefetch_related('ingredients__food').all():
            is_seasonal = cls.update_recipe_value(recipe)
            if is_seasonal and recipe.status >= Recipe.STATUS_PUBLISHED:
                seasonal_recipe_ids.add(recipe.id)

        cache.set('seasonality:recipe_id_list', seasonal_recipe_ids, None)
        return seasonal_recipe_ids