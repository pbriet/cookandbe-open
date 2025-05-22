
from common.model           import reload_object
from common.test            import TestAPIWithLogin, OptalimTest
from mock                   import patch

from recipe_mgr.models      import RecipeRating
from recipe_mgr.tasks       import update_recipe_ratings

class TestRatingsAPI(TestAPIWithLogin):
    """
    Test adding comments/ratings on some recipes
    """
    def setUp(self):
        super().setUp()
        self.other_user = self.create_db_user(email="other@somewhereelse.com")
        self.recipe1 = self.create_db_recipe()
        self.recipe2 = self.create_db_recipe(author=self.other_user)
        
    def test_rate_invalid_recipe(self):
        recipe_id = self.recipe2.id
        self.recipe2.delete()
        response = self.client.post('/api/recipe/%i/rate' % recipe_id,
                                    {'rating': '3'})
        self.assertEqual(response.status_code, 400)
        
    def _check_unique_rating(self, recipe, expected_rating, expected_comment):
        
        ratings = recipe.ratings.all()
        self.assertEqual(len(ratings), 1)
        rating = ratings[0]
        self.assertEqual(rating.user_id, self.user.id)
        self.assertEqual(rating.rating, expected_rating)
        self.assertEqual(rating.comment, expected_comment)
        self.assertEqual(rating.moderated_at, None)
        
    def test_cannot_rate_own_recipe(self):
        """
        Cannot rate/comment your own recipe
        """
        response = self.client.post('/api/recipe/%i/rate' % self.recipe1.id,
                                    {'rating': '3', 'comment': 'YaY !'})
        self.assertEqual(response.status_code, 400)
        
    def test_once_then_twice(self):
        # Adding one comment
        response = self.client.post('/api/recipe/%i/rate' % self.recipe2.id,
                                    {'rating': '3', 'comment': 'YaY !'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.recipe2.ratings.count(), 1)
        
        self._check_unique_rating(self.recipe2, 3, 'YaY !')
        
        # Adding one comment again, on the same recipe
        response = self.client.post('/api/recipe/%i/rate' % self.recipe2.id,
                                    {'rating': '4', 'comment': 'YaY 2'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.recipe2.ratings.count(), 1)
        
        self._check_unique_rating(self.recipe2, 3, 'YaY !')
        
        # Once again, but with 'replace'
        response = self.client.post('/api/recipe/%i/rate' % self.recipe2.id,
                                    {'rating': '4', 'comment': 'YaY 2', 'replace': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.recipe2.ratings.count(), 1)
        
        self._check_unique_rating(self.recipe2, 4, 'YaY 2')


class BaseTestRatings(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.recipe1 = self.create_db_recipe("banana !")
        self.recipe2 = self.create_db_recipe("pink orange")
        self.recipe3 = self.create_db_recipe("alcoholic goulash")
        
        self.other_user = self.create_db_user(email="other@somewhereelse.com")
        
        self.rating1 = self.create_db_rating(self.recipe1, self.user, 5, 'Amazing')
        self.rating2 = self.create_db_rating(self.recipe1, self.other_user, 1, 'Terrible', moderated_at=None)
        self.rating3 = self.create_db_rating(self.recipe2, self.user, 4, 'Lovely')
        self.rating4 = self.create_db_rating(self.recipe2, self.other_user, 3, 'Tolerable')
   
    def assert_ratings_list(self, response, expected):
        """
        Extract from the response a list of tuples (comment, rating), and compare to the given value
        """
        elts = [(elt['comment'], elt['rating']) for elt in response.data['data']]
        self.assertEqual(elts, expected)

class TestUserRatingAPI(BaseTestRatings):
    """
    Test retrieving the user rating
    """
    def test_user_rating_rated(self):
        response = self.client.get('/api/recipe/%i/user_rating' % self.recipe2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['rated'], True)
        self.assertEqual(response.data['rating'], 4)
        
        response = self.client.get('/api/recipe/%i/user_rating' % self.recipe3.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['rated'], False)


class TestRatingsListAPI(BaseTestRatings):
    """
    Test listing comments/ratings on some recipes
    """
        
    def testing_list_recipe_ratings(self):
        """
        Test listing ratings on a recipe
        """
        
        response = self.client.get('/api/recipe/%i/ratings' % self.recipe2.id)
        self.assertEqual(response.status_code, 200)
        
        self.assert_ratings_list(response, [('Tolerable', 3), ('Lovely', 4)])
        
        
    def testing_list_last_ratings(self):
        response = self.client.get('/api/last_ratings')
        self.assertEqual(response.status_code, 200)
        
        # Without the non-moderated one
        self.assert_ratings_list(response, [('Tolerable', 3), ('Lovely', 4), ('Amazing', 5)])
        
        
    def testing_unmoderated(self):
        """
        Testing retrieving the unmoderated comments with a public account
        """
        response = self.client.get('/api/last_ratings', {'moderated': False})
        self.assertEqual(response.status_code, 403)
        
        
class TestRatingsListNotLoggedInAPI(BaseTestRatings):
    LOGIN_ON_STARTUP = False
    def testing_list_recipe_ratings_not_logged(self):
        """
        Test listing ratings when not logged in
        """
        response = self.client.get('/api/recipe/%i/ratings' % self.recipe2.id)
        self.assertEqual(response.status_code, 200)
        
        self.assert_ratings_list(response, [('Tolerable', 3), ('Lovely', 4)])
        
        
        
class TestRatingsModerationAPI(BaseTestRatings):
    """
    Tests related to ratings moderation
    """
    PERMISSIONS = ['reviewer']
    
    def listing_unmoderated(self):
        """
        Testing retrieving the unmoderated comments with a public account
        """
        response = self.client.get('/api/last_ratings', {'moderated': False})
        self.assertEqual(response.status_code, 200)
        
        self.assert_ratings_list(response, [('Terrible', 1),])
    
    
    def test_accept_comment(self):
        response = self.client.post('/secure/api/rating/%i/moderate' % self.rating2.id, {'accept': True})
        self.assertEqual(response.status_code, 200)
        reload_object(self.rating2)
        self.assertTrue(self.rating2.moderated_at is not None)
        self.assertEqual(self.rating2.moderator.id, self.user.id)
        
    def test_reject_without_reason(self):
        response = self.client.post('/secure/api/rating/%i/moderate' % self.rating2.id, {'accept': False})
        self.assertEqual(response.status_code, 400)
        
    def test_already_moderated(self):
        response = self.client.post('/secure/api/rating/%i/moderate' % self.rating1.id, {'accept': True})
        self.assertEqual(response.status_code, 400)
        
    
    @patch('recipe_mgr.views.ratings.sendmail_template')
    def test_reject_comment(self, mock_sendmail_template):
        response = self.client.post('/secure/api/rating/%i/moderate' % self.rating2.id, {'accept': False, 'reason': 'Plop'})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(mock_sendmail_template.call_count, 1)
        
        args, kargs = mock_sendmail_template.call_args
        self.assertEqual(args[1], 'recipe_mgr/templates/rejected_rating.html')
        self.assertEqual(sorted(args[2].keys()), ['comment', 'reason', 'recipe'])
        self.assertEqual(args[2]['reason'], 'Plop')
        self.assertEqual(args[2]['recipe'].name, 'banana !')
        self.assertEqual(args[3], 'Votre commentaire nécessite des modifications')
        self.assertEqual(kargs['users'][0].email, "other@somewhereelse.com")
    
        self.assertEqual(RecipeRating.objects.count(), 3)
        self.assertEqual(RecipeRating.objects.filter(pk=self.rating2.id).count(), 0)
        
        
        
class TestRecipeRatingsUpdated(OptalimTest):
    INITIALIZE_RECIPE_INDEXER = True
    
    def setUp(self):
        super().setUp()
        self.other_user = self.create_db_user()
        self.recipe1 = self.create_db_recipe()
        self.recipe2 = self.create_db_recipe()
        self.recipe3 = self.create_db_recipe()
        
        
        self.create_db_rating(self.recipe2, self.user, 3)
        
        self.create_db_rating(self.recipe3, self.user, 2)
        self.create_db_rating(self.recipe3, self.other_user, 3)
    
    def test_update(self):
        update_recipe_ratings()
        
        for r in self.recipe1, self.recipe2, self.recipe3:
            reload_object(r)
        
        self.assertTrue(self.recipe1.avg_rating is None)
        self.assertEqual(self.recipe1.nb_ratings, 0)
        self.assertEqual(self.recipe2.avg_rating, 3)
        self.assertEqual(self.recipe2.nb_ratings, 1)
        self.assertEqual(self.recipe3.avg_rating, 2.5)
        self.assertEqual(self.recipe3.nb_ratings, 2)
        
        response = self.client.get('/api/recipe/%i/with_ingredients' % self.recipe3.id)
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data['avg_rating'], 2.5)
        self.assertEqual(response.data['nb_ratings'], 2)