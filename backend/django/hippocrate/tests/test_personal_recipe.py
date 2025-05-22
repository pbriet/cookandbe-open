

from common.boost                   import to_dict
from common.mock_tools              import fake_today_decorator, empty_diet_decorator

from hippocrate_cpp.core                import set_random_seed, load_darwin_config
from hippocrate.tests               import HpUnidishApiTest
from hippocrate.tests.test_indicators import FakeMongoHpTable

from planning_mgr.models            import DishRecipe

from recipe_mgr.models              import DishType, Recipe

from mock                           import patch

import optalim.mongo

class TestPersonalRecipeBase(HpUnidishApiTest):
    """
    Testing an optimization with 7 recipes : one personal, and the others public (published)
    The algorithm has to use the personal one to avoid the unicity constraint
    """
    NB_RECIPES          = 7
    NB_FOODS            = 1
    NB_MEALSLOTS        = 7
    NB_SLOTS_PER_DAY    = 1
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1
    
    # One recipe is published, the other is the following:
    OTHER_RECIPE_STATUS = None

    def init_foods(self):
        # Only one DishType used (full course, for which we encourage unicity)
        self.defaultDishType = self.create_db_dishtype(DishType.DT_FULL_COURSE)
        super().init_foods(False)
        
    def init_recipe(self, recipe_number, *args, **kargs):
        recipe = super().init_recipe(recipe_number, *args, **kargs)
        if recipe_number == 0:
            # The first recipe is personal
            recipe.name = "MINE"
            recipe.status = self.OTHER_RECIPE_STATUS
            recipe.author = self.user
            recipe.save()
        return recipe
    
    @fake_today_decorator()
    @empty_diet_decorator
    def optimize_and_get_nb_recipes(self):
        """
        Generates a planning, and returns the number of different recipes
        """
        set_random_seed(42)
        
        # Generate a planning and get suggestions
        response = self._suggest_through_api()
        
        # Retrieving the DishRecipes
        recipes = set()
        for dish_recipe in DishRecipe.objects.all():
            recipes.add(dish_recipe.recipe_id)
        return len(recipes)
        

class TestPersonalRecipeShouldBeUsed(TestPersonalRecipeBase):
    # The other recipe is validated, it has to be included in the solution to avoid unicity
    OTHER_RECIPE_STATUS = Recipe.STATUS_VALIDATED

    def test_must_have_all_recipes(self):
        self.assertEqual(self.optimize_and_get_nb_recipes(), 7)
        
        @fake_today_decorator()
        @empty_diet_decorator
        def check_indicators():
            
            # Testing that personal recipes work with indicators
            response = self.client.get('/api/user/%s/indicators/%s' % (self.user.id, self.days[0].date))
            
            for day in self.days :
                fake_hp_table = FakeMongoHpTable()
                with patch.object(optalim.mongo.Mongo, 'hp_table', lambda x: fake_hp_table):
                    response = self.client.get('/api/user/%s/day/%s/indicators' % (self.user.id, day.date))
                    self.assertEqual(response.status_code, 200)
        
        check_indicators()

class TestNonValidatedRecipeShouldntBeUsed(TestPersonalRecipeBase):
    # The other recipe is a work in progress (not saved)
    # Don't include it, even if there is unicity
    OTHER_RECIPE_STATUS = Recipe.STATUS_CREATING

    def test_must_have_six_recipes(self):
        self.assertEqual(self.optimize_and_get_nb_recipes(), 6)
