
from common.model           import reload_object
from common.test            import TestAPIWithLogin
from planning_mgr.models    import Dish


class TestValidateDish(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        # We create 3 simple dish types, and one aggregated (1 + 2)
        self.dt3 = self.create_db_dishtype()
        self.dt_agg, self.dt1, self.dt2 = self.create_db_dishtype_aggregated()
        
        # DT3 and DT AGG are allowed for this meal_type
        self.mealtype = self.create_db_mealtype(dish_types=[self.dt3, self.dt_agg])

        # 1 day, 1 meal_slot, 2 dishes
        day = self.create_db_day()
        self.meal_slot = self.create_db_mealslot(day, meal_type=self.mealtype)

        self.agg_dish = self.create_db_dish(self.meal_slot, self.dt_agg, order=0)
        self.simple_dish = self.create_db_dish(self.meal_slot, self.dt3, order=1)

        # Recipes for each dish type
        self.recipe_dt1     = self.create_db_recipe(dish_types=[self.dt1])
        self.recipe_dt2     = self.create_db_recipe(dish_types=[self.dt2])
        self.recipe_dt3     = self.create_db_recipe(dish_types=[self.dt3])
        self.recipe_dt_agg  = self.create_db_recipe(dish_types=[self.dt_agg])
   
    def _reload_dishes(self):
        for d in (self.agg_dish, self.simple_dish):
            reload_object(d)
        
    def test_validate_simple(self):
        # Assign 1 recipe to each dish
        self.create_db_dishrecipe(self.agg_dish, self.recipe_dt_agg)
        self.create_db_dishrecipe(self.simple_dish, self.recipe_dt3)
       
        # Validate the aggregated one
        response = self.client.post('/api/user/%i/validate_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipe_dt_agg.id})
        self.assertEqual(response.status_code, 200)
        self._reload_dishes()
        self.assertEqual(self.agg_dish.order, 0)
        self.assertEqual(self.simple_dish.order, 1)
        self.assertEqual(self.agg_dish.dishrecipe_set.filter(validated=True).count(), 1)
        self.assertEqual(self.simple_dish.dishrecipe_set.filter(validated=True).count(), 0)
        
       
        # Validate the simple one
        response = self.client.post('/api/user/%i/validate_dish/%i' % (self.user.id, self.simple_dish.id),
                                    {'recipe_id': self.recipe_dt3.id})
        self.assertEqual(response.status_code, 200)
        self._reload_dishes()
        self.assertEqual(self.agg_dish.order, 0)
        self.assertEqual(self.simple_dish.order, 1)
        self.assertEqual(self.agg_dish.dishrecipe_set.filter(validated=True).count(), 1)
        self.assertEqual(self.simple_dish.dishrecipe_set.filter(validated=True).count(), 1)
    
    def _check_post_splitted_validation(self):
        dishes = list(Dish.objects.all())
        self.assertEqual(len(dishes), 3)
        dish_orders = sorted([dish.order for dish in dishes])
        self.assertEqual(dish_orders, [0, 1, 2])
        dish_dish_types = sorted([dish.dish_type_id for dish in dishes])
        self.assertEqual(dish_dish_types, [self.dt3.id, self.dt1.id, self.dt2.id])
    
    def test_validate_part_of_aggregated1(self):
        # Assign 1 recipe to simple dish, and 2 to the aggregated one
        self.create_db_dishrecipe(self.agg_dish, self.recipe_dt1, order=1)
        self.create_db_dishrecipe(self.agg_dish, self.recipe_dt2, order=2)
        self.create_db_dishrecipe(self.simple_dish, self.recipe_dt3)
        
        # Validate the first one
        response = self.client.post('/api/user/%i/validate_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipe_dt1.id})
        self.assertEqual(response.status_code, 200)
        self._reload_dishes()
        self.assertEqual(self.agg_dish.order, 0)
        self.assertEqual(self.simple_dish.order, 2)
        
        self.assertEqual(self.agg_dish.dish_type_id, self.dt1.id)
        self._check_post_splitted_validation()
        
    def test_validate_part_of_aggregated2(self):
        # Assign 1 recipe to simple dish, and 2 to the aggregated one
        self.create_db_dishrecipe(self.agg_dish, self.recipe_dt1, order=1)
        self.create_db_dishrecipe(self.agg_dish, self.recipe_dt2, order=2)
        self.create_db_dishrecipe(self.simple_dish, self.recipe_dt3)
        
        # Validate the second one
        response = self.client.post('/api/user/%i/validate_dish/%i' % (self.user.id, self.agg_dish.id),
                                    {'recipe_id': self.recipe_dt2.id})
        self.assertEqual(response.status_code, 200)
        self._reload_dishes()
        self.assertEqual(self.agg_dish.order, 1)
        self.assertEqual(self.simple_dish.order, 2)
        
        self.assertEqual(self.agg_dish.dish_type_id, self.dt2.id)
        self._check_post_splitted_validation()
        