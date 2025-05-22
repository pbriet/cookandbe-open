"""
Testing how ustensils are filtering recipes
"""
from django.db.models                       import Count

from common.mock_tools                      import empty_diet_decorator

from hippocrate.tests                       import HpUnidishApiTest

from planning_mgr.models                    import DishRecipe

from recipe_mgr.models                      import Recipe

from collections                            import defaultdict

class TestUstensilApi(HpUnidishApiTest):
    NB_RECIPES = 4

    def setUp(self):
        # Creating ustensil
        self.knife  = self.create_db_ustensil(name = "knife", default_check = True)
        self.spoon  = self.create_db_ustensil(name = "spoon", default_check = False)
        # Parent initialization
        super().setUp()

    def init_recipe(self, recipe_number, *args, **kargs):
        # 1 recipe needs a spoon, 1 needs a knife, 1 needs both and 1 needs none
        recipe = super().init_recipe(recipe_number, *args, **kargs)
        if recipe_number in (0, 1):
            recipe.ustensils.add(self.knife)
        if recipe_number in (1, 2):
            recipe.ustensils.add(self.spoon)
        recipe.save()
        return recipe

    @empty_diet_decorator
    def test_no_ustensil(self):
        self.assertEqual(0, self.user.ustensils.count())
        # Generating planning
        response = self._fill_through_api()
        self.assertEqual(response.status_code, 201)
        # All recipes should require no ustensil
        query = Recipe.objects.filter(dishrecipe__dish__meal_slot__day__user = self.user).annotate(nb_dishrecipe = Count('dishrecipe'))
        self.assertEqual(1, query.count())
        for recipe in query:
            self.assertEqual(0, recipe.ustensils.count())

    @empty_diet_decorator
    def test_ustensil_filter(self):
        self.client.post('/api/user/%i/add_ustensil' % (self.user.id), {"ustensil_id": self.spoon.id})
        self.assertEqual([self.spoon, ], list(self.user.ustensils.all()))
        # Generating planning
        response = self._fill_through_api()
        # Controls
        self.assertEqual(response.status_code, 201)
        # All recipes should require no ustensil or a spoon
        query = Recipe.objects.filter(dishrecipe__dish__meal_slot__day__user = self.user).annotate(nb_dishrecipe = Count('dishrecipe'))
        self.assertEqual(2, query.count())
        for recipe in query:
            self.assertTrue(recipe.ustensils.count() == 0 or \
                           (recipe.ustensils.count() == 1 and list(recipe.ustensils.all())[0] == self.spoon))
