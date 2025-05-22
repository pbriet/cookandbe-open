
import datetime

from common.boost                               import to_dict
from common.mock_tools                          import fake_ratio_variable

from eater_mgr.ratios                           import RatiosCalculator

from hippocrate_cpp.core                            import build_solution, load_darwin_config
from hippocrate_cpp.core                            import Dish as CppDish
from hippocrate.models.constraints              import NutrientConstraint, UnicityConstraint
from hippocrate.models.problem                  import Problem
from hippocrate.tests                           import HpUnidishApiTest

from nutrient.models                            import FoodNutrient

from optalim.config                             import Config

from planning_mgr.models                        import DishRecipe

from recipe_mgr.models                          import DishType

import eater_mgr.ratios

from collections                                import defaultdict
from mock                                       import patch
import numpy
import sys

def fake_calories_decorator(calories):
    def fake_calc_profile_calories(calculator):
        calculator._profile_calories = defaultdict(lambda: calories)
    def decorator(fcn):
        @patch.object(RatiosCalculator, "_calc_profile_calories", fake_calc_profile_calories)
        def new_fcn(*args, **kargs):
            return fcn(*args, **kargs)
        new_fcn.__name__ = fcn.__name__
        return new_fcn
    return decorator


def fake_profile_ratios_decorator(value):
    def fake_calc_profile_ratios(calculator):
        calculator._calc_profile_calories()
        calculator._profile_ratios = defaultdict(lambda: value)
    def decorator(fcn):
        @patch.object(RatiosCalculator, '_calc_profile_ratios', fake_calc_profile_ratios)
        @patch.object(RatiosCalculator, 'precision_from_nb_eaters', lambda *args, **kargs: 0.5)
        def new_fcn(*args, **kargs):
            return fcn(*args, **kargs)
        new_fcn.__name__ = fcn.__name__
        return new_fcn
    return decorator

class iRatioTest(HpUnidishApiTest):
    # 10 recipes, each one with 1 different food
    NB_RECIPES          = 50
    NB_FOODS            = 50
    NB_DISHES_PER_MEAL  = None # Bypassed
    DISABLE_RATIO_ROUND = False

    def init_dishtypes(self):
        dishTypeInfos = [
            #  Name            standard calories
            ("small dish",     500),
            ("normal dish",    1000),
            ("big dish",       2000),
            ("custom dish",    None)
        ]

        self.dish_types = []
        # Name -> dish_type
        self.dish_type_per_name = dict()
        for name, std_calories in dishTypeInfos:
            dish_type = self.create_db_dishtype(name=name, standard_calories=std_calories)
            self.dish_type_per_name[name] = dish_type
            self.dish_types.append(dish_type)

    def compute_amount_per_gram(self, i):
        if i < 20:
            return 1 # Recipe with 100 midichloriens
        if i < 35:
            return 2 # Recipe with 200 midichloriens
        if i < 45:
            return 5 # Recipe with 500 midichloriens
        return 10 # Recipe with 1000 midichloriens

    def init_food_nutrients(self, i, food):
        """
        Sachant que dans le test :
        - on utilise uniquement des recettes monoingrédients avec 100g/ingrédient
        - le recettes bouclent sur les ingrédients, ils sont donc utilisés chacun NB_RECIPES / NB_FOODS fois
        """
        FoodNutrient.objects.create(food = food, nutrient = self.midichlorien,
                                    amount_per_gram = self.compute_amount_per_gram(i),
                                    raw_state = self.raw, cooking_method = self.not_cooked)

    def init_recipe(self, recipe_number, dish_type, recipe_name = None):
        """
        Creating recipes for each dish_type
        """
        dish_type = self.dish_types[recipe_number % len(self.dish_types)]

        return super().init_recipe(recipe_number, dish_type, recipe_name=recipe_name)

    def init_week(self, eaters = None):

        planning = self.create_db_planning()
        self.days = planning.sorted_days

        # Creating week planning : {weekday : [dish_types] }
        my_week = {
            0 : ["small dish", "normal dish"],  # 500 + 1000  =  1500 kcal   (ratio = 2300/1500 = 1.53).   midi = (100+500)*1.53 = 918
            1 : ["big dish"],                   # 2000 kcal                  (ratio = 2300/2000 = 1.15)    midi = 1000*1.15 = 1150
            2 : ["normal dish"],                # 1000 kcal                  (ratio = 2.3)                 midi = 500*2.3 = 1150
            3 : ["normal dish", "normal dish"], # 1000+1000 = 2000 kcal      (ratio = 1.15)                midi = (500+500) * 1.15 = 1150
            4 : ["small dish"],                 # 500 kcal                   (ratio = 4.6)                 midi = 200*4.6 = 920
            5 : ["big dish", "big dish"],       # 2000*2 = 4000 kcal         (ratio = 0.575)               midi = (1000+1000) * 0.575 = 1150
            6 : ["big dish", "big dish", "big dish"] # 2000*3 = 6000 kcal    (ratio = 0.3833)              midi = (3*1000) * 0.3833 = 1150
        }
        self.mealslots_per_day = defaultdict(list)
        for day_number, dish_type_names in my_week.items():
            for i, dt_name in enumerate(dish_type_names):
                dish_type = self.dish_type_per_name[dt_name]
                self.init_meal_slot(i, dish_type, day_number)


    def init_meal_slot(self, meal_slot_number, dish_type, day_number, with_eaters=None):
        mealslot = self.create_db_mealslot(self.days[day_number], with_eaters=with_eaters)
        self.mealslots_per_day[day_number].append(mealslot)
        self.create_db_dish(mealslot, dish_type, order = 0)

    @fake_profile_ratios_decorator(1)
    @fake_calories_decorator(2300)
    def setUp(self):
        self.init_dishtypes()
        super().setUp()


    @fake_ratio_variable('ENABLE_DAY_RATIO_SECURITY', False)
    def init_problem(self):
        round_to_closest = eater_mgr.ratios.round_to_closest
        if self.DISABLE_RATIO_ROUND:
            round_to_closest = lambda x, *args: x

        with patch.object(eater_mgr.ratios, 'round_to_closest', round_to_closest):
            #original_set_profile_ratio = CppDish.set_profile_ratio
            # You should eat the average quotat of Midichloriens each day
            print("Expected daily midichloriens [%i : %i]" % (800, 1200))
            constraint = NutrientConstraint(self.midichlorien,
                                            800,
                                            1200,
                                            daily_tolerance = 0,
                                            cost_per_percent_out = 100)

            self.problem = Problem(self.days, enable_diet=False, forced_constraints=[constraint], current_day=self.days[0])

