
import datetime

from common.boost                       import to_dict

from hippocrate.tests                   import HpUnidishApiTest
from hippocrate.models.recipestorage    import MainRecipeStorage
from hippocrate.models.constraints      import NutrientConstraint, UnicityConstraint
from hippocrate_cpp.core                    import build_solution, load_darwin_config

from nutrient.models                    import Nutrient, FoodNutrient

from optalim.config                     import Config

from planning_mgr.models                import DishRecipe, Dish

from recipe_mgr.models                  import Recipe

from collections                        import defaultdict
import numpy
import sys

class TestNaive(HpUnidishApiTest):
    def test_naive(self):
        self._test_algorithm("solve_naive")
        
    def test_darwin(self):
        self._test_algorithm("solve_darwin")

    def _test_algorithm(self, solve_method):
        print("======== Testing with solve method : '%s'" % solve_method)

        initial_dish_ids = [d.id for d in Dish.objects.all()]

        # Checking that DB is empty at the beginning
        self.assertEqual(self._get_nb_dishes(empty_only=True), self.NB_MEALSLOTS * self.NB_DISHES_PER_MEAL)

        solution = getattr(self.problem, solve_method)()

        dish_id_to_recipes = to_dict(solution.get_recipes())
        # Checking we have the correct number of dish_recipes
        self.assertEqual(self.NB_MEALSLOTS * self.NB_DISHES_PER_MEAL, len(dish_id_to_recipes))

        # Checking we have a recipe for each dish
        self.assertEqual(sorted(dish_id_to_recipes.keys()), sorted(initial_dish_ids))

        # Checking that the recipes are on the right dish type
        for dish_id, recipe_list in dish_id_to_recipes.items():
            dish = Dish.objects.get(pk=dish_id)
            recipe = Recipe.objects.get(pk=recipe_list[0].recipe_id)
            self.assertTrue(dish.dish_type in list(recipe.dish_types.all()))

        # Saving solution in database
        self.problem.save_solution(solution)

        # Checking database content
        self.assertEqual(self._get_nb_dishes(filled_only=True), self.NB_MEALSLOTS * self.NB_DISHES_PER_MEAL)

    def _get_nb_dishes(self, empty_only=False, filled_only=False):
        """
        Return the number of dishes, empty or filled (or either)
        """
        dishes = Dish.objects.filter(meal_slot__day__in=self.problem.days)
        if empty_only:
            dishes = dishes.filter(dishrecipe__isnull = True)
        if filled_only:
            dishes = dishes.filter(dishrecipe__isnull = False)
        return dishes.count()

