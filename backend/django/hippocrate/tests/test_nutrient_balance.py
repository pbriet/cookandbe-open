from hippocrate.tests                   import HpUnidishApiTest
from common.boost                       import to_dict
from hippocrate_cpp.core                    import set_random_seed
from hippocrate.models.constraints      import NutrientBalanceConstraint
from collections                        import defaultdict

class _TestNutrientBalance(HpUnidishApiTest):
    def setUp(self):
        self.dishes_per_day = defaultdict(set)
        self.dishes_per_meal = defaultdict(set)
        self.meal_types = [self.create_db_mealtype() for i in range (self.NB_SLOTS_PER_DAY)]
        super().setUp()

    def init_nutrients(self):
        self.nutrient = self.create_db_nutrient("energie", key="energie")
        self.referent = self.create_db_nutrient("anti-energie", key="anti-energie")

    def init_food_nutrients(self, i, food):
        if i % 2 == 0:
            self.create_db_foodnutrient(food, self.nutrient, 10, raw_state = self.raw, cooking_method = self.not_cooked)
            self.create_db_foodnutrient(food, self.referent, 1, raw_state = self.raw, cooking_method = self.not_cooked)
        if i % 2 == 1:
            self.create_db_foodnutrient(food, self.referent, 10, raw_state = self.raw, cooking_method = self.not_cooked)
            self.create_db_foodnutrient(food, self.nutrient, 1, raw_state = self.raw, cooking_method = self.not_cooked)
        
    def init_ingredient(self, recipe_number, recipe, **kargs):
        # One recipe contains "energie" the other "anti-energie"
        ingredient  = self.create_db_ingredient(recipe, self.foods[recipe_number % self.NB_FOODS], 100)
        return ingredient
    
    def create_db_dish(self, *args, **kargs):
        """
        Overriding create_db_dish to store the created dishes
        """
        dish = super().create_db_dish(*args, **kargs)
        self.dishes_per_day[dish.meal_slot.day].add(dish)
        self.dishes_per_meal[dish.meal_slot].add(dish)
        return dish

    def init_problem(self, dish_ids = None, forced_constraints = None):
        self.assertTrue(forced_constraints is None)
        forced_constraints = [NutrientBalanceConstraint(self.nutrient.key, self.referent.key, min_ratio = 0.9, max_ratio = 1.1)]
        return super().init_problem(dish_ids, forced_constraints)

class TestDayNutrientBalance(_TestNutrientBalance):
    """
    4 days, 2 different meals per day, 2 recipes categories
    """
    NB_MEALSLOTS            = 8
    NB_SLOTS_PER_DAY        = 2
    NB_DISHES_PER_MEAL      = 1
    NB_PROFILES             = 1
    NB_FOODS                = 2
    NB_RECIPES              = NB_MEALSLOTS

    def test_balance(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        # Retrieving dishrecipes
        recipes_per_dish = to_dict(solution.get_recipes())
        # Checking nutrient balance
        for day, dishes in self.dishes_per_day.items():
            energy = 0
            for dish in dishes:
                recipe_list = recipes_per_dish[dish.id]
                self.assertEqual(len(recipe_list), 1)
                nutrient_value = recipe_list[0].get_data_from_key(self.nutrient.key)
                referent_value = recipe_list[0].get_data_from_key(self.referent.key)
                energy += nutrient_value
                energy -= referent_value
                print("day", day.id, "dish", dish.id, "energy", nutrient_value, "antienergy", referent_value)
            self.assertEqual(energy, 0)
        self.assertEqual(self.problem.eval(solution).total, 0)

class TestMealNutrientBalance(_TestNutrientBalance):
    """
    4 days, 2 different meals per day, 2 recipes categories
    """
    NB_MEALSLOTS            = 8
    NB_SLOTS_PER_DAY        = 1
    NB_DISHES_PER_MEAL      = 2
    NB_PROFILES             = 1
    NB_FOODS                = 2
    NB_RECIPES              = NB_MEALSLOTS

    def test_balance(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        # Retrieving dishrecipes
        recipes_per_dish = to_dict(solution.get_recipes())
        # Checking nutrient balance
        for meal, dishes in self.dishes_per_meal.items():
            energy = 0
            for dish in dishes:
                recipe_list = recipes_per_dish[dish.id]
                self.assertEqual(len(recipe_list), 1)
                nutrient_value = recipe_list[0].get_data_from_key(self.nutrient.key)
                referent_value = recipe_list[0].get_data_from_key(self.referent.key)
                energy += nutrient_value
                energy -= referent_value
                print("meal", meal.id, "dish", dish.id, "energy", nutrient_value, "antienergy", referent_value)
            self.assertEqual(energy, 0)
        self.assertEqual(self.problem.eval(solution).total, 0)
