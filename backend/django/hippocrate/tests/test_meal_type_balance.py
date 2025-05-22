from hippocrate.tests                   import HpUnidishApiTest
from common.boost                       import to_dict
from hippocrate_cpp.core                    import set_random_seed
from hippocrate.models.constraints      import MealTypeBalanceConstraint
from collections                        import defaultdict

class _TestMealTypeBalance(HpUnidishApiTest):
    """
    Test that the algorithm encourage a meal type balance between all meals of the same type
    """

    def setUp(self):
        self.dishes_per_meal_type = defaultdict(set)
        self.meal_types = [self.create_db_mealtype() for i in range (self.NB_SLOTS_PER_DAY)]
        super().setUp()

    def init_nutrients(self):
        self.nutrient = self.create_db_nutrient("energie", key="energie")

    def init_food_nutrients(self, i, food):
        # 1kcal per gram of food
        self.create_db_foodnutrient(food, self.nutrient, 1, raw_state = self.raw, cooking_method = self.not_cooked)
        
    def init_ingredient(self, recipe_number, recipe, **kargs):
        food = self.foods[0] # There is only one food
        # Creating NB_SLOTS_PER_DAY ingredient types
        grams = dict((i, i * 1000) for i in range(0, self.NB_RECIPE_CATEGORIES))
        # NB: default profile ratio is 0.5. Doubling nutrient
        ingredient  = self.create_db_ingredient(recipe, food, grams[recipe_number % self.NB_RECIPE_CATEGORIES])
        return ingredient
    
    def init_meal_slot(self, meal_slot_number, *args, **kargs):
        meal_slot = super().init_meal_slot(meal_slot_number, *args, **kargs)
        # Meal of each type per day
        meal_slot.meal_type = self.meal_types[meal_slot.day.meal_slots.count() - 1]
        meal_slot.save()
        return meal_slot
    
    def create_db_dish(self, *args, **kargs):
        """
        Overriding create_db_dish to store the created dishes
        """
        dish = super().create_db_dish(*args, **kargs)
        self.dishes_per_meal_type[dish.meal_slot.meal_type].add(dish)
        return dish

    def init_problem(self, dish_ids = None, forced_constraints = None):
        self.assertTrue(forced_constraints is None)
        forced_constraints = [MealTypeBalanceConstraint(self.nutrient.key, min_ratio = 0.9, max_ratio = 1.1)]
        return super().init_problem(dish_ids, forced_constraints)

class TestMealTypeBalance(_TestMealTypeBalance):
    """
    4 days, 2 different meals per day
    """
    NB_MEALSLOTS            = 8
    NB_SLOTS_PER_DAY        = 2
    NB_DISHES_PER_MEAL      = 1
    NB_PROFILES             = 1
    NB_FOODS                = 1
    NB_RECIPES              = NB_MEALSLOTS
    NB_RECIPE_CATEGORIES    = 4
    
    def test_balance(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        # Retrieving dishrecipes
        recipes_per_dish = to_dict(solution.get_recipes())
        # Checking meal type balance
        for meal_type, dishes in self.dishes_per_meal_type.items():
            nutrients = set()
            for dish in dishes:
                recipe_list = recipes_per_dish[dish.id]
                self.assertEqual(len(recipe_list), 1)
                nutrient_value = recipe_list[0].get_data_from_key(self.nutrient.key)
                nutrients.add(nutrient_value)
                print("meal type", meal_type.id, "dish nutrients", nutrient_value)
            self.assertEqual(len(nutrients), 1)
        self.assertEqual(self.problem.eval(solution).total, 0)

class TestMealTypeBalanceWithExternal(_TestMealTypeBalance):
    """
    4 days, 2 different meals per day, 1 external on each meal type
    """
    NB_MEALSLOTS            = 8
    NB_SLOTS_PER_DAY        = 2
    NB_DISHES_PER_MEAL      = 1
    NB_PROFILES             = 1
    NB_FOODS                = 1
    NB_RECIPES              = NB_MEALSLOTS
    NB_RECIPE_CATEGORIES    = 4
    FORCED_NUTRIENTS        = 10000
    
    def setUp(self):
        self.external = self.create_db_mealplace("away")
        super().setUp()

    def init_recipes(self, *args, **kargs):
        self.external_recipe = self.create_db_recipe(dish_types = [self.defaultDishType, ], internal = True)
        food = self.foods[0] # There is only one food
        self.create_db_ingredient(self.external_recipe, food, self.FORCED_NUTRIENTS) # Can't be equilibrated
        return super().init_recipes(*args, **kargs)

    def init_meal_slot(self, meal_slot_number, *args, **kargs):
        if meal_slot_number in range(self.NB_SLOTS_PER_DAY):
            # The first day is external
            kargs["meal_place"] = self.external
        meal_slot = super().init_meal_slot(meal_slot_number, *args, **kargs)
        return meal_slot

    def create_db_dish(self, meal_slot, *args, **kargs):
        if meal_slot.meal_place_id == self.external.id:
            kargs["recipes"] = [self.external_recipe, ]
            kargs["user_dish_recipes"] = self.user # Forced to external
        dish = super().create_db_dish(meal_slot, *args, **kargs)
        return dish

    def test_balance_with_external(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        # Retrieving dishrecipes
        recipes_per_dish = to_dict(solution.get_recipes())
        # Checking meal type balance
        for meal_type, dishes in self.dishes_per_meal_type.items():
            nutrients = set()
            for dish in dishes:
                recipe_list = recipes_per_dish[dish.id]
                self.assertEqual(len(recipe_list), 1)
                external = dish.meal_slot.meal_place_id == self.external.id
                nutrient_value = recipe_list[0].get_data_from_key(self.nutrient.key)
                if external:
                    self.assertEqual(nutrient_value, self.FORCED_NUTRIENTS)
                else:
                    nutrients.add(nutrient_value)
                print("meal type", meal_type.id, "dish", dish.id, "nutrients", nutrient_value, ("", "(external)")[external])
            self.assertEqual(len(nutrients), 1)
        self.assertEqual(self.problem.eval(solution).total, 0)
