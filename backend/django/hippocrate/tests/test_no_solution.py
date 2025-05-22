from hippocrate.tests               import HpUnidishApiTest
from common.mock_tools              import fake_today_decorator, empty_diet_decorator
from planning_mgr.models            import DishRecipe

class TestLimitedSolution(HpUnidishApiTest):
    """
    Testing to optimize a planning with no solution because of too many filters
    """
    NB_RECIPES          = 2
    NB_MEALSLOTS        = 7
    NB_SLOTS_PER_DAY    = 1
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1
    WITH_INGREDIENTS    = False
    DISLIKE_RECIPE1     = True
    DISLIKE_RECIPE2     = True
    
    def init_problem(self):
        # Adding dislikes on the two recipes
        profile = self.profiles[0]
        if self.DISLIKE_RECIPE1:
            self.create_db_recipe_dislike(self.recipes[0], profile)
        if self.DISLIKE_RECIPE2:
            self.create_db_recipe_dislike(self.recipes[1], profile)
        super().init_problem()
    
    @fake_today_decorator()
    @empty_diet_decorator
    def _do(self):
        return self._suggest_through_api()
        
class TestNoSolution(TestLimitedSolution):
    def test_should_return_invalid_solution(self):
        """
        There should be a solution _anyway_, but the DishRecipe must store
        a flag that all filters were not respected
        """
        response = self._do()
        dishrecipes = sorted(list(DishRecipe.objects.all()), key=lambda x: x.id)
        self.assertEqual(len(dishrecipes), 7) # 7 dish recipes, one for each mealslot
        for dr in dishrecipes:
            self.assertTrue(not dr.fully_filtered)
        
        self.assertEqual(len(response.data['suggestions']), 1) # 1 dishrecipe on day 1 (1 per day)
        suggestion = response.data['suggestions'][0]
        self.assertTrue(not suggestion['fully_filtered'])
        self.assertEqual(suggestion['disabled_filters'],  ["N'aime pas %s" % dishrecipes[0].recipe.name])

class TestWithSolution(TestLimitedSolution):
    DISLIKE_RECIPE2     = False
    def test_should_return_invalid_solution(self):
        """
        Testing that without a dislike, things work like a charm, as usual
        """
        self._do()
        dishrecipes = list(DishRecipe.objects.all())
        self.assertEqual(len(dishrecipes), 7) # 7 dish recipes, one for each mealslot
        for dr in dishrecipes:
            self.assertTrue(dr.fully_filtered)
            # Only recipe 2 is not disliked
            self.assertEqual(dr.recipe.id, self.recipes[1].id)
