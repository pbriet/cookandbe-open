from common.test                        import TestAPIWithLogin
from planning_mgr.models                import Dish, MealSlot, MetaPlanning, MealSlotEater, MealType
from planning_mgr.controller.dish       import factorize_and_order_dishes
from recipe_mgr.models                  import DishTypeAggregation
from recipe_mgr.models                  import DishType
import json
import copy

class TestFactorizeDishes(TestAPIWithLogin):
    """
    Tests the method that group together dishtypes that should be aggregated
    """
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        
        self.dt1 = self.create_db_dishtype(name="dt1")
        self.dt4 = self.create_db_dishtype(name="dt4")
        # AGG = 2 + 3
        self.dish_type_agg, self.dt2, self.dt3 = self.create_db_dishtype_aggregated()

        planning = self.create_db_planning()
        self.days = planning.sorted_days

        self.meal_type = self.create_db_mealtype(dish_types=[self.dt1, self.dt2, self.dt3, self.dt4])
        self.meal_slot = self.create_db_mealslot(self.days[0], meal_type=self.meal_type)


    def _get_dish_type_ids_array(self):
        """
        Helper, returns dish type ids of the dishes
        """
        return [dish.dish_type_id for dish in sorted(self.meal_slot.dishes.all(), key=lambda x: x.dish_type_id)]

        
    def test_basic(self):
        """
        Basic: no aggregation
        """
        dish1 = self.create_db_dish(self.meal_slot, self.dt1)
        dish2 = self.create_db_dish(self.meal_slot, self.dt2)
        factorize_and_order_dishes(self.meal_slot)

        self.assertEqual(self._get_dish_type_ids_array(), [self.dt1.id, self.dt2.id])
        
    def test_simple_regroup(self):
        """
        simple aggregation, one next to the other
        """
        dish1 = self.create_db_dish(self.meal_slot, self.dt1)
        dish2 = self.create_db_dish(self.meal_slot, self.dt2)
        dish3 = self.create_db_dish(self.meal_slot, self.dt3)

        factorize_and_order_dishes(self.meal_slot)

        self.assertEqual(self._get_dish_type_ids_array(),
                [self.dt1.id, self.dish_type_agg.id])

