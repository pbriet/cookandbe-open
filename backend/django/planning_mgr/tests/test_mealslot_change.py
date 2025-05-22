from collections                        import defaultdict

from common.model                       import reload_object
from common.test                        import TestAPIWithLogin

import eater_mgr.ratios

from planning_mgr.controller.planning   import build_planning
from planning_mgr.models                import DishRecipe, MealType, MealSlotEater

from recipe_mgr.models                  import DishType

from user_mgr.models                    import User

from mock                               import patch

import datetime

class TestMealSlotChange(TestAPIWithLogin):
    """
    Testing the API to modify a meal slot : speed and eaters
    """

    def setUp(self):
        super().setUp()

        self.day = self.create_db_day(skipped=False)

        # Creating 2 eaters, 2 meals, and 2 dishes in the first meal (with two recipes)
        self.profile1 = self.create_db_profile(nickname = "alice", sex = "female", height = 170, weight = 60, work_score = 1, moving_score = 1, sport_score = 0)
        self.profile2 = self.create_db_profile(nickname = "bob",   sex = "male",   height = 180, weight = 80, work_score = 0, moving_score = 0, sport_score = 2)
        self.eater1 = self.create_db_eater(self.profile1)
        self.eater2 = self.create_db_eater(self.profile2)
        recipe = self.create_db_recipe()

        self.meal_slot1 = self.create_db_mealslot(self.day, speed=1, with_eaters=[self.eater1]) # Eater 1 only
        self.meal_slot2 = self.create_db_mealslot(self.day, speed=4, with_eaters=[self.eater1]) # Eater 1 only

        self.dt = self.create_db_dishtype()
        self.dish1_1 = self.create_db_dish(self.meal_slot1, self.dt)
        self.dish1_2 = self.create_db_dish(self.meal_slot1, self.dt)
        self.dish2   = self.create_db_dish(self.meal_slot2, self.dt)

        # Creating two dish recipes with a ratio of 1.0 (profile 1), on dish1
        self.create_db_dishrecipe(self.dish1_1, recipe, ratio=1.0)
        self.create_db_dishrecipe(self.dish1_2, recipe, ratio=1.0)

        # Creating a dish recipe on dish 2, with 1 eater (profile1)
        self.dishrecipe2 = self.create_db_dishrecipe(self.dish2, recipe, ratio=1.0)

        another_user = User.objects.create_superuser("plup@plop.fr", "plll")
        day = self.create_db_day(user=another_user)
        self.not_my_mealslot = self.create_db_mealslot(day, with_eaters=[]) # No eater
        profile3 = self.create_db_profile(creator=another_user)
        self.not_my_eater = self.create_db_eater(profile3, user=another_user)

    def test_set_speed(self):
        response = self.client.post('/api/meal_slot/%i/set_speed' % (self.meal_slot1.id), {"speed": 3})
        self.assertEqual(response.status_code, 200)
        reload_object(self.meal_slot1)
        self.assertEqual(self.meal_slot1.speed, 3)
        self.assertEqual(response.data['previous_value'], 1)

    def test_invalid_set_speed(self):
        response = self.client.post('/api/meal_slot/%i/set_speed' % (self.meal_slot1.id), {"speed": 12})
        self.assertEqual(response.status_code, 400)
        response = self.client.post('/api/meal_slot/%i/set_speed' % (self.not_my_mealslot.id), {"speed": 1})
        self.assertEqual(response.status_code, 403)

    def _dish_ratio(self, dish):
        return DishRecipe.objects.get(dish=dish).ratio

    @patch.object(eater_mgr.ratios.RatiosCalculator, 'precision_from_nb_eaters', lambda *args, **kargs: 0.5)
    @patch.object(eater_mgr.ratios.RatiosCalculator, 'get_profile_ratios', lambda *args, **kargs: defaultdict(lambda: 1))
    def test_add_remove_eater(self):
        # Profile ratios :
        # 1 : 1.0
        # 2 : 1.328
        with patch.object(eater_mgr.ratios, 'get_theoretical_dish_calories', lambda *x: (0, 1150)):
            # Adding eater1 a second time through the API
            response = self.client.post('/api/meal_slot/%i/add_eater' % (self.meal_slot1.id), {"eater_id": self.eater1.id})
            self.assertEqual(response.status_code, 200)
            # Checking that the ratios are not modified
            self.assertEqual(self._dish_ratio(self.dish1_1), 1.0) # eater1 only  (unchanged)
            self.assertEqual(self._dish_ratio(self.dish1_2), 1.0) # eater1 only  (unchanged)
            self.assertEqual(self._dish_ratio(self.dish2),   1.0) # eater1 only  (unchanged)

            # Add eater2 to meal_slot1
            # Will increase ratio of 132.8%  (1.328 / 1.0)
            # new ratio = 1 * 2.328 = 2.328 (rounded : 2.5)
            response = self.client.post('/api/meal_slot/%i/add_eater' % (self.meal_slot1.id), {"eater_id": self.eater2.id})
            self.assertEqual(response.status_code, 200)
            meal_slot_eaters = sorted([eater.id for eater in self.meal_slot1.eaters.all()])
            self.assertEqual(meal_slot_eaters, sorted([self.eater1.id, self.eater2.id]))

            # Checking that the ratio is correct  (eater1+eater2)
            self.assertEqual(self._dish_ratio(self.dish1_1), 2.5) # eater1+eater2
            self.assertEqual(self._dish_ratio(self.dish1_2), 2.5) # eater1+eater2
            self.assertEqual(self._dish_ratio(self.dish2),   1.0) # eater1 only  (unchanged)

            # Fail to remove eater1 (main_profile)
            response = self.client.post('/api/meal_slot/%i/remove_eater' % (self.meal_slot1.id), {"eater_id": self.eater1.id})
            self.assertEqual(response.status_code, 400)

            # Remove eater2 (not present)
            response = self.client.post('/api/meal_slot/%i/remove_eater' % (self.meal_slot2.id), {"eater_id": self.eater2.id})
            self.assertEqual(response.status_code, 200)

            # Remove eater2
            # Will decrease ratio of 57%  (1.328 / 2.328)
            # New ratio = 2.5 0.43 = 1.075 (rounded: 1.0)
            response = self.client.post('/api/meal_slot/%i/remove_eater' % (self.meal_slot1.id), {"eater_id": self.eater2.id})
            self.assertEqual(response.status_code, 200)
            # Checking that the ratio is correct  (eater1)
            self.assertEqual(self._dish_ratio(self.dish1_1), 1.0) # eater1 only
            self.assertEqual(self._dish_ratio(self.dish1_2), 1.0) # eater1 only
            self.assertEqual(self._dish_ratio(self.dish2),   1.0)# eater1 only (unchanged)

    def test_invalid_add_rm_eater(self):
        response = self.client.post('/api/meal_slot/%i/add_eater' % (self.meal_slot1.id), {"eater_id": self.not_my_eater.id})
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/meal_slot/%i/add_eater' % (self.not_my_mealslot.id), {"eater_id": self.eater1.id})
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/meal_slot/%i/remove_eater' % (self.meal_slot1.id), {"eater_id": self.not_my_eater.id})
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/meal_slot/%i/remove_eater' % (self.not_my_mealslot.id), {"eater_id": self.eater1.id})
        self.assertEqual(response.status_code, 403)

