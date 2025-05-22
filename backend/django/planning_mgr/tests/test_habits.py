from common.test                import TestAPIWithLogin
from planning_mgr.models        import MealType, Dish, MetaPlanning
from recipe_mgr.models          import DishType

class TestHabitudes(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        self.init_db_profile_eater()

        self.lunch = MealType.objects.get(name="Déjeuner")

        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)

    def test_default_nb_queries(self):
        with self.assertNumQueries(15):
            self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.lunch.id))

    def test_set_meal_speed(self):
        meta_planning = MetaPlanning.objects.get(user_id = self.user.id)

        response = self.client.post('/api/user/%i/meal_type/%i/set_meal_speed' % (self.user.id, self.lunch.id),
                                        {'value': 1})
        self.assertEqual(response.status_code, 200)

        for day in meta_planning.days.all():
            for meal_slot in day.meal_slots.all():
                if meal_slot.meal_type_id == self.lunch.id:
                    self.assertEqual(meal_slot.speed, 1)

    def test_default_serialization(self):
        response = self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.lunch.id))
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.data['suggest']['enabled'])
        self.assertEqual(len(response.data['suggest']['dish_types']), 7)
        enabled_dishtypes = []
        for dt in response.data['suggest']['dish_types']:
            if dt['enabled']:
                enabled_dishtypes.append(dt['name'])
        self.assertEqual(sorted(enabled_dishtypes),
                         ['Dessert', 'Fromage', 'Fruit', 'Plat complet'])

        self.assertTrue(response.data['static']['recipe'] is None)

