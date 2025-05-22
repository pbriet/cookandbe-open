from common.test                    import TestAPIWithLogin
from recipe_mgr.models              import Recipe
from mock                           import patch

class TestTag(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.recipe = self.create_db_recipe()
        self.meat = self.create_db_recipe_tag("meat")
        self.beef = self.create_db_recipe_tag("beef", parent=self.meat)
        self.cooked_beef = self.create_db_recipe_tag("slowly cooked beef", parent=self.beef)

    def test_api_categories(self):
        response = self.client.get('/secure/api/recipe_tag')
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(sorted([d['name'] for d in response.data]), ["beef", "meat", "slowly cooked beef"])


    def test_api_categories_hierarchized(self):
        response = self.client.get('/secure/api/recipe_tag', {"tree": 1})
        self.assertEqual(response.status_code, 200)
        print(response.data)
        self.assertEqual(response.data, [{
                                          "name": "meat",
                                          'url_key': 'meat-%i' % self.meat.id,
                                          "id": self.meat.id,
                                          "children": [
                                              {
                                                  "name": "beef",
                                                  'url_key': 'beef-%i' % self.beef.id,
                                                  "id": self.beef.id,
                                                  "children": [
                                                      {
                                                          "name": "slowly cooked beef",
                                                          'url_key': 'slowly-cooked-beef-%i' % self.cooked_beef.id,
                                                          "id": self.cooked_beef.id,
                                                          "children": []
                                                       }]
                                               }]
                                           }])

    def test_recursive_loop(self):
        """
        Test invalid hierarchy when child is parent of his parent
        """
        self.meat.parent = self.cooked_beef
        self.meat.save()
        
        self.assertRaises(AssertionError, self.client.get, '/secure/api/recipe_tag', {"tree": 1})

    def test_recursive_loop2(self):
        """
        Test invalid hierarchy when child is parent of his parent
        """
        self.beef.parent = self.cooked_beef
        self.beef.save()

        self.assertRaises(AssertionError, self.client.get, '/secure/api/recipe_tag', {"tree": 1})