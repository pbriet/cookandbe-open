from common.test            import TestAPIWithLogin
from common.date            import get_tomorrow
from common.model           import reload_object
from django.utils           import timezone
from planning_mgr.models    import DishRecipe, MealSlot, Dish
from mock                   import patch
import datetime


class TestSetDishRecipe(TestAPIWithLogin):
    SUBSCRIPTION_LEVEL = 1
    
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        self.dish_type_agg, self.dish_type1, self.dish_type2 = self.create_db_dishtype_aggregated()

        self.meta_planning  = self.create_db_meta_planning(user=self.user, with_n_days=1)
        # One meal slot with 2 dishes, first a simple, then an aggregated one
        self.mealslot       = self.create_db_mealslot(self.meta_planning.sorted_days[0])
        self.simple_dish    = self.create_db_dish(self.mealslot, self.dish_type1, order=1)
        self.agg_dish       = self.create_db_dish(self.mealslot, self.dish_type_agg, order=2)
        self.user.meta_planning = self.meta_planning
        self.user.save()

        self.recipe1_1 = self.create_db_recipe(dish_types=[self.dish_type1])
        self.recipe1_2 = self.create_db_recipe(dish_types=[self.dish_type1])
        self.recipe1_3 = self.create_db_recipe(dish_types=[self.dish_type1])
        
        self.carrots = self.create_db_food("carrots")
        self.ingredient = self.create_db_ingredient(self.recipe1_1, self.carrots, 400)
        
        self.recipe2 = self.create_db_recipe(dish_types=[self.dish_type2])
        self.recipe2_bis = self.create_db_recipe(dish_types=[self.dish_type2])
        self.recipeagg = self.create_db_recipe(dish_types=[self.dish_type_agg])
        self.recipeagg2 = self.create_db_recipe(dish_types=[self.dish_type_agg])
        
    def test_set_dishrecipes(self):
        
        tomorrow = get_tomorrow()
        
        response = self.client.post('/api/user/%i/add_days/%s' % (self.user.id, tomorrow))
        self.assertEqual(response.status_code, 201)
        dishes = list(Dish.objects.filter(meal_slot__day__date__gte=tomorrow))
        dishes_date = None
        for dish in dishes:
            # checking generated dishes are built on a monday
            self.assertEqual(dish.meal_slot.day.weekday, 0)
            dishes_date = dish.meal_slot.day.date
            
        self.assertEqual(len(dishes), 2)

        # Force a recipe on one dish
        response = self.client.post('/api/user/%s/set_dishrecipes/%s' % (self.user.id, self.simple_dish.id),
                                    {'recipe_ids': [self.recipe1_1.id], 'force': True, 'ratio': 1.2}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 201)

        dish_recipes = list(self.simple_dish.dishrecipe_set.all())
        self.assertEqual(len(dish_recipes), 1)
        self.assertTrue(dish_recipes[0].user == self.user) # Means 'forced by the user'
        self.assertEqual(dish_recipes[0].recipe_id, self.recipe1_1.id)

        # Force 2 recipes on the same dish -> should override
        response = self.client.post('/api/user/%s/set_dishrecipes/%s' % (self.user.id, self.simple_dish.id),
                                    {'recipe_ids': [self.recipe1_2.id, self.recipe1_1.id], 'force': True}, format='json')
        dish_recipes = list(self.simple_dish.dishrecipe_set.all())
        self.assertEqual(len(dish_recipes), 2)
        for dr in dish_recipes:
            # Should have kept the ratio of the previous recipe set
            self.assertEqual(dr.ratio, 1.2)


        # Test forcing one recipe again
        response = self.client.post('/api/user/%i/set_dishrecipes/%s' % (self.user.id, self.simple_dish.id),
                                    {'recipe_ids': [self.recipe1_1.id], 'force': True}, format='json')
        self.assertEqual(response.status_code, 201)

        dish_recipes = list(self.simple_dish.dishrecipe_set.all())
        self.assertEqual(len(dish_recipes), 1)
        self.assertTrue(dish_recipes[0].user == self.user)
        self.assertEqual(dish_recipes[0].recipe_id, self.recipe1_1.id)


    def test_set_dishrecipe_basic(self):
        """
        Test when setting a recipe (basic)
        """
        self.create_db_dishrecipe(self.simple_dish, self.recipe1_2)
        
        # set a recipe on the dish dish_type
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.simple_dish.id),
                                    {'recipe_id': self.recipe1_1.id, 'ratio': 1.2}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 201)

        dish_recipes = list(self.simple_dish.dishrecipe_set.all())
        self.assertEqual(len(dish_recipes), 1)
        self.assertEqual(dish_recipes[0].recipe_id, self.recipe1_1.id)


    def test_set_dishrecipe_invalid(self):
        """
        Test setting a recipe with a wrong dish type
        """
        # Index is too high
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.simple_dish.id),
                                    {'recipe_id': self.recipe1_1.id, 'ratio': 1.2, 'index': 1}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 400)

    def test_set_simple_aggregated(self):
        self.create_db_dishrecipe(self.agg_dish, self.recipeagg)
        
        # set a recipe on the dish dish_type
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipeagg2.id, 'ratio': 1.2}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 201)

        dish_recipes = list(self.agg_dish.dishrecipe_set.all())
        self.assertEqual(len(dish_recipes), 1)
        self.assertEqual(dish_recipes[0].recipe_id, self.recipeagg2.id)


    def test_set_dishrecipe_subtype_from_two_recipes(self):
        
        # Setting directly 2 recipes
        response = self.client.post('/api/user/%s/set_dishrecipes/%s' % (self.user.id, self.agg_dish.id),
                                    {'recipe_ids': [self.recipe1_2.id, self.recipe2.id], 'force': True,
                                    'ratio': 1.2}, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Then setting a "sub recipe", this should split the Dish into 2 dishes
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipe1_3.id, 'index': 0},
                                    format='json')

        print(response.data)
        self.assertEqual(response.status_code, 201)
        dishes = self.mealslot.dishes.all()
        self.assertEqual(len(dishes), 3)
        dish_dts = [dish.dish_type_id for dish in dishes]
        dish_orders = [dish.order for dish in dishes]
        self.assertEqual(sorted(dish_dts), sorted([self.dish_type1.id, self.dish_type1.id, self.dish_type2.id]))
        self.assertEqual(sorted(dish_orders), [1, 2, 3])
        
        # Reloading the dish
        reload_object(self.agg_dish)
        # It should now have a sub dish type id
        self.assertEqual(self.agg_dish.dish_type_id, self.dish_type1.id)
        # And recipe 1_3
        self.assertEqual(self.agg_dish.recipes.count(), 1)
        self.assertTrue(self.recipe1_3.id in [r.id for r in self.agg_dish.recipes.all()])

        # The newly created dish should have the previously set recipe2
        last_dish = Dish.objects.order_by('-id')[0]
        self.assertEqual(last_dish.dish_type_id, self.dish_type2.id)
        self.assertTrue(self.recipe2.id in [r.id for r in last_dish.recipes.all()])

        
        
    def test_set_dishrecipe_subtype_from_two_recipes_at_index1(self):
        
        # Setting directly 2 recipes
        response = self.client.post('/api/user/%s/set_dishrecipes/%s' % (self.user.id, self.agg_dish.id),
                                    {'recipe_ids': [self.recipe1_2.id, self.recipe2.id], 'force': True,
                                    'ratio': 1.2}, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Then setting a "sub recipe", this should split the Dish into 2 dishes
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipe2_bis.id, 'index': 1},
                                    format='json')

        print(response.data)
        self.assertEqual(response.status_code, 201)
        dishes = self.mealslot.dishes.all()
        self.assertEqual(len(dishes), 3)
        dish_dts = [dish.dish_type_id for dish in dishes]
        dish_orders = [dish.order for dish in dishes]
        self.assertEqual(sorted(dish_dts), sorted([self.dish_type1.id, self.dish_type1.id, self.dish_type2.id]))
        self.assertEqual(sorted(dish_orders), [1, 2, 3])
        
        # Reloading the dish
        reload_object(self.agg_dish)
        # It should now have a sub dish type id
        self.assertEqual(self.agg_dish.dish_type_id, self.dish_type1.id)
        # And recipe 1_2
        self.assertEqual(self.agg_dish.recipes.count(), 1)
        self.assertTrue(self.recipe1_2.id in [r.id for r in self.agg_dish.recipes.all()])

        # The newly created dish should have the new recipe2_bis
        last_dish = Dish.objects.order_by('-id')[0]
        self.assertEqual(last_dish.dish_type_id, self.dish_type2.id)
        self.assertTrue(self.recipe2_bis.id in [r.id for r in last_dish.recipes.all()])

    

