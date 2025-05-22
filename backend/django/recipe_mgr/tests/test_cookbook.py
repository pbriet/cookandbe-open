from common.test                        import TestAPIWithLogin
from recipe_mgr.models                  import CookbookRecipe

class TestRecipeBase(TestAPIWithLogin):
    
    def setUp(self):
        super().setUp()
        self.recipe1 = self.create_db_recipe("recipe1")
        self.recipe2 = self.create_db_recipe("recipe2")
        self.recipe3 = self.create_db_recipe("recipe3")
        
    
    def test_cookbook(self):
        # Listing : no recipe in cookbook yet
        response = self.client.get('/api/user/%i/cookbook_recipe' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])
        
        # Add 2 recipes in cookbook
        for recipe in (self.recipe2, self.recipe3):
            response = self.client.post('/api/user/%i/cookbook_recipe' % self.user.id,
                                        {'recipe': recipe.id, 'user': self.user.id})
            self.assertEqual(response.status_code, 201)
        
        # Listing : 2 recipes !
        response = self.client.get('/api/user/%i/cookbook_recipe' % self.user.id)
        self.assertEqual(response.status_code, 200)
        recipe_ids = [cr['recipe'] for cr in response.data]
        self.assertEqual(sorted(recipe_ids), [self.recipe2.id, self.recipe3.id])
        
        # Removing recipe 3
        cr = CookbookRecipe.objects.get(recipe=self.recipe3)
        response = self.client.delete('/api/user/%i/cookbook_recipe/%i' % (self.user.id, cr.id))
        self.assertEqual(response.status_code, 204)
        
        # Listing : 1 recipe remaining !
        response = self.client.get('/api/user/%i/cookbook_recipe' % self.user.id)
        self.assertEqual(response.status_code, 200)
        recipe_ids = [cr['recipe'] for cr in response.data]
        self.assertEqual(recipe_ids, [self.recipe2.id])
        
        # And deleting it with API
        # First doing a mistake (deleting the wrong one)
        response = self.client.post('/api/user/%i/cookbook_recipe/delete_by_recipe_id' % self.user.id, {"recipe_id": self.recipe1.id})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(CookbookRecipe.objects.count(), 1)
        
        # Then really deleting it
        response = self.client.post('/api/user/%i/cookbook_recipe/delete_by_recipe_id' % self.user.id, {"recipe_id": self.recipe2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CookbookRecipe.objects.count(), 0)