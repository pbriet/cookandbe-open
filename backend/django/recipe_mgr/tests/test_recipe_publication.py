from common.test            import TestAPIWithLogin
from recipe_mgr.models      import Recipe
from mock                   import patch

class TestPublicationRejectAPI(TestAPIWithLogin):
    PERMISSIONS = ['reviewer']
    
    def setUp(self):
        super().setUp()
        
        self.author = self.create_db_user(email="plops@somewhere.tk")
        
        self.recipe_reviewing = self.create_db_recipe("Recipe being reviewed", status=Recipe.STATUS_REVIEWING,
                                                      author=self.author)
        
        self.recipe_validated = self.create_db_recipe("Recipe not being reviewed", status=Recipe.STATUS_VALIDATED,
                                                      author=self.author)
        
    def test_rejecting_invalid(self):
        
        response = self.client.post('/secure/api/recipe/%i/reject_publication' % self.recipe_validated.id,
                                    {'reason': 'plop'})
        self.assertEqual(response.status_code, 400)
        
    @patch('recipe_mgr.views.recipe.sendmail_template')
    def test_rejecting_valid(self, mock_sendmail_template):
        response = self.client.post('/secure/api/recipe/%i/reject_publication' % self.recipe_reviewing.id,
                                    {'reason': 'plop'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(mock_sendmail_template.call_count, 1)
        
        args, kargs = mock_sendmail_template.call_args
        self.assertEqual(args[1], 'recipe_mgr/templates/rejected_publication.html')
        self.assertEqual(sorted(args[2].keys()), ['reason', 'recipe'])
        self.assertEqual(args[2]['reason'], 'plop')
        self.assertEqual(args[2]['recipe'].name, 'Recipe being reviewed')
        self.assertEqual(args[3], 'La publication de votre recette a été refusée')
        self.assertEqual(kargs['users'][0].email, "plops@somewhere.tk")
    
    
    @patch('recipe_mgr.views.recipe.sendmail_template')
    def test_publish(self, mock_sendmail_template):
        response = self.client.post('/secure/api/recipe/%i/publish' % self.recipe_validated.id)
        self.assertEqual(response.status_code, 400) # Recipe has wrong status
        
        response = self.client.post('/secure/api/recipe/%i/publish' % self.recipe_reviewing.id)
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(mock_sendmail_template.call_count, 1)
        
        args, kargs = mock_sendmail_template.call_args
        self.assertEqual(args[1], 'recipe_mgr/templates/publication.html')
        self.assertEqual(sorted(args[2].keys()), ['recipe'])
        self.assertEqual(args[2]['recipe'].name, 'Recipe being reviewed')
        self.assertEqual(args[3], 'Félicitations : votre recette a été publiée')
        self.assertEqual(kargs['users'][0].email, "plops@somewhere.tk")