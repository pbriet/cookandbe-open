from common.test                    import TestAPIWithLogin, add_permissions
from recipe_mgr.models              import Recipe
from user_mgr.models                import User
from mock                           import patch
from optalim.config                 import Config
from optalim.settings               import MEDIA_ROOT
import copy
import json
import storages.backends.s3boto3
import django.http.request

class TestRecipePhotoAPI(TestAPIWithLogin):
    PASSWORD = "snowwhite"
    DEFAULT_PHOTO_PATH = "/bob/photo1.png"
    ANOTHER_PHOTO_PATH = "/bob/photo2.png"
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        TestAPIWithLogin.setUp(self)
        # Non admin user
        self.simple_user = self.create_db_user(password = self.PASSWORD)
        # Creating recipe
        response = self.client.post('/api/recipe', self.get_recipe_attributes())
        self.assertEqual(response.status_code, 201)
        self.simple_recipe = Recipe.objects.get()
        # Setting default photo path
        self.simple_recipe.photo = self.DEFAULT_PHOTO_PATH
        self.simple_recipe.save()
        self.assertTrue(self.DEFAULT_PHOTO_PATH != self.ANOTHER_PHOTO_PATH)

    def get_recipe_attributes(self, **kargs):
        values = copy.copy({
            'name' : "my test recipe",
            'author': self.simple_user.id,
            'nb_people': 3,
            'difficulty': 3,
            'price': 3
        })
        values.update(**kargs)
        return values

    @add_permissions('admin')
    def test_update_with_photo(self):
        # No photo url change should be fine
        response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(photo = MEDIA_ROOT + self.DEFAULT_PHOTO_PATH))
        self.assertEqual(response.status_code, 200)
        # Photo url change via update not allowed
        response = self.client.put('/api/recipe/%i' % self.simple_recipe.id, self.get_recipe_attributes(photo = MEDIA_ROOT + self.ANOTHER_PHOTO_PATH))
        self.assertEqual(response.status_code, 403)

    def test_upload_img(self):
        # TODO !
        # response = self.client.post('/api/recipe/%i/upload_img' % self.simple_recipe.id)
        self.assertTrue(True)