class TestSingleProfileMealRatios(iRatioTest):
    DISABLE_RATIO_ROUND = True

    def test_profile_ratios(self, solve_method = "solve_darwin"):
        # Freeze the ratio computation formula
        expectedDailyRatios = {0 : 1.5333, 1 : 1.15, 2 : 2.3, 3 : 1.15, 4 : 4.6, 5 : 0.575, 6 : 0.5}
        for day in self.days:
            for meal_slot in day.ordered_meal_slots:
                for dish in meal_slot.ordered_dishes:
                    self.assertAlmostEqual(expectedDailyRatios[day.weekday], self.problem.dish_ratios[dish.id], 4)

        # Launching algorithm
        load_darwin_config(self.get_fixture_path(__file__, "darwin_config_test_advanced.yml"))
        print("======== Testing with solve method : '%s'" % solve_method)
        self.reload_recipe_index()
        solution = getattr(self.problem, solve_method)()

        # Saving solution in database
        self.problem.save_solution(solution)

        # Getting score
        score = self.problem.eval(solution)
        print("Score = ", score.total)
        midichloriens_per_day = defaultdict(float)
        amounts_selected = defaultdict(int)
        redundant_recipes = defaultdict(int)
        for dish_recipe in self.problem.get_results():
            ingredient = dish_recipe.recipe.ingredients.all()[0]
            nutrient   = ingredient.food.food_nutrients.all()[0]
            midichloriens = dish_recipe.ratio * ingredient.grams * nutrient.amount_per_gram
            midichloriens_per_day[dish_recipe.dish.meal_slot.day.weekday] += midichloriens
            redundant_recipes[dish_recipe.recipe.name] += 1
            amounts_selected[nutrient.amount_per_gram] += 1

        for midichloriens in midichloriens_per_day.values():
            float_epsilon_tolerance = 0.000001
            self.assertLessEqual(800 - float_epsilon_tolerance, midichloriens)
            self.assertGreaterEqual(1200 + float_epsilon_tolerance, midichloriens)
        print("Midichloriens per day", midichloriens_per_day)
        print("Amounts selected", amounts_selected)
        print("Redundant recipes", ["%s (%i times)" % (recipe, times) for recipe, times in redundant_recipes.items() if times > 1])
        self.assertEqual(score.total, 0)

