
from common.model                    import reload_object
from common.test                     import TestAPIWithLogin

class TestRecipeUrlKey(TestAPIWithLogin):
    """
    Testing that a url_key is automatically generated when creating/updating a recipe,
    and its content
    """
    EXPECTED_KEY = "this-is-my-bldy-recpe-arc-en-ciel-a-l-orange-44"
    INITIALIZE_RECIPE_INDEXER = True
    
    def setUp(self):
        super().setUp()
        self.recipe = self.create_db_recipe(" this is my bl**dy rec!pé arc-en-ciel à     l'orange \\   ", id=44)
        
    def _check_equals(self, expected):
        """
        Check that url key is equals to expected, before and after DB reload
        """
        self.assertEqual(self.recipe.url_key, expected)
        reload_object(self.recipe)
        self.assertEqual(self.recipe.url_key, expected)
        
    
    def test_valid_after_creation(self):
        self._check_equals(self.EXPECTED_KEY)
        
    def test_no_change_on_update(self):
       
        # Field that has nothing to do with url_key
        self.recipe.source_url = "www.plop.fr"
       
        self.recipe.save()
        self._check_equals(self.EXPECTED_KEY)
    
    def test_change_on_update(self):
        
        self.recipe.name = "new name"
        self.recipe.save()
        
        self._check_equals("new-name-44")
        
        
    def test_retrieve_from_api(self):
        response = self.client.get('/api/recipe/from_key/toto')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['exists'], False)
        
        response = self.client.get('/api/recipe/from_key/%s' % self.EXPECTED_KEY)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['exists'], True)