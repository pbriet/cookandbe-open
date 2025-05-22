
from hippocrate_cpp.core                    import build_solution, load_darwin_config
from hippocrate.tests                   import HpUnidishApiTest
from recipe_mgr.models                  import Recipe


class TestHippocrateCookBook(HpUnidishApiTest):
    """
    Test that solutions are correctly initialized with cookbook recipes and personal recipes
    """
    def init_problem(self):
        
        self.favorite_recipe_1 = self.recipes[6]
        self.favorite_recipe_2 = self.recipes[12]
        self.personal_recipe = self.recipes[13]
        
        # Make it a personal recipe
        self.personal_recipe.author = self.user
        self.personal_recipe.status = Recipe.STATUS_VALIDATED
        self.personal_recipe.save()
        
        # Add favorite recipes to cookbook
        self.create_db_cookbookrecipe(self.favorite_recipe_1)
        self.create_db_cookbookrecipe(self.favorite_recipe_2)
        
        super().init_problem()
        
    
    def test_cookbook(self):
        # Loading a configuration file that prevents the algorithm from creating generations of solutions
        # Only initialization
        load_darwin_config(self.get_fixture_path(__file__, "darwin_no_generation.yml"))
        
        # Ensure that favorite ids are correctly set in problem
        favorite_ids = sorted(self.problem.favorite_recipe_ids)
        self.assertEqual(favorite_ids, [self.favorite_recipe_1.id, self.favorite_recipe_2.id, self.personal_recipe.id])
        
        # Ensure that the solution contains only favorite recipes  (because it's initial solution, and there is no generation)
        solution = self._solve_with_no_api(False)
        recipe_ids = self._get_recipe_ids(solution)
        
        self.assertTrue(len(recipe_ids) > 0)
        
        for recipe_id in recipe_ids:
            self.assertTrue(recipe_id in favorite_ids)