class TestMultiProfileMealRatios(iRatioTest):
    NB_PROFILES = 2

    # (day, i_meal)
    SKIPPED_MEALS = [(0, 0), (1, 0), (5, 1), (6, 2)]

    def init_meal_slot(self, meal_slot_number, dish_type, day_number):

        # The second profile skips some meals
        if (day_number, meal_slot_number) in self.SKIPPED_MEALS:
            eaters = [self.eaters[0]]
        else:
            eaters = self.eaters
        return super().init_meal_slot(meal_slot_number, dish_type, day_number, with_eaters=eaters)


    @fake_profile_ratios_decorator(1)
    @fake_calories_decorator(2300)
    def test_profile_ratios(self, solve_method = "solve_darwin"):
        # 2014-12-09 infos: since the ratio patch on secondary profiles, we consider that all eaters
        # are having the same meals but not necessarily together. Therefore they have the same DailyRatio
        # but can have a different MealRatio according to their characteristics
        expectedMealRatios = {
            self.profiles[0].id : {0 : [1.5, 1.5], 1 : [1.], 2 : [2.25], 3 : [1.25, 1.25], 4 : [4.5], 5 : [0.5, 0.5], 6 : [0.5, 0.5, 0.5]},
            self.profiles[1].id : {0 : [0,   1.5], 1 : [0], 2 : [2.25], 3 : [1.25, 1.25], 4 : [4.5], 5 : [0.5, 0], 6 : [0.5, 0.5, 0]},
        }

        calculator = RatiosCalculator(self.user)

        for i_day, day in enumerate(self.days):
            for i_meal, meal_slot in enumerate(day.ordered_meal_slots):
                for dish in meal_slot.ordered_dishes:
                    expected_dish_ratios = {}
                    for profile in self.profiles:
                        expectedValue = expectedMealRatios[profile.id][day.weekday][i_meal]
                        if expectedValue > 0:
                            expected_dish_ratios[profile.id] = expectedValue


                    profiles = [eater.profile for eater in meal_slot.eaters.all()]
                    splitted_ratios = calculator.split_ratios(self.problem.dish_ratios[dish.id], profiles)
                    print("splitted_ratios : ", splitted_ratios)
                    print("expected :", expected_dish_ratios)
                    self.assertEqual(sorted(splitted_ratios.keys()), sorted(expected_dish_ratios.keys()))
                    for dish_id, value in splitted_ratios.items():
                        self.assertAlmostEqual(value, expected_dish_ratios[dish_id], 4)


class TestInitialRatioStays(HpUnidishApiTest):
    """
    Ensure that many optimizations don't set the ratio out of its boundaries :
    - With one dish only
    - With one recipe having 100g of midichloriens
    - And initial ratio of 2
    - Objective of min. 800g of midichloriens.

    Ensure that ratio goes up to 4, but no further
    """
    # 1 meal, 1 dish, 1 recipe, ...  so easy :)
    NB_RECIPES          = 1
    NB_FOODS            = 1
    NB_MEALSLOTS        = 1
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1
    NB_SLOTS_PER_DAY    = 1

    # We have an initial ratio of 2 on every dish
    INITIAL_RATIO = 2

    # By default, every recipe has a midichlorien value of 100g  (100*1g)
    def init_problem(self):
        # We want 800g of midichloriens per day
        self.constraint = NutrientConstraint(self.midichlorien, 800, -1, daily_tolerance = 0,cost_per_percent_out = 100)
        super().init_problem(forced_constraints=[self.constraint])

    def test_initial_ratio_stays(self):
        load_darwin_config(self.get_fixture_path(__file__, "darwin_config_test_advanced.yml"))
        # First optimization
        self._solve_with_no_api()
        dr = DishRecipe.objects.get()
        self.assertEqual(dr.ratio, 3)  # Maximized at +50%

        super().init_problem(forced_constraints=[self.constraint], start_from_existing_solution=True)

        # Second optimization - starting from existing
        self._solve_with_no_api(clean_before_save=True)
        dr = DishRecipe.objects.get()
        self.assertEqual(dr.ratio, 3)