class TestHabitudesModification(TestAPIWithLogin):

    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        self.init_db_profile_eater()

        # AGG = 1 + 2
        self.dish_type_agg, self.dt1, self.dt2 = self.create_db_dishtype_aggregated()
        self.dt3 = self.create_db_dishtype(name="dt3")

        self.planning = self.create_db_meta_planning(with_n_days=1)
        self.meal_type = self.create_db_mealtype(force_suggest=True)
        for dish_type, optional in (self.dish_type_agg, False), (self.dt3, True):
            self.create_db_mealdishoption(self.meal_type, dish_type, default_optional = optional)

        self.meal_slot = self.create_db_mealslot(self.planning.sorted_days[0], meal_type=self.meal_type)

        self.recipe1 = self.create_db_recipe(dish_types=[self.dish_type_agg, self.dt1, self.dt3])
        self.recipe2 = self.create_db_recipe(dish_types=[self.dish_type_agg, self.dt1, self.dt3])

    def test_serialization(self):

        response = self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.meal_type.id))
        self.assertEqual(response.status_code, 200)

        enabled_dishtypes = [dt for dt in response.data['suggest']['dish_types'] if dt['enabled']]
        self.assertEqual(enabled_dishtypes, [])

        # Only the aggregated dishtype and the independant one (dt3) should be listed
        all_dishtypes_ids = sorted([dt['id'] for dt in response.data['suggest']['dish_types']])
        self.assertEqual(all_dishtypes_ids,
                         [self.dish_type_agg.id, self.dt3.id])

    def _enable_dt(self, dt, expected_status_code=200):
        """
        Helper: calls the API to enable a dishtype
        """
        response = self.client.post('/api/user/%i/meal_type/%i/enable_meal_dish' % (self.user.id, self.meal_type.id),
                                    {'dish_type_id': dt.id})
        self.assertEqual(response.status_code, expected_status_code)

    def _disable_dt(self, dt, expected_status_code=200):
        """
        Helper: calls the API to disable a dishtype
        """
        response = self.client.post('/api/user/%i/meal_type/%i/disable_meal_dish' % (self.user.id, self.meal_type.id),
                                    {'dish_type_id': dt.id})
        self.assertEqual(response.status_code, expected_status_code)

    def _force_recipe(self, dt, recipe_id, expected_status_code=200):
        """
        Helper: calls the API to set a forced_recipe on a given dish type
        """
        response = self.client.post('/api/user/%i/meal_type/%i/force_recipe' % (self.user.id, self.meal_type.id),
                                    {'dish_type_id': dt.id,
                                    'forced_recipe_id': recipe_id})
        self.assertEqual(response.status_code, expected_status_code)

    def _get_enabled_dts(self):
        """
        Helper: calls the API to retrieve what are the dish types enabled for the meal_type
        """
        response = self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.meal_type.id))
        self.assertEqual(response.status_code, 200)
        return sorted([dt['id'] for dt in response.data['suggest']['dish_types'] if dt['enabled']])

    def _get_dt_details(self, dish_type):
        """
        Helper : calls the API, and returns status for a given dish type for the meal_type we are testing
        """
        response = self.client.get('/api/user/%i/meal_type/%i/habits' % (self.user.id, self.meal_type.id))
        self.assertEqual(response.status_code, 200)
        for dt in response.data['suggest']['dish_types']:
            if dt['id'] == dish_type.id:
                return dt
        assert False, "couldn't find dish_type in habits"

    def _sorted_dish_dt_ids(self):
        """
        Return the list of ordered dish_type_ids from every dishes in the DB
        """
        return sorted(d.dish_type_id for d in Dish.objects.all())

    def test_enable_disable_dish(self):

        # Enabling dish type 3 ("solo")
        self._enable_dt(self.dt3)
        self.assertEqual(self._get_enabled_dts(), [self.dt3.id])
        self.assertEqual(Dish.objects.filter(optional=True).count(), 1)

        # Re-enabling dish type 3 ("solo") - should change nothing
        self._enable_dt(self.dt3)
        self.assertEqual(self._get_enabled_dts(), [self.dt3.id])
        self.assertEqual(Dish.objects.filter(optional=True).count(), 1)

        # Enabling dish type agg
        self._enable_dt(self.dish_type_agg)
        self.assertEqual(self._get_enabled_dts(), [self.dish_type_agg.id, self.dt3.id])
        self.assertEqual(Dish.objects.filter(optional=True).count(), 1)

        # At this point, we should have two dishes : aggregated and 3
        self.assertEqual(self._sorted_dish_dt_ids(), [self.dish_type_agg.id, self.dt3.id])

        # Disabling dish type 1 (not enabled)
        self._disable_dt(self.dt1, 400)
        self.assertEqual(self._get_enabled_dts(), [self.dish_type_agg.id, self.dt3.id])

        self.assertEqual(Dish.objects.count(), 2)
        self.assertEqual(self._sorted_dish_dt_ids(), [self.dish_type_agg.id, self.dt3.id])

        # Disabling dish type agg
        self._disable_dt(self.dish_type_agg)
        self.assertEqual(self._get_enabled_dts(), [self.dt3.id])

        self.assertEqual(Dish.objects.count(), 1)
        self.assertEqual(self._sorted_dish_dt_ids(), [self.dt3.id])

        self.assertEqual(Dish.objects.filter(optional=True).count(), 1)

    def test_force_recipe(self):

        # Forcing on non-aggregated non-enabled dish_type -> definitely fail !
        self._force_recipe(self.dt1, self.recipe1.id, 400)

        # Enabling dish type 1
        self._enable_dt(self.dt3)

        self._force_recipe(self.dt3, self.recipe1.id)
        self.assertEqual(self._get_dt_details(self.dt3)['forced_recipe']['id'], self.recipe1.id)

        self._force_recipe(self.dt3, self.recipe2.id)
        self.assertEqual(self._get_dt_details(self.dt3)['forced_recipe']['id'], self.recipe2.id)

        self._force_recipe(self.dt3, -1)
        self.assertTrue(self._get_dt_details(self.dt3)['forced_recipe'] is None)

        # Disabling dish type 1 and enabling the aggregated
        self._disable_dt(self.dt3)
        self._enable_dt(self.dish_type_agg)

        # Forcing a recipe on the aggregated dish_type should fail
        self._force_recipe(self.dish_type_agg, self.recipe1.id, 400)
        self.assertTrue(self._get_dt_details(self.dish_type_agg)['forced_recipe'] is None)
