from planning_mgr.models        import MealPlace
from shopping_mgr.tests         import TestBaseShoppingListTest
from shopping_mgr.controller    import fill_shopping_list
from shopping_mgr.serializers   import ShoppingListExtendedSerializer

class TestShoppingListGeneration(TestBaseShoppingListTest):
    
    FILL_LIST = False
    
    def test_with_external_meals(self):
        """
        The content of external meals shouldn't be added to the shopping list
        """
        away = MealPlace.objects.create(key="away")
        
        self.meal_slot2.meal_place = away
        self.meal_slot2.save()
        
        fill_shopping_list(self.shopping_list)
        
        # Ensure there is no "things" in the shopping list  (only in meal2)
        res = ShoppingListExtendedSerializer(self.shopping_list).data
        
        items = res[0]['items'] # [0] = unique category
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertTrue('thing' not in item['food']['name'])
        

