from common.test                import TestAPIWithLogin
from planning_mgr.models        import MealType, Dish, MealSlot
from recipe_mgr.models          import DishType, CookingMethod, Ingredient

class TestSuggestOrStatic(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        self.init_db_profile_eater()
        
        self.dish_type = self.create_db_dishtype()
        
        self.recipe1 = self.create_db_recipe(dish_types=[self.dish_type])
        self.recipe2 = self.create_db_recipe(dish_types=[self.dish_type])
        self.recipe3 = self.create_db_recipe(dish_types=[self.dish_type])
        
        self.breakfast = MealType.objects.get(name="Petit déjeuner")
    
        # Initializing metaplanning
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        
        # Reloading user to get metaplanning
        self.reload_user()

    def _get_breakfast_habits(self):
        response = self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.breakfast.id))
        self.assertEqual(response.status_code, 200)
        return response.data
    
    def test_get_all_habits_default(self):
        response = self.client.get('/api/user/%i/meal_types_habits' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['content']), 3) # By default, breakfast lunch and dinner

    def test_toggle_suggest(self):
        """
        Test toggling from 'suggest' to 'static' and reversed
        """
        def _check_suggest_habits(habits):
            """
            Check that configuration is correct on default breakfast 'suggest'
            """
            # Checking that 'suggestion' is enabled by default on breakfast
            self.assertTrue(habits['suggest']['enabled'])
            # There should be some entries for dish_types
            self.assertTrue(len(habits['suggest']['dish_types']) > 0)
            # Even if we are in 'suggest' mode, default static recipes should be returned
            self.assertTrue(habits['static']['recipe'] is not None)

        def _check_static_habits(habits):
            """
            Check that configuration is correct on default breakfast 'static'
            """
            self.assertFalse(habits['suggest']['enabled'])
            # No data for suggest
            self.assertTrue(len(habits['suggest']['dish_types']) == 0)
            # In 'static mode' there should be default and selected recipes
            self.assertTrue(len(habits['static']['recipe']) > 0)
            
        habits = self._get_breakfast_habits()
        _check_static_habits(habits) # Breakfast is 'static' by default
        
        # Toggling to suggest
        response = self.client.post('/api/user/%i/meal_type/%i/set_suggest' % (self.user.id, self.breakfast.id), {"suggest": True})
        self.assertEqual(response.status_code, 201)
        
        habits = self._get_breakfast_habits()
        _check_suggest_habits(habits) # Breakfast is now 'suggested'
        
        # Toggling back to static
        response = self.client.post('/api/user/%i/meal_type/%i/set_suggest' % (self.user.id, self.breakfast.id), {"suggest": False})
        self.assertEqual(response.status_code, 201)
        
        habits = self._get_breakfast_habits()
        _check_static_habits(habits) # Breakfast is now 'static' again

    def test_static_add_remove(self):
        """
        Test adding / removing ingredients in a non-suggested mealtype
        """
        # By default, a breakfast has 2 recipes forced
        habits = self._get_breakfast_habits()
        self.assertTrue(habits['static']['recipe'] is not None)
        
        def _check_dishrecipe_content(nb_dishes, dish_recipes):
            """
            Test that there are as many dishes as nb_dishes, with dishrecipe forced and validated
            Test that should_contain are in the static recipe ingredients
            """
            recipe_ids = set()
            dishes = Dish.objects.filter(meal_slot__meal_type=self.breakfast, meal_slot__day=self.user.meta_planning.days.first())
            self.assertEqual(dishes.count(), nb_dishes)
            for dish in dishes:
                if dish.dish_type.name == "Personnalisé":
                    self.assertEqual(dish.dishrecipe_set.count(), 1)
                    self.assertTrue(dish.dishrecipe_set.get().recipe.internal)
                    continue
                for dishrecipe in dish.dishrecipe_set.all():
                    self.assertTrue(dishrecipe.validated)
                    self.assertEqual(dishrecipe.user_id, self.user.id)
                    recipe_ids.add(dishrecipe.recipe)
            self.assertEqual(dish_recipes, recipe_ids)

        # By default it has 2 dishes + a dish with a forced and validated recipes (static)
        _check_dishrecipe_content(3, set())
        
        # Adding one recipe
        response = self.client.post('/api/user/%i/meal_type/%i/add_static_recipe' % (self.user.id, self.breakfast.id),
                                    {'recipe_id': self.recipe2.id})
        self.assertEqual(response.status_code, 201)
        _check_dishrecipe_content(4, set([self.recipe2]))
        
        
        # Adding an other recipe
        response = self.client.post('/api/user/%i/meal_type/%i/add_static_recipe' % (self.user.id, self.breakfast.id),
                                    {'recipe_id': self.recipe3.id})
        self.assertEqual(response.status_code, 201)
        _check_dishrecipe_content(5, set([self.recipe2, self.recipe3]))
        
        # Removing the first one
        response = self.client.post('/api/user/%i/meal_type/%i/del_static_recipe' % (self.user.id, self.breakfast.id),
                                    {'recipe_id': self.recipe2.id})
        self.assertEqual(response.status_code, 201)
        _check_dishrecipe_content(4, set([self.recipe3]))

    def _check_dish_content(self, nb_dishes, should_contains):
        dishes = Dish.objects.filter(meal_slot__meal_type = self.breakfast,
                                     meal_slot__day=self.user.meta_planning.days.first(),
                                     dish_type__name = DishType.DT_CUSTOM)
        self.assertEqual(dishes.count(), nb_dishes)
        dish = dishes.get()
        self.assertEqual(dish.dishrecipe_set.count(), 1)
        self.assertTrue(dish.dishrecipe_set.get().validated)
        self.assertEqual(dish.dishrecipe_set.get().user_id, self.user.id)
        custom_recipe = dish.dishrecipe_set.get().recipe
        self.assertTrue(custom_recipe.internal)
        custom_foods = set([ingredient.food_id for ingredient in custom_recipe.ingredients.all()])
        for food in should_contains:
            self.assertTrue(food.id in custom_foods)
        return custom_recipe

    def test_custom_recipe(self):
        """
        Test adding / removing ingredients in a non-suggested mealtype
        """
        self.food1 = self.create_db_food()
        self.food2 = self.create_db_food()
        self.create_db_food_conversion(self.food1)
        self.create_db_food_conversion(self.food2)
        habits = self._get_breakfast_habits()
        self.assertTrue(habits['static']['recipe'] is not None)
        
        custom_recipe = self._check_dish_content(1, set())
        response = self.client.post('/api/ingredient', {
            'food': self.food1.id,
            'recipe': custom_recipe.id,
            'grams': 100,
            'raw_state': self.raw.id,
            'cooking_method': self.not_cooked.id,
        })
        self._check_dish_content(1, set([self.food1, ]))
        response = self.client.post('/api/ingredient', {
            'food': self.food2.id,
            'recipe': custom_recipe.id,
            'grams': 100,
            'raw_state': self.raw.id,
            'cooking_method': self.not_cooked.id,
        })
        self._check_dish_content(1, set([self.food1, self.food2]))
        response = self.client.delete('/api/ingredient/%i' % Ingredient.objects.get(recipe = custom_recipe, food = self.food1).id)
        self._check_dish_content(1, set([self.food2, ]))

    def test_empty_custom_recipe(self):
        nb_meta_slots = 7 * 5
        nb_week_slots = 7 * 3
        custom_recipe = self._check_dish_content(1, set())
        # Check static breakfast
        habits = self._get_breakfast_habits()
        self.assertFalse(habits['suggest']['enabled'])
        self.assertTrue(len(habits['static']['recipe']) > 0)
        # Génération du planning
        self.assertEqual(MealSlot.objects.count(), nb_meta_slots)
        response = self.client.post('/api/user/%i/add_days/2010-01-01' % self.user.id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MealSlot.objects.count(), nb_meta_slots + nb_week_slots)
        # Control du repas static plein: doit contenir les ingrédients
        breakfast = MealSlot.objects.get(meal_type = self.breakfast, day__date = '2010-01-01')
        self.assertEqual(breakfast.suggest, False)
        self.assertEqual(breakfast.dishes.count(), 1)
        self.assertEqual(breakfast.dishes.get().recipes.get().ingredients.count(), custom_recipe.ingredients.count())
        # Set empty custom recipe
        custom_recipe.ingredients.all().delete()
        self.assertEqual(custom_recipe.ingredients.count(), 0)
        # Génération du planning
        response = self.client.post('/api/user/%i/add_days/2010-01-08' % self.user.id)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(MealSlot.objects.count(), nb_meta_slots + 2 * nb_week_slots)
        # Control du repas static vide: doit contenir l'équivalent d'un suggest
        breakfast = MealSlot.objects.get(meal_type = self.breakfast, day__date = '2010-01-08')
        self.assertEqual(breakfast.dishes.count(), 2)
        self.assertEqual(breakfast.suggest, True)