class TestMealSlotMealPlaceChange(TestAPIWithLogin):
    """
    Testing the API to change the meal_place of existing meal_slots
    """
    SUBSCRIPTION_LEVEL = 1

    def setUp(self):
        super().setUp()
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        # Default metaplanning
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        # Reloading user
        self.reload_user()

        # Creating a default monday
        self.day = build_planning(self.user, datetime.date(2014, 9, 1), 1)[0]

    def _assert_at_home(self, meal):
        self.assertEqual(meal.meal_place.key, "home")
        self.assertTrue(meal.dishes.count() >= 1)
        for dish in meal.dishes.all():
            self.assertTrue(dish.dish_type.name != DishType.DT_EXTERNAL)

    def test_from_home_to_external_and_backwards(self):
        """
        Test switching a meal_place from home to external
        """
        dinner = self.day.meal_slots.get(meal_type__nickname='Dîner')
        self._assert_at_home(dinner)
        # Not eating at home Monday evening, but away
        response = self.client.post('/api/user/%i/day/2014-09-01/set_meal_place' % self.user.id,
                                    {'meal_type_id': dinner.meal_type_id, 'meal_place_key': self.places["away"].key})
        self.assertEqual(response.status_code, 200)

        dinner = self.day.meal_slots.get(meal_type__nickname='Dîner')
        self.assertEqual(dinner.meal_place.key, "away")
        self.assertEqual(dinner.dishes.count(), 5) # Entrée-Plat-dessert-fromage-pain

        # And back home

        response = self.client.post('/api/user/%i/day/2014-09-01/set_meal_place' % self.user.id,
                                    {'meal_type_id': dinner.meal_type_id, 'meal_place_key': self.places["home"].key})
        self.assertEqual(response.status_code, 200)

        dinner = self.day.meal_slots.get(meal_type__nickname='Dîner')
        self._assert_at_home(dinner)

    def test_from_home_to_noteat(self):
        dinner = self.day.meal_slots.get(meal_type__nickname='Dîner')
        self._assert_at_home(dinner)

        response = self.client.post('/api/user/%i/day/2014-09-01/set_meal_place' % self.user.id,
                                    {'meal_type_id': dinner.meal_type_id, 'meal_place_key': self.places["donoteat"].key})
        self.assertEqual(response.status_code, 200)

        # No more dinner !
        self.assertEqual(self.day.meal_slots.filter(meal_type__nickname='Dîner').count(), 0)

    def test_from_noteat_to_home(self):
        collation = MealType.objects.get(nickname='Collation')
        # No collation by default
        self.assertEqual(self.day.meal_slots.filter(meal_type=collation).count(), 0)

        response = self.client.post('/api/user/%i/day/2014-09-01/set_meal_place' % self.user.id,
                                    {'meal_type_id': collation.id, 'meal_place_key': self.places["home"].key})
        self.assertEqual(response.status_code, 200)

        # Now there is a collation !
        meal = self.day.meal_slots.get(meal_type=collation)
        self._assert_at_home(meal)

