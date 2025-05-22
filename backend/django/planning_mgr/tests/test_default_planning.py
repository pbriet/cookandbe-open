from common.test            import TestAPIWithLogin
from planning_mgr.models    import MetaPlanning, MealSlot, Dish, MealSlotEater, MealType, Day, DishRecipe

from recipe_mgr.models      import DishType, Recipe, Ingredient

from eater_mgr.models       import Eater
from django.utils           import timezone
from collections            import defaultdict

class TestInitDefaultPlanningAPI(TestAPIWithLogin):

    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.assertEqual(Recipe.objects.filter(internal = False).count(), 0)
        self.init_default_meal_type_settings()
        self.nb_default_test_recipes = Recipe.objects.filter(internal = False).count()
        self.nb_default_test_ingredients = Ingredient.objects.count()
        DishType.reset()
        # 3 people, 2 are "regular eaters"
        self.profile1 = self.create_db_profile()
        self.profile2 = self.create_db_profile()
        self.profile3 = self.create_db_profile()
        self.eater1 = Eater.objects.create(profile=self.profile1, user=self.user, regular=True)
        self.eater2 = Eater.objects.create(profile=self.profile2, user=self.user, regular=False)
        self.eater3 = Eater.objects.create(profile=self.profile3, user=self.user, regular=True)
        
    def check_db_object(self):
        expectedDays = 7
        expectedGlobalMealCount = 5
        expectedDailyMealCount = 3                      # Breakfast, lunch, dinner
        expectedDailyDishCount = 2 + 1 + 4 + 1 + 5      # Breakfast, collation, lunch, snack, dinner
        expectedEaters = 2                              # 2 regulars
        expectedRoutineMealCount = 3                    # Breakfast, collation, snack
        expectedRoutineDishCount = 2 + 1 + 1            # Breakfast, collation, snack
        self.assertEqual(MetaPlanning.objects.count(), 1)
        self.assertEqual(Day.objects.count(), expectedDays)
        self.assertEqual(MealSlot.objects.filter(meal_place__key = "home").count(), expectedDailyMealCount * expectedDays)
        self.assertEqual(MealSlot.objects.filter(meal_place__key = "donoteat").count(), (expectedGlobalMealCount - expectedDailyMealCount) * expectedDays)
        self.assertEqual(MealSlot.objects.count(), 35)
        self.assertEqual(MealSlotEater.objects.count(), expectedGlobalMealCount * expectedDays * expectedEaters)
        self.assertEqual(Dish.objects.filter(dish_type__name = DishType.DT_CUSTOM).count(), expectedDays * expectedRoutineMealCount)
        self.assertEqual(Dish.objects.exclude(dish_type__name = DishType.DT_CUSTOM).count(), expectedDailyDishCount * expectedDays)
        self.assertEqual(Recipe.objects.filter(internal = True).count(), expectedRoutineMealCount)
        self.assertEqual(Recipe.objects.filter(internal = False).count(), self.nb_default_test_recipes)
        self.assertEqual(DishRecipe.objects.count(), expectedDays * expectedRoutineMealCount)
        self.assertEqual(Ingredient.objects.count(), expectedRoutineDishCount + self.nb_default_test_ingredients)
        
        # Every meal should have the main eater
        for meal_slot in MealSlot.objects.all():
            eater_ids = [eater.id for eater in meal_slot.eaters.all()]
            self.assertTrue(self.eater1.id in eater_ids)

        for dish_recipe in DishRecipe.objects.all():
            self.assertTrue(dish_recipe.recipe.internal)
            custom_ingredients = set([ ingredient.food for ingredient in dish_recipe.recipe.ingredients.all() ])
            default_recipes = list(opt.default_recipe for opt in dish_recipe.dish.meal_slot.meal_type.dish_options.filter(min_speed_check__lte = 2, min_budget_check__lte = 2, default_recipe__isnull = False))
            self.assertTrue(len(custom_ingredients), len(default_recipes))
            for recipe in default_recipes:
                self.assertEqual(recipe.ingredients.count(), 1)
                self.assertTrue(recipe.ingredients.get().food in custom_ingredients)
            
    
    def test_init_default(self):
        expectedHomeCount = 2                           # 2 meals at home (lunch, dinner)
        expectedRoutineHomeCount = 1                    # 1 meal at home, but without being suggested by default (breakfast)
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        self.check_db_object()

        for day in Day.objects.all():
            # 5 meals every day
            self.assertEqual(day.meal_slots.count(), 5)
        
        # non suggested : with already pre-set recipe forced
        nonsuggested_meals = MealSlot.objects.filter(suggest = False, meal_place__key = "home")
        self.assertEqual(nonsuggested_meals.count(), expectedRoutineHomeCount * 7) # breakfast, goûter
        for meal in nonsuggested_meals:
            for dish in meal.dishes.all():
                if dish.dish_type.name != DishType.DT_CUSTOM:
                    self.assertEqual(dish.dishrecipe_set.count(), 0) # 1 recipe set by default for each dish in a routine meal
                else:
                    self.assertEqual(dish.dishrecipe_set.count(), 1) # 1 recipe set by default for each dish in a routine meal
                    dishrecipe = dish.dishrecipe_set.get()
                    self.assertTrue(dishrecipe.user == self.user)
                    self.assertTrue(dishrecipe.validated)
                    self.assertTrue(dishrecipe.recipe.internal)
        
        # Initializing a second time should rewrite the planning
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        self.check_db_object()
            