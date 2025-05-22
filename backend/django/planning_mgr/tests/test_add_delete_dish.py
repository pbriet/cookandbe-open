from common.test            import TestAPIWithLogin
from common.date            import get_tomorrow
from common.model           import reload_object
from django.utils           import timezone
from planning_mgr.models    import MealSlot, Dish
from planning_mgr.models    import Dish
from mock                   import patch
import datetime


class TestDeleteDish(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        # We create 3 simple dish types, and one aggregated (1 + 2)
        self.dt3 = self.create_db_dishtype()
        self.dt_agg, self.dt1, self.dt2 = self.create_db_dishtype_aggregated()
        
        # The first meal slot will have a meal type  (dt3 and dt1 allowed)
        self.mealtype1 = self.create_db_mealtype(dish_types=[self.dt3, self.dt1])
        # External meal
        self.mealplace_external = self.create_db_mealplace("away")

        self.day = self.create_db_day()
        self.meal_slot1 = self.create_db_mealslot(self.day, meal_type=self.mealtype1)
        self.meal_slot2 = self.create_db_mealslot(self.day)

        self.simple_dish = self.create_db_dish(self.meal_slot1, self.dt1)
        self.agg_dish = self.create_db_dish(self.meal_slot2, self.dt_agg)

    def _get_db_dish_list(self):
        """
        Returns a list of tuples (dish_id, dish_type_id) that are in the DB
        """
        return sorted([(d.id, d.dish_type_id) for d in Dish.objects.all()])

    def test_delete_simple_dish(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.simple_dish.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._get_db_dish_list(), [(self.agg_dish.id, self.dt_agg.id)])

    def test_delete_simple_dish_with_dishtype(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.simple_dish.id),
                                    {'dish_type_id': self.dt1.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._get_db_dish_list(), [(self.agg_dish.id, self.dt_agg.id)])

    def test_delete_wrong_dishtype(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.simple_dish.id),
                                    {'dish_type_id': self.dt2.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(self._get_db_dish_list()), 2)

    def test_delete_agg_dish_type_full(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'dish_type_id': self.dt_agg.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._get_db_dish_list(), [(self.simple_dish.id, self.dt1.id)])

    def test_delete_agg_dish_type_partial1(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'dish_type_id': self.dt1.id})
        self.assertEqual(response.status_code, 200)
        dish_list = self._get_db_dish_list()
        self.assertEqual(len(dish_list), 2)
        self.assertEqual([dl[1] for dl in dish_list], [self.dt1.id, self.dt2.id])
        
    def test_delete_agg_dish_type_partial2(self):
        response = self.client.post('/api/user/%i/delete_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'dish_type_id': self.dt2.id})
        self.assertEqual(response.status_code, 200)
        dish_list = self._get_db_dish_list()
        self.assertEqual(len(dish_list), 2)
        self.assertEqual([dl[1] for dl in dish_list], [self.dt1.id, self.dt1.id])

    def test_add_dish_to_external(self):
        self.meal_slot_external = self.create_db_mealslot(self.day, meal_type = self.mealtype1, meal_place = self.mealplace_external)
        response = self.client.post('/api/user/%i/add_dish/%i' % (self.user.id, self.meal_slot_external.id),
                                    {"dish_type_id": self.dt3.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(self._get_db_dish_list()), 2)

    def test_add_dish_to_static(self):
        self.meal_slot_static = self.create_db_mealslot(self.day, meal_type = self.mealtype1, suggest = False)
        response = self.client.post('/api/user/%i/add_dish/%i' % (self.user.id, self.meal_slot_static.id),
                                    {"dish_type_id": self.dt3.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(self._get_db_dish_list()), 2)

    def test_invalidate_dish(self):
        recipe = self.create_db_recipe(dish_types=[self.dt1])
        dr = self.create_db_dishrecipe(self.simple_dish, recipe, validated=True, user=self.user)

        response = self.client.post('/api/user/%i/clear_dish/%i' % (self.user.id, self.simple_dish.id))
        print(response.data)
        self.assertEqual(response.status_code, 200)

        # Reloading from DB
        reload_object(dr)
        self.assertTrue(not dr.validated)
        self.assertTrue(dr.user is None)
        
    def _get_mealslot1_dishtypes(self):
        mealslot1_dishes = Dish.objects.filter(meal_slot=self.meal_slot1).order_by('order')
        return [d.dish_type_id for d in mealslot1_dishes]
    
    def test_add_dish(self):
        response = self.client.post('/api/user/%i/add_dish/%i' % (self.user.id, self.meal_slot1.id),
                                    {"dish_type_id": self.dt3.id})
        print(response.data)
        self.assertEqual(response.status_code, 201)
        
        self.assertEqual(self._get_mealslot1_dishtypes(), [self.dt3.id, self.dt1.id])
        
    def test_add_dish_on_optional_empty(self):
        """
        Test adding a dish in an mealslot that have a dish of same dish_type, optional, and with no dishrecipe
        Expecting it to replace the existing dish
        """
        self.optional_dish = self.create_db_dish(self.meal_slot1, self.dt3, optional=True)
        
        response = self.client.post('/api/user/%i/add_dish/%i' % (self.user.id, self.meal_slot1.id),
                                    {"dish_type_id": self.dt3.id})
        
        # No new dish created
        self.assertEqual(self._get_mealslot1_dishtypes(), [self.dt3.id, self.dt1.id])
        
        # Expecting the optional not be optional anymore
        reload_object(self.optional_dish)
        self.assertEqual(self.optional_dish.optional, False)
        
    def test_add_dish_on_optional_filled(self):
        """
        Test adding a dish in an mealslot that have a dish of same dish_type, optional, with one dishrecipe
        Expecting it to create a new dish
        """
        self.optional_dish = self.create_db_dish(self.meal_slot1, self.dt3, optional=True)
        recipe = self.create_db_recipe(dish_types=[self.dt3])
        self.create_db_dishrecipe(self.optional_dish, recipe)
        
        response = self.client.post('/api/user/%i/add_dish/%i' % (self.user.id, self.meal_slot1.id),
                                    {"dish_type_id": self.dt3.id})
        
        # New dish created
        self.assertEqual(self._get_mealslot1_dishtypes(), [self.dt3.id, self.dt3.id, self.dt1.id])
        
        # Expecting the optional to be still optional
        reload_object(self.optional_dish)
        self.assertEqual(self.optional_dish.optional, True)