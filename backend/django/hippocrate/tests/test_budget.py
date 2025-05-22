"""
Testing how meal time limit is constraining recipes
"""
from hippocrate.tests                       import HpUnidishApiTest
from common.mock_tools                      import empty_diet_decorator, fake_today_decorator
from hippocrate.models.database             import DishRecipe
from hippocrate_cpp.core                        import set_random_seed

import hippocrate.controls.constraint
import hippocrate.controls.filters
from mock import patch

class TestBudgetConstraint(HpUnidishApiTest):
    
    NB_MEALSLOTS            = 2 # 2 meal slots -- 1 per day, with 2 dishes in it.
    NB_RECIPES              = 20

    def init_user(self):
        self.user.budget = 1 # Small budget  (patched in test_budget_limit)
        self.user.save()

    def init_recipes(self):
        super().init_recipes()
        self.cheapRecipes = []
        for i, recipe in enumerate(self.recipes):
            if i > 0 and i % 4 == 0:
                recipe.price = 1 # 4 cheap recipe
                self.cheapRecipes.append(recipe.id)
            else:
                # 8 standards
                if i % 2 == 0:
                    recipe.price = 3 # shouldn't be selected
                else:
                    recipe.price = 5 # Will be filtered
            recipe.save()
    
    @fake_today_decorator()
    @empty_diet_decorator
    @patch.object(hippocrate.controls.constraint, "BUDGET_VALUES", {1: {"max_avg": 1.1, "max_filter": 3}})
    @patch.object(hippocrate.controls.filters, "BUDGET_VALUES", {1: {"max_avg": 1.1, "max_filter": 3}})
    def test_budget_limit(self):
        set_random_seed(42)
        
        # Planning calculation
        response = self._suggest_through_api()
        self.assertEqual(response.status_code, 200)
        
        # Retrieving the DishRecipes
        recipes = set()
        for dish_recipe in DishRecipe.objects.all():
            recipes.add(dish_recipe.recipe_id)
        
        self.assertEqual(sorted(recipes), self.cheapRecipes)


class TestNoBudgetConstraint(HpUnidishApiTest):
    """
    Just testing that a no budget constraint doesn't crash
    """
    def init_user(self):
        self.user.budget = 3 # High budget
        self.user.save()
        
    @fake_today_decorator()
    @empty_diet_decorator
    @patch.object(hippocrate.controls.constraint, "BUDGET_VALUES", {3: {"max_avg": 4, "max_filter": 0}})
    @patch.object(hippocrate.controls.filters, "BUDGET_VALUES", {3: {"max_avg": 4, "max_filter": 0}})
    def test_no_budget_limit(self):
        response = self._suggest_through_api()
        self.assertEqual(response.status_code, 200)