class TestCustomMealslotEaters(TestAPIWithLogin):
    SUBSCRIPTION_LEVEL = 1

    def setUp(self):
        super().setUp()
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        self.mt_breakfast = MealType.objects.get(name="Petit déjeuner")
        self.other_profile = self.create_db_profile()
        self.other_eater = self.create_db_eater(self.other_profile)
        # Default metaplanning
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        # Reloading user
        self.reload_user()
        self._init_habits()

    def _init_habits(self):
        # Changing habits
        self.meta_monday = self.user.meta_planning.days.first()
        self.meta_breakfast = self.meta_monday.meal_slots.get(meal_type = self.mt_breakfast)
        # Default is custom meal (do not suggest) but donoteat
        self.meta_breakfast.meal_place = self.places["donoteat"]
        self.meta_breakfast.suggest = False
        self.meta_breakfast.save()
        self._create_custom_recipe(self.meta_breakfast)
        reload_object(self.meta_monday)

    def _create_custom_recipe(self, meal):
        # Retrieving custom recipe
        dish = meal.dishes.get(dish_type__name = DishType.DT_CUSTOM)
        custom_recipe = dish.dishrecipe_set.get().recipe
        self.assertTrue(custom_recipe.internal)
        # Populating ingredients
        self.food1 = self.create_db_food()
        self.food2 = self.create_db_food()
        self.create_db_food_conversion(self.food1)
        self.create_db_food_conversion(self.food2)
        response = self.client.post('/api/ingredient', {
            'food': self.food1.id,
            'recipe': custom_recipe.id,
            'grams': 100,
            'raw_state': self.raw.id,
            'cooking_method': self.not_cooked.id,
        })
        response = self.client.post('/api/ingredient', {
            'food': self.food2.id,
            'recipe': custom_recipe.id,
            'grams': 100,
            'raw_state': self.raw.id,
            'cooking_method': self.not_cooked.id,
        })
        return custom_recipe

    def test_from_noteat_to_custom_meal(self):
        """
        A problem can occurs when switching meal_place on a custom meal.
        As the metaplanning usually contains all eaters for a meal, we must check that
        only he main eater remains when the planning meal_slot is generated again.
        """
        # Creating a default monday, should be no breakfast
        monday = build_planning(self.user, datetime.date(2014, 9, 1), 1)[0]
        self.assertEqual(monday.meal_slots.filter(meal_type = self.mt_breakfast).count(), 0)
        self.assertEqual(self.meta_breakfast.meal_place.key, self.places["donoteat"].key)
        self.assertEqual(self.meta_breakfast.eaters.count(), 2)

        # Swithing breakfast to home
        response = self.client.post(
            '/api/user/%i/day/2014-09-01/set_meal_place' % self.user.id,
            {'meal_type_id': self.mt_breakfast.id, 'meal_place_key': self.places["home"].key}
        )
        self.assertEqual(response.status_code, 200)
        reload_object(self.meta_breakfast)

        # Checking metaplanning
        self.assertEqual(self.meta_monday.meal_slots.filter(meal_type = self.mt_breakfast).count(), 1)
        self.assertEqual(self.meta_breakfast.eaters.count(), 2)
        self.assertEqual(self.meta_breakfast.meal_place.key, self.places["donoteat"].key)

        # Checking planning
        reload_object(monday)
        self.assertEqual(monday.meal_slots.filter(meal_type = self.mt_breakfast).count(), 1)
        breakfast = monday.meal_slots.get(meal_type = self.mt_breakfast)
        self.assertEqual(breakfast.eaters.count(), 1)
        self.assertEqual(breakfast.meal_place.key, self.places["home"].key)
