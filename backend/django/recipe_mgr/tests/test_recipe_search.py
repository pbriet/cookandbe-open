from common.test                        import TestAPIWithLogin, add_permissions
from recipe_mgr.models                  import CookingMethod, DishType, RecipeDishType, Recipe
from recipe_mgr.models                  import Food, RecipeInstruction, Ingredient
from user_mgr.models                    import User
from mock                               import patch
import copy

class TestRecipeSearchAPI(TestAPIWithLogin):
    ALL_RECIPES = ('simple carrots', 'carrots with rice', 'cake', 'bloody carrots', 'carrot cake', 'his carrot cake')
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.recipes = [
            self.create_db_recipe(name=name)
            for name in self.ALL_RECIPES]

        self.other_dish_type = self.create_db_dishtype()

        # Carrot cake has a different dish type
        self.recipes[-2].dish_types.clear()
        RecipeDishType.objects.create(recipe=self.recipes[-2], dish_type=self.other_dish_type)

        # Simple carrots is not published
        self.recipes[0].status = Recipe.STATUS_VALIDATED
        self.recipes[0].save()

        # Carrots with rice is not even saved
        self.recipes[1].status = Recipe.STATUS_CREATING
        self.recipes[1].save()

        # His carrot cake is not published and written by somebody else
        self.user2 = self.create_db_user()
        self.recipes[-1].author = self.user2
        self.recipes[-1].status = Recipe.STATUS_VALIDATED
        self.recipes[-1].save()

        # Simple carrots and carrot cake have ingredients
        for recipe in (self.recipes[0], self.recipes[-2]):

            some_food1 = self.create_db_food()
            some_food2 = self.create_db_food()
            self.create_db_ingredient(recipe, some_food1, 10)
            self.create_db_ingredient(recipe, some_food2, 10)

    def _test_search(self, keyword, expected_results, kargs = None):
        if kargs is None:
            kargs = {}
        response = self.client.get('/api/recipe/search/' + keyword, kargs)
        self.assertEqual(response.status_code, 200)
        results_names = tuple([r['name'] for r in response.data['results']])
        self.assertEqual(results_names, tuple(expected_results))

    def test_search_empty(self):
        self._test_search('plop', [])

    def test_search_carrot(self):
        with self.assertNumQueries(5):
            self._test_search('carrot', ['bloody carrots', 'carrot cake', 'simple carrots'], {'details': 'ingredients'})

        # with self.assertNumQueries(5):
        self._test_search('carrot', ['bloody carrots', 'carrot cake', 'simple carrots'], {'details': 'full'})


    def test_search_carrot_including_validated(self):
        self._test_search('carrot', ['bloody carrots', 'carrot cake', 'his carrot cake', 'simple carrots'],
                          {'min_status': Recipe.STATUS_VALIDATED})

    def test_search_carrot_all(self):
        self._test_search('carrot', ['bloody carrots', 'carrot cake', 'carrots with rice', 'his carrot cake', 'simple carrots'],
                          {'min_status': Recipe.STATUS_CREATING})

    def test_search_carrot_without_own_recipes(self):
        self._test_search('carrot', ['bloody carrots', 'carrot cake'],
                          {'include_own_recipes': False})

    def test_search_carrot_offset(self):
        self._test_search('carrot', ['carrot cake', 'simple carrots'], {'offset': 1})

    def test_search_carrot_limit(self):
        self._test_search('carrot', ['bloody carrots', 'carrot cake'], {'limit': 2})

    def test_search_dishtype(self):
        self._test_search('carrot', ['carrot cake'],
                          {'dish_type_ids': [self.other_dish_type.id]})

    def test_search_internal_recipe(self):
        self.apple_recipe = self.create_db_recipe(name = "apple juice", internal = False)
        self._test_search('apple', ["apple juice"])
        self.apple_recipe.internal = True
        self.apple_recipe.save()
        self._test_search('apple', [])

    def test_search_author(self):
        my_recipes = ('bloody carrots', 'cake', 'carrot cake', 'carrots with rice', 'simple carrots')
        self._test_search('', my_recipes, {'author_id': self.user.id})
        r1 = self.create_db_recipe(author = self.user2, name = 'alcool carrrots')
        r2 = self.create_db_recipe(author = self.user,  name = 'alcool carots')
        r3 = self.create_db_recipe(author = self.user,  name = 'yumiam')

        expected_recipe_names = (r2.name, ) + my_recipes + (r3.name, )
        self._test_search('', expected_recipe_names, {'author_id': self.user.id})

        #Test retrieving personal recipes through dedicated api
        response = self.client.get('/api/user/%i/personal_recipes' % self.user.id)
        self.assertEqual(response.status_code, 200)
        results_names = tuple(sorted([r['name'] for r in response.data['results']]))
        self.assertEqual(results_names, expected_recipe_names)

        expected_recipe_ids = sorted(r.id for r in Recipe.objects.filter(name__in=expected_recipe_names))
        response = self.client.get('/api/user/%i/personal_recipes' % self.user.id, {'ids_only': True})
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(response.data['results']), expected_recipe_ids)


    def test_search_order(self):
        recipes = ('bloody carrots', 'cake', 'carrot cake', 'simple carrots')
        self._test_search('c', recipes, {'order_by': "name"})
        r1 = self.create_db_recipe(author = self.user,  name = 'yuc')
        r2 = self.create_db_recipe(author = self.user2, name = 'alcool carots')
        self._test_search('c', (r2.name, ) + recipes + (r1.name, ), {'order_by': "name"})
        time_recipes = ('simple carrots', 'cake', 'bloody carrots', 'carrot cake', r1.name, r2.name)
        self._test_search('c', time_recipes, {'order_by': "creation_date"})
        self._test_search('c', reversed(time_recipes), {'order_by': "-creation_date"})


    def test_personal_recipes_permission_denied(self):
        """
        Test retrieving personal recipes through dedicated api
        """
        response = self.client.get('/api/user/%i/personal_recipes' % self.user2.id)
        self.assertEqual(response.status_code, 403)
