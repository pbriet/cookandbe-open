from common.test                     import TestAPIWithLogin, add_permissions
from recipe_mgr.models               import Recipe
from user_mgr.models                 import User
from mock                            import patch
from optalim.config                  import Config
import copy
import json

class TestRecipeStatusAPI(TestAPIWithLogin):
    PASSWORD = "snowwhite"
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        super().setUp()
        # Non admin user
        self.simple_user = self.create_db_user(password = self.PASSWORD)
        # Creating recipe
        response = self.client.post('/api/recipe', self.get_recipe_attributes())
        self.assertEqual(response.status_code, 201)
        self.simple_recipe = Recipe.objects.get()
    
    def get_recipe_attributes(self, **kargs):
        values = copy.copy({
            'name' : "my test recipe",
            'author': self.simple_user.id,
            'nb_people': 3,
            'difficulty': 3,
            'price': 3,
        })
        values.update(**kargs)
        return values

    def test_default_create_status(self):
        self.assertTrue(self.simple_recipe.status == Recipe.STATUS_CREATING)
   
    @add_permissions('admin')
    def test_create_status(self):
        status_modifications = (
            (Recipe.STATUS_CREATING, 201, 201),
            (Recipe.STATUS_VALIDATED, 201, 201),
            (Recipe.STATUS_REVIEWING, 201, 201),
            (Recipe.STATUS_PUBLISHED, 201, 403),
        )
        # Admin mode
        for status, admin_return_code, dummy in status_modifications:
            print("admin creating status", status)
            response = self.client.post('/api/recipe', self.get_recipe_attributes(status = status))
            self.assertEqual(response.status_code, admin_return_code)
        # User mode
        self.change_user(self.simple_user)
        for status, dummy, simple_return_code in status_modifications:
            print("user creating status", status)
            response = self.client.post('/api/recipe', self.get_recipe_attributes(status = status))
            self.assertEqual(response.status_code, simple_return_code)
    
    @add_permissions('admin')
    def test_update_status(self):
        status_modifications = (
            (Recipe.STATUS_CREATING, 200, 200),
            (Recipe.STATUS_VALIDATED, 200, 200),
            (Recipe.STATUS_REVIEWING, 200, 200),
            (Recipe.STATUS_PUBLISHED, 200, 403),
            (Recipe.STATUS_REVIEWING, 200, 200),
            (Recipe.STATUS_VALIDATED, 200, 403), # Regression by users not allowed
            (Recipe.STATUS_CREATING, 200, 403),  # Regression by users not allowed
        )
        # Admin mode
        for status, admin_return_code, dummy in status_modifications:
            print("admin updating status", status)
            response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(status = status))
            self.assertEqual(response.status_code, admin_return_code)
        # User mode
        self.change_user(self.simple_user)
        for status, dummy, simple_return_code in status_modifications:
            print("user updating status", status)
            response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(status = status))
            self.assertEqual(response.status_code, simple_return_code)
        # After publishing, no more user changes
        self.simple_recipe.status = Recipe.STATUS_PUBLISHED
        self.simple_recipe.save()
        for status, dummy1, dummy2 in status_modifications:
            print("user updating published status", status)
            response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(status = status))
            self.assertEqual(response.status_code, 403)
            
    def test_delete_status(self):
        status_modifications = (
            (Recipe.STATUS_CREATING, 204, 204),
            (Recipe.STATUS_VALIDATED, 204, 204),
            (Recipe.STATUS_REVIEWING, 403, 403),
            (Recipe.STATUS_PUBLISHED, 403, 403),
        )
        # Admin mode
        for status, admin_return_code, dummy in status_modifications:
            print("admin deleting status", status)
            recipe = self.create_db_recipe(status = status, author = self.user)
            response = self.client.delete('/api/recipe/%i' % recipe.id)
            self.assertEqual(response.status_code, admin_return_code)
        # User mode
        self.change_user(self.simple_user)
        for status, dummy, simple_return_code in status_modifications:
            print("user deleting status", status)
            recipe = self.create_db_recipe(status = status, author = self.simple_user)
            response = self.client.delete('/api/recipe/%i' % recipe.id)
            self.assertEqual(response.status_code, simple_return_code)
    
    @add_permissions('admin')
    def test_publication(self):
        # Checking infos
        self.assertTrue(self.simple_recipe.status != Recipe.STATUS_PUBLISHED)
        self.assertTrue(self.simple_recipe.publisher is None)
        self.assertTrue(self.simple_recipe.publication_date is None)
        # Publishing recipe
        response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(status = Recipe.STATUS_PUBLISHED))
        self.assertEqual(response.status_code, 200)
        # Checking infos
        self.simple_recipe = Recipe.objects.get() # Updating data
        self.assertEqual(self.simple_recipe.status, Recipe.STATUS_PUBLISHED)
        self.assertEqual(self.simple_recipe.publisher, self.user)
        self.assertTrue(self.simple_recipe.publication_date is not None)

    def test_system_attributes(self):
        values = dict()
        ref_system_attributes = dict()
        for attrName in Recipe.SYSTEM_ATTRIBUTES:
            values[attrName] = "mouhouhaha"
            if attrName == "modification_date": continue # Always modified
            ref_system_attributes[attrName] = getattr(self.simple_recipe, attrName)
        # Trying to change system attributes
        response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(**values))
        # Checking infos
        self.simple_recipe = Recipe.objects.get() # Updating data
        new_system_attributes = dict()
        for attrName in Recipe.SYSTEM_ATTRIBUTES:
            if attrName == "modification_date": continue # Always modified
            new_system_attributes[attrName] = getattr(self.simple_recipe, attrName)
        self.assertEqual(ref_system_attributes, new_system_attributes)
