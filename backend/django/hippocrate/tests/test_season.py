
from common.boost                   import to_dict
from common.mock_tools              import fake_today_decorator, fake_redis_cache_decorator

from hippocrate_cpp.core                import set_random_seed
from hippocrate.models.constraints  import UnicityConstraint
from hippocrate.tests               import HpUnidishApiTest

from recipe_mgr.models              import FoodSeasonality, Recipe
from recipe_mgr.seasons             import SeasonManager

class TestHippocrateSeasons(HpUnidishApiTest):
    """
    Test with 3 recipes :
    - 2 that are summer-recipes (with foods defined with a seasonality). 1 published, and 1 personal+validated
    - 1 which is a all-year recipe
    
    Check that, being in winter, there is only the last recipe in the generated planning, despite the UnicityConstraint
    """
    NB_RECIPES          = 3  # 3 recipes, one personal with seasonal food, one non-seasonal published and one published seasonal
    NB_FOODS            = 2  # one food seasonal, one which is not
    NB_MEALSLOTS        = 2
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1

    @fake_today_decorator(2014, 1, 14)  # Deep winter
    @fake_redis_cache_decorator
    def setUp(self):
        self.other_user = self.create_db_user()
        super().setUp()

    def init_food(self, i):
        food = super().init_food(i)
        if i == 0:
            # The first food is only in summer
            FoodSeasonality.objects.create(food=food, start_month=7, end_month=8)
        return food

    def init_problem(self):
        # adding a unicity constraint
        super().init_problem(forced_constraints=[UnicityConstraint(300, [self.defaultDishType.id])])
        
    def init_recipe(self, recipe_number, *args, **kargs):
        recipe = super().init_recipe(recipe_number, *args, **kargs)
        if recipe_number == 0:
            # First recipe is personal and unpublished
            recipe.status = Recipe.STATUS_VALIDATED
        else:
            # The two other ones are redacted by somebody else
            recipe.author = self.other_user
        recipe.save()
        return recipe
    
    def init_recipes(self, *args, **kargs):
        res = super().init_recipes(*args, **kargs)
        SeasonManager.update_all()
        return res
            
    @fake_today_decorator(2014, 1, 14)  # Deep winter
    def test_should_be_with_no_season(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        recipes = []
        for dish_id, recipe_list in to_dict(solution.get_recipes()).items():
            for r in recipe_list:
                recipes.append(r.recipe_id)

        # All the recipes should be the same, because there is only one recipe which is season-compatible
        self.assertEqual(len(set(recipes)), 1)
        self.assertTrue(list(set(recipes))[0], self.recipes[1].id)  # Public recipe, non-seasonal
