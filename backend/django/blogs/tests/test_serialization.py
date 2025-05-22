from common.test                import TestAPIWithLogin

from blogs.serializers          import BlogSerializer

class TestSerialization(TestAPIWithLogin):
    INITIALIZE_RECIPE_INDEXER = True
    
    def setUp(self):
        super().setUp()
        
        self.blog = self.create_db_blog(title="Mon blog",
                                        url="www.monblog.fr",
                                        facebook="facebook/monblog",
                                        twitter="twitter/monblog",
                                        user=self.user)
        
        self.recipe = self.create_db_recipe()
        
   
    def test_basic_serialization(self):
        
        data = BlogSerializer(self.blog).data
        
        self.assertEqual(data['title'], 'Mon blog')
        self.assertEqual(data['url'], 'www.monblog.fr')
        
    
    def test_recipe_serialization(self):
        
        response = self.client.get('/api/recipe/%i/with_ingredients?include_internal=true' % self.recipe.id)
        
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data['blog']['id'], self.blog.id)
        self.assertEqual(response.data['blog']['title'], 'Mon blog')
        self.assertEqual(response.data['blog']['url'], 'www.monblog.fr')