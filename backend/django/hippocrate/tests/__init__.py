
from common.boost                               import to_dict
from common.mock_tools                          import fake_ratios_decorator
from common.test                                import TestAPIWithLogin

from hippocrate.controls.indicators             import old_retrieve_indicators
from hippocrate_cpp.core                            import load_darwin_config
from hippocrate.models.database                 import DishType, RecipeDishType
from hippocrate.models.problem                  import Problem
from hippocrate.models.recipestorage            import MainRecipeStorage

from nutrient.models                            import Nutrient

from planning_mgr.models                        import DishRecipe, Day

from recipe_mgr.models                          import Recipe

from mock                                       import patch
from math                                       import ceil

import datetime


class HpUnidishApiTest(TestAPIWithLogin):
    NB_RECIPES          = 20
    NB_FOODS            = 10
    NB_MEALSLOTS        = 7
    NB_DISHES_PER_MEAL  = 2
    NB_PROFILES         = 1
    NB_SLOTS_PER_DAY    = 1
    WITH_INGREDIENTS    = True
    START_DATE          = datetime.date(2014, 3, 3) # Monday
    INITIAL_RATIO       = 1

    NB_DAYS = property(lambda x: int(ceil(float(x.NB_MEALSLOTS) / x.NB_SLOTS_PER_DAY)))

    def setUp(self):
        super().setUp()
        self.init_user()
        # Everything will be raw, not_cooked and full of Midichloriens !
        self.init_default_ingredient_settings()
        load_darwin_config(self.get_fixture_path(__file__, "naive_darwin_conf.yml"))
        for i in range(self.NB_PROFILES):
            self.init_db_profile_eater()
        self.init_nutrients()
        MainRecipeStorage.init_indexer()
        self.init_foods()
        self.init_recipes()
        self.reload_recipe_index()
        self.init_week()
        self.init_problem()

    def debug_print_indicators(self):
        """
        Useful for test debugging purposes
        """
        score = self.problem.eval(solution)
        constraints = old_retrieve_indicators(self.problem, score)
        print(constraints)


    def _fill_through_api(self):
        """
        Calls the API to fill the planning
        """
        return self.client.post('/api/user/%i/fill_days/%s' % (self.user.id, self.START_DATE), {"nb_days": self.NB_DAYS})

    def _suggest_through_api(self, date=None, start_from_existing=False):
        """
        Calls the API to get suggestions and recalculate
        """
        if date is None:
            date = self.START_DATE
        return self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {"date": date, "init": not start_from_existing, "recalculate": True})

    def _solve_with_no_api(self, save=True, clean_before_save=False):
        # Launching algorithm
        solution = self.problem.solve_darwin()

        # Saving solution in database
        if save:
            if clean_before_save:
                self.problem.clean_previous_solution()
            self.problem.save_solution(solution)
        
        return solution
    
    def init_user(self):
        # Some stuff to init the user ?
        pass

    def init_food_nutrients(self, i, food):
        self.create_db_foodnutrient(food, self.midichlorien, 1, raw_state=self.raw, cooking_method=self.not_cooked)

    def init_food(self, i):
        food = self.create_db_food(name = 'Yumyum %i' % i)
        self.foods.append(food)
        self.init_food_nutrients(i, food)
        return food
    
    def init_nutrients(self):
        self.midichlorien = self.create_db_nutrient("Midichloriens", unit = "mg")
        self.init_default_nutrients()
    
    def init_foods(self, init_default_dish_type=True):
        # Only one DishType used
        if init_default_dish_type:
            self.defaultDishType = self.create_db_dishtype("Plat complet") # Unicity will be applied by default
        if not self.WITH_INGREDIENTS:
            return

        # Creating foods
        self.foods      = []
        for i in range(self.NB_FOODS):
            self.init_food(i)

    def init_recipe(self, recipe_number, dish_type, recipe_name = None):
        if recipe_name is None:
            recipe_name = "Recipe %i" % recipe_number
        recipe = self.create_db_recipe(name = recipe_name)
        RecipeDishType.objects.create(recipe = recipe, dish_type = dish_type)
        return recipe

    def init_ingredient(self, recipe_number, recipe, food = None, quantity = 100):
        if food is None:
            food = self.foods[recipe_number % self.NB_FOODS]
        ingredient  = self.create_db_ingredient(recipe, food, quantity)
        return ingredient
    
    def init_recipes(self):
        # Creating recipes (for now with ingredient and defaultDishType)
        self.recipes        = []
        self.ingredients    = []
        for i in range(self.NB_RECIPES):
            recipe = self.init_recipe(i, self.defaultDishType)
            self.recipes.append(recipe)
            if self.WITH_INGREDIENTS:
                ingredient = self.init_ingredient(i, recipe)
                self.ingredients.append(ingredient)

    def init_meal_slot(self, meal_slot_number, days = None, day_no = 0, speed = 4, eaters = None, **kargs):
        if days is None and hasattr(self, "days"):
            days = self.days
        day = days[int(day_no)]
        return self.create_db_mealslot(day,
                                       speed        = speed,
                                       with_eaters  = eaters,
                                       **kargs)
    
    def init_week(self, eaters = None):
        planning = self.create_db_planning(start_date=self.START_DATE, nb_days=self.NB_DAYS)
        self.days = planning.sorted_days

        self.dishes = []
        self.mealslots = []

        # MealSlots (1 per day for now)
        for i in range(self.NB_MEALSLOTS):
            mealslot = self.init_meal_slot(i, self.days, i / self.NB_SLOTS_PER_DAY, eaters = eaters)
            self.mealslots.append(mealslot)
            # Dishes (2 dishes per mealslot for now)
            for j in range(self.NB_DISHES_PER_MEAL):
                dish = self.create_db_dish(mealslot, self.defaultDishType, order=j)
                self.dishes.append(dish)

    def init_problem(self, dish_ids=None, forced_constraints=None, start_from_existing_solution=False):
        @fake_ratios_decorator(self.INITIAL_RATIO)
        def fcn():
            self.problem = Problem(self.days, enable_diet=False, dish_ids=dish_ids,
                                forced_constraints=forced_constraints,
                                start_from_existing_solution=start_from_existing_solution,
                                current_day=self.days[0])
        fcn()

    def reload_recipe_index(self):
        nutrient_ids = []
        if self.WITH_INGREDIENTS:
            nutrient_ids = [n.id for n in Nutrient.objects.all()]
            
        self.init_recipe_index(nutrient_ids)

    def _get_recipe_ids(self, solution):
        """
        From a solution, returns the list of recipe ids selected
        """
        res = []
        for dish_id, recipe_list in to_dict(solution.get_recipes()).items():
            for r in recipe_list:
                res.append(r.recipe_id)
        return res
    
    
class DefaultMetaPlanningHippocrateTest(TestAPIWithLogin):
    """
    Test with a default metaplanning creation, through API, and
    some helpers to call the optimize API
    """
    
    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        self.init_default_nutrients()
        profile = self.create_db_profile()
        self.create_db_eater(profile)
        
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        
        for dish_type in DishType.objects.all():
            self.recipe = self.create_db_recipe(dish_types=[dish_type])
            
        self.init_recipe_index([])

    def _fill_through_api(self, date):
        response = self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {'init': True})
        self.assertEqual(response.status_code, 200)
        
    def _suggest_through_api(self, date=None, start_from_existing=False):
        """
        Calls the API to get suggestions and recalculate
        """
        if date is None:
            date = self.START_DATE
        return self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {"date": date, "init": not start_from_existing, "recalculate": True})

    def _nb_dishrecipes(self):
        return DishRecipe.objects.count()
    
    def _nb_days(self):
        return Day.objects.count()