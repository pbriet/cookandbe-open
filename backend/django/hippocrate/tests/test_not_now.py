from hippocrate.tests               import HpUnidishApiTest
from hippocrate_cpp.core                import set_random_seed
from hippocrate.models.problem      import Problem
from hippocrate.models.constraints  import UnicityConstraint
from hippocrate.controls.constraint import ConstraintGenerator
from planning_mgr.models            import NotNow


class TestNotNow(HpUnidishApiTest):
    """
    We have 2 recipes, 2 dishes.
    There is a big constraint of redundancy that makes obvious what is the ideal solution (recipe1, recipe2)
    But then we add a NotNow to exclude one of the recipes of the solution, and recalculate
    starting from this previous solution
    """
    NB_RECIPES          = 2
    WITH_INGREDIENTS    = False
    NB_MEALSLOTS        = 1
    NB_DISHES_PER_MEAL  = 2

    def init_problem(self, start_from_existing_solution=False):

        forced_constraints = [UnicityConstraint(100, [self.defaultDishType.id])]

        class FakeProblem:
            def __init__(x):
                x.user = self.user
                x.profiles = []
                x.planning = self.days[0].planning
                x.enable_diet = False
                x.own_recipes = []
                x.cookbook_recipes = []

        constraint_generator = ConstraintGenerator(FakeProblem())
        forced_constraints.extend(constraint_generator.recipe_constraints())

        self.problem = Problem(self.days, forced_constraints=forced_constraints,
                               start_from_existing_solution=start_from_existing_solution)

    def test_notnow(self):

        # Ensuring we really have 2 recipes
        self.assertEqual(len(self.recipes), 2)
        set_random_seed(42)

        self.init_problem(False)
        solution = self.problem.solve_darwin()
        self.problem.save_solution(solution)
        recipe_ids = self._get_recipe_ids(solution)

        # There should be 2 recipes because of the redundancy constraint
        self.assertEqual(len(set(recipe_ids)), 2)

        # Saying : I don't want recipe 1, not now
        NotNow.objects.create(user=self.user, recipe=self.recipes[0])

        # Another user is saying "I don't want recipe 2"
        other_user = self.create_db_user("other@other.fr")
        NotNow.objects.create(user=other_user, recipe=self.recipes[1])

        # Restarting the calculation, restarting from the existing solution
        self.init_problem(True)
        solution = self.problem.solve_darwin()
        recipe_ids = self._get_recipe_ids(solution)

        self.assertEqual(len(set(recipe_ids)), 1)