class TestAvoidMidichloriens(HpUnidishApiTest):
    # 10 recipes, each one with 1 different food
    NB_RECIPES      = 10
    NB_FOODS        = 10

    def init_food_nutrients(self, i, food):
        # High default Midichloriens amount
        amount = 99
        # 3 foods contain a small amount of Midichloriens (expressed per grams)
        if i in (2, 7, 9):
            amount = 1
        FoodNutrient.objects.create(food = food, nutrient = self.midichlorien, amount_per_gram = amount, raw_state = self.raw, cooking_method = self.not_cooked)

    def init_week(self, eaters = None):

        self.day = self.create_db_day()
        # Creating 3 mealslots in one day, each one with one dish  (total of 3 dishes)
        for i in range(3):
            mealType = self.create_db_mealtype()
            mealslot = self.create_db_mealslot(self.day, meal_type = mealType, time = datetime.time(i, 00))
            self.create_db_dish(mealslot, self.defaultDishType, order=0)

        self.days = [self.day]

    def init_problem(self):
        # You should eat no more than 1kg of Midichloriens each day
        # Recipes 2, 7, 9 have 990g each. The others have 1kg per recipe.
        constraint = NutrientConstraint(self.midichlorien, -1, 1000,
                                        daily_tolerance=0,
                                        cost_per_percent_out=100)
        HpUnidishApiTest.init_problem(self, forced_constraints=[constraint, UnicityConstraint(300, [self.defaultDishType.id])])

    def test_darwin(self):
        load_darwin_config(self.get_fixture_path(__file__, "naive_darwin_conf.yml"))
        self._test_algorithm()

    def test_darwin_oriented(self):
        load_darwin_config(self.get_fixture_path(__file__, "darwin_config_oriented.yml"))
        self._test_algorithm()
        
    def _test_algorithm(self):
        profile_ratio = 1.0
        self.reload_recipe_index()

        solution = self._solve_with_no_api()

        # 2, 7 and 9 are the ids of the recipes with low Midichloriens
        # EXPECTED VALUES
        low_midichlorien_recipedata = []
        for recipe_id in MainRecipeStorage.iter_stored_recipe_ids():
            rdata = MainRecipeStorage.get(recipe_id)
            if rdata.get_data_from_key(self.midichlorien.key, profile_ratio) == 100:
                low_midichlorien_recipedata.append(rdata)
        self.assertEqual(len(low_midichlorien_recipedata), 3)

        # Getting score
        score = self.problem.eval(solution)

        print("Score = ", score.total)
        self.assertEqual(score.total, 0)

        result_recipe_ids = sorted([dish_recipe.recipe.id for dish_recipe in self.problem.get_results()])
        self.assertEqual(result_recipe_ids, sorted([r.recipe_id for r in low_midichlorien_recipedata]))



class BaseTestShouldModifyTheCorrectDays(HpUnidishApiTest):
    """
    Test that the algorithms modifies only days :
    - that are current
    - or not validated
    """
    # 2 meals per day (one dish)
    # 8 different recipes
    NB_RECIPES          = 8
    NB_MEALSLOTS        = 8
    NB_DISHES_PER_MEAL  = 1
    NB_SLOTS_PER_DAY    = 2
    
    
    EXPECTED_NB_RECIPES_AT_THE_END = 8  # All different !

    def init_problem(self):
        # A unicity constraint
        HpUnidishApiTest.init_problem(self, forced_constraints=[UnicityConstraint(300, [self.defaultDishType.id])])

    def init_week(self):
        super().init_week()
        self.dishrecipes = []
        # Assign the first recipe to all the dishes
        for dish in self.dishes:
            dr = self.create_db_dishrecipe(dish, self.recipes[0])
            self.dishrecipes.append(dr)
            
    def test_optimize(self):
        """
        By default, all days can be modified.
        check that the unicity works well :)
        """
        solution = self._solve_with_no_api(False)
        recipe_ids = set(self._get_recipe_ids(solution))
        self.assertEqual(len(recipe_ids), self.EXPECTED_NB_RECIPES_AT_THE_END)


class TestAllDaysValidated(BaseTestShouldModifyTheCorrectDays):
    EXPECTED_NB_RECIPES_AT_THE_END = 3  # 2 different on current day, but stille the same otherwise
    """
    All days are validated.
    Only the current day will be modified
    """
    def init_week(self):
        super().init_week()
        for day in self.days:
            day.skipped = False
            day.save()

class TestAllDaysValidatedAndDishRecipeValidated(TestAllDaysValidated):
    EXPECTED_NB_RECIPES_AT_THE_END = 2  # Only one will change : on current day, not validated
    
    def init_week(self):
        super().init_week()
        # Current day is day 1, the two first dishrecipes belong to him
        self.dishrecipes[1].validated = True
        self.dishrecipes[1].save()
        
        
class TestAllDaysValidatedAndDishRecipeForced(TestAllDaysValidated):
    EXPECTED_NB_RECIPES_AT_THE_END = 2  # Only one will change : on current day, not forced by user
    
    def init_week(self):
        super().init_week()
        # Current day is day 1, the two first dishrecipes belong to him
        self.dishrecipes[0].user = self.user
        self.dishrecipes[0].save()