class TestsSetDishRecipeMonotonous(TestAPIWithLogin):
    """
    Test that forcing a recipe on a monotonous dish type also modifies all the non-validated
    dishes of same dish_type  (but not forcing them)
    """
    SUBSCRIPTION_LEVEL = 1
    
    def setUp(self):
        super().setUp()
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        
        self.dish_type_classic = self.create_db_dishtype("classic")
        self.dish_type_monotonous = self.create_db_dishtype("monotonous", monotonous=True)
        
        self.planning  = self.create_db_planning(user=self.user)
        
        self.metaplanning = self.create_db_meta_planning(user=self.user)

        self.days = []
        def add_day(d): self.days.append(d)
        # First day : validated
        add_day(self.create_db_day(date=datetime.date(2012, 4, 3), skipped=False, planning=self.planning))
        # Second day: validated
        add_day(self.create_db_day(date=datetime.date(2012, 4, 4), skipped=False, planning=self.planning))
        # Third day : skipped
        add_day(self.create_db_day(date=datetime.date(2012, 4, 5), skipped=True, planning=self.planning))
        # 4th to 6th day : not discovered yet
        add_day(self.create_db_day(date=datetime.date(2012, 4, 6), skipped=None, planning=self.planning))
        add_day(self.create_db_day(date=datetime.date(2012, 4, 7), skipped=None, planning=self.planning))
        add_day(self.create_db_day(date=datetime.date(2012, 4, 8), skipped=None, planning=self.planning))
        
        # Metaplanning day
        add_day(self.create_db_day(date=datetime.date(2007, 1, 1), skipped=None, planning=self.metaplanning))
        
        # One mealslot per day
        self.meal_slots = []
        for day in self.days:
            self.meal_slots.append(self.create_db_mealslot(day))
        
        # For each meal_slot, a classic dish and a monotonous dish
        self.classic_dishes, self.mono_dishes = [], []
        for mealslot in self.meal_slots:
            self.classic_dishes.append(self.create_db_dish(mealslot, self.dish_type_classic))
            self.mono_dishes.append(self.create_db_dish(mealslot, self.dish_type_monotonous))
        
        # 2 recipes for each dish_type
        self.classic_recipes, self.mono_recipes = [], []
        for i in range(2):
            self.classic_recipes.append(self.create_db_recipe(dish_types=[self.dish_type_classic]))
            self.mono_recipes.append(self.create_db_recipe(dish_types=[self.dish_type_monotonous]))
        
        # Setting dishrecipes - with the first recipe of each type
        for dishes, recipes in (self.classic_dishes, self.classic_recipes), (self.mono_dishes, self.mono_recipes):
            for i, dish in enumerate(dishes):
                self.create_db_dishrecipe(dish, recipes[0])
        
        # On 5th day, the monotonous recipe is validated
        DishRecipe.objects.filter(dish_id=self.mono_dishes[4].id).update(validated=True)
        # On 6th day, the monotonous recipe is forced
        DishRecipe.objects.filter(dish_id=self.mono_dishes[5].id).update(user=self.user)
        
        
    def test_force_monotonous_recipe(self):
        # Force a recipe on first monotonous dish, in a validated day
        response = self.client.post('/api/user/%s/set_dishrecipe/%s' % (self.user.id, self.mono_dishes[1].id),
                                    {'recipe_id': self.mono_recipes[1].id, 'ratio': 1.2}, format='json')
        print(response.data)
        self.assertEqual(response.status_code, 201)

        EXPECTED_RECIPE_PER_DISH = {
            0: 0,  # Day that was validated, don't touch !
            1: 1,  # This is the recipe we wanted to force. Check that it's done
            2: 1,  # On skipped day, this should also be done !
            3: 1,  # On 3rd day, which was undiscovered, this should also be done !
            4: 0,  # 4th day : the validated dish shouldn't change
            5: 0,  # 5th day : the forced dish shouldn't change
            6: 0   # Meta planning : shouldn't change
        }
        
        for dish_i, recipe_i in EXPECTED_RECIPE_PER_DISH.items():
            print("dish_i : ", dish_i, "expected_recipe_i : ", recipe_i)
            self.assertEqual(DishRecipe.objects.get(dish_id=self.mono_dishes[dish_i].id).recipe_id,
                             self.mono_recipes[recipe_i].id)
        
        # Check that classic dish_types don't change
        for classic_dish in self.classic_dishes:
            self.assertEqual(DishRecipe.objects.get(dish_id=classic_dish.id).recipe_id,
                             self.classic_recipes[0].id)
        