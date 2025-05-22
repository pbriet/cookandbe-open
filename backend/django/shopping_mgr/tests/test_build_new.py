from shopping_mgr.models    import ShoppingList
from shopping_mgr.tests     import TestBaseShoppingListTest


class TestBuildNewList(TestBaseShoppingListTest):
    WITH_LIST = False
    FILL_LIST = False
    
    
    def test_build_new(self):
        """
        Test creating a new shopping list with API
        """
        self.assertEqual(ShoppingList.objects.count(), 0)
        
        response = self.client.post('/api/user/%i/shopping_list/build_new' % self.user.id,
                                    {'start_date': "2014-07-08", 'end_date': "2014-07-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "created")
        
        self.assertEqual(ShoppingList.objects.count(), 1)
        
        
    def test_build_new_with_existing_in_middle(self):
        """
        Test creating a new shopping list with API
        But with already a shopping list created within these dates
        """
        self.create_db_shopping_list("2014-07-09", "2014-07-10")
        self.assertEqual(ShoppingList.objects.count(), 1)
        
        response = self.client.post('/api/user/%i/shopping_list/build_new' % self.user.id,
                                    {'start_date': "2014-07-08", 'end_date': "2014-07-11"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "failed")
        
        self.assertEqual(ShoppingList.objects.count(), 1)