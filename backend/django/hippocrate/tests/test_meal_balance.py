from hippocrate.tests                   import HpUnidishApiTest
from common.boost                       import to_dict
from hippocrate_cpp.core                    import set_random_seed

class TestMealBalance(HpUnidishApiTest):
    """
    Test that the algorithm encourage a meal balance between lunch and dinner :
    - 2 meal_slots in the same day  (lunch + dinner) with one dish each
    - 4 recipes : 1000kcal, 2000kcal, 2300kcal, 4000kcal
    """
    NB_MEALSLOTS        = 2
    NB_SLOTS_PER_DAY    = 2
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1
    NB_FOODS            = 1
    NB_RECIPES          = 4

    def setUp(self):
        self.dish_ids = []
        self.lunch = self.create_db_mealtype(key="lunch", name="Déjeuner", nickname="Déjeuner")
        self.dinner = self.create_db_mealtype(key="dinner", name="Dîner", nickname="Dîner")
        super().setUp()

    def init_nutrients(self):
        self.calories = self.init_default_nutrients()

    def init_food_nutrients(self, i, food):
        # 1kcal per gram of food
        self.create_db_foodnutrient(food, self.calories, 1, raw_state=self.raw, cooking_method=self.not_cooked)
        
    def init_ingredient(self, recipe_number, recipe, **kargs):
        food = self.foods[0] # There is only one food
        # Grams depend on recipe_number
        # NB : default profile ratio is 0.5. Doubling calories
        grams = {0: 2000, 1: 4000, 2: 4600, 3: 8000}
        ingredient  = self.create_db_ingredient(recipe, food, grams[recipe_number])
        return ingredient
    
    def init_meal_slot(self, meal_slot_number, *args, **kargs):
        meal_slot = super().init_meal_slot(meal_slot_number, *args, **kargs)
        if meal_slot_number == 0:
            meal_slot.meal_type = self.lunch
        else:
            meal_slot.meal_type = self.dinner
        meal_slot.save()
        return meal_slot
    
    def create_db_dish(self, *args, **kargs):
        """
        Overriding create_db_dish to store the created dishes
        """
        dish = super().create_db_dish(*args, **kargs)
        self.dish_ids.append(dish.id)
        return dish

    def test_balance(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        recipe_per_dish = {}
        for dish_id, recipe_list in to_dict(solution.get_recipes()).items():
            assert len(recipe_list) == 1
            recipe_per_dish[dish_id] = recipe_list[0].recipe_id
            
        # Lunch should be the recipe with 2300kcal
        self.assertEqual(recipe_per_dish[self.dish_ids[0]], self.recipes[2].id)
        # Dinner should be the recipe with 2000kcal (87% of lunch)
        self.assertEqual(recipe_per_dish[self.dish_ids[1]], self.recipes[1].id)
        