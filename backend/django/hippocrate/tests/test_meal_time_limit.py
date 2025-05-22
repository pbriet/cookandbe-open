"""
Testing how meal time limit is constraining recipes
"""
from hippocrate.tests                       import HpUnidishApiTest
from optalim.config                         import Config
from common.mock_tools                      import empty_diet_decorator
from hippocrate.models.database             import DishRecipe
from hippocrate_cpp.core                        import set_random_seed

class TestMealTimeLimitApi(HpUnidishApiTest):
    MEAL_SLOTS_SPEED        = 2  # {'prep_minutes': 15, 'rest_minutes': 10, 'cook_minutes': 15}
    CURVE_EXPONENT          = 2

    MEAL_SLOTS_MAX_DURATION = 15
    
    NB_MEALSLOTS            = 2 # 2 meal slots -- 1 per day, with 2 dishes in it.

    def init_recipes(self):
        super().init_recipes()
        self.recipeNameDict = dict()
        for i, recipe in enumerate(self.recipes):
            recipe.prep_minutes = (i ** self.CURVE_EXPONENT) * self.MEAL_SLOTS_MAX_DURATION / (self.NB_RECIPES ** self.CURVE_EXPONENT)
            recipe.cook_minutes = ((self.NB_RECIPES - i) ** self.CURVE_EXPONENT) * self.MEAL_SLOTS_MAX_DURATION / (self.NB_RECIPES ** self.CURVE_EXPONENT)
            recipe.rest_minutes = 1
            recipe.save()
            self.recipeNameDict[recipe.name] = recipe

    def init_week(self):
        super().init_week()
        # Ajout de la limite de temps au meal
        for day in self.days:
            for meal in day.meal_slots.all():
                meal.speed = self.MEAL_SLOTS_SPEED
                meal.save()

    @empty_diet_decorator
    def test_with_meal_time_limit(self):
        set_random_seed(42)
        # Génération du planning
        response = self._fill_through_api()
        # Contrôles
        self.assertEqual(response.status_code, 201)
        # Aucun meal slot ne doit excéder sa durée limite
        self.assertEqual(len(response.data["days"]), 2)
        for day in response.data["days"]:
            self.assertEqual(len(day["meal_slots"]), 1)
            for meal_type_id, meal in day["meal_slots"].items():
                self.assertEqual(len(meal["dishes"]), 2)
                total_prep_time, total_cook_time, total_rest_time = 0, 0, 0
                for dish in meal["dishes"]:
                    self.assertEqual(len(dish["recipes"]), 1)
                    recipe = self.recipeNameDict[dish["recipes"][0]["name"]]
                    total_prep_time += recipe.prep_minutes
                    total_cook_time += recipe.cook_minutes
                    total_rest_time += recipe.rest_minutes
                print('Prep : ', total_prep_time, "<= 15")
                self.assertTrue(total_prep_time <= 15)
                print('Cook : ', total_cook_time, "<= 15")
                self.assertTrue(total_cook_time <= 15)
                print('Rest : ', total_rest_time, "<= 10")
                self.assertTrue(total_rest_time <= 10)
                