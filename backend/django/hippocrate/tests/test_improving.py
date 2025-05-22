from hippocrate.tests               import HpUnidishApiTest
from common.mock_tools              import fake_today_decorator, empty_diet_decorator
from hippocrate_cpp.core                import set_random_seed
from hippocrate.models.problem      import Problem
from hippocrate.models.constraints  import MaxModifsConstraint, UnicityConstraint
from planning_mgr.models            import Dish
import common
import datetime

class TestPlanningImproval(HpUnidishApiTest):
    """
    In this test, we'll have 3 dishes and 3 recipes
    + one unicity constraint

    The ideal solution is one recipe per dish.
    """
    NB_RECIPES          = 3
    WITH_INGREDIENTS    = False
    NB_MEALSLOTS        = 3
    NB_DISHES_PER_MEAL  = 1
    NB_SLOTS_PER_DAY    = 2

    def setUp(self):
        super().setUp()
        
        # The initial solution has 3 times the same recipe -- so wrong!
        for day in self.days:
            for meal_slot in day.meal_slots.all():
                for dish in meal_slot.dishes.all():
                    self.create_db_dishrecipe(dish, self.recipes[0])

        # Creating a total of 7 days. The 5 remaining days are just empty
        last_date = self.days[-1].date
        for i_day in range(7 - self.NB_DAYS):
            self.create_db_day(last_date + datetime.timedelta(days=i_day + 1))

    def init_problem(self, dish_ids=None):
        self.problem = Problem(self.days, forced_constraints=[UnicityConstraint(100, [self.defaultDishType.id])])

    def _test_improve(self, max_nb_modifications, cost_modification):
        """
        Test an improvement and return the number of recipes in the solution
        """
        set_random_seed(42)
        initial_solution = self.problem.build_current_solution()
        self.problem.add_constraint(MaxModifsConstraint(initial_solution, max_nb_modifications, cost_modification))

        solution = self.problem.solve_darwin()
        recipe_ids = self._get_recipe_ids(solution)

        # 3 different recipes now !
        return len(set(recipe_ids))

    def test_improve_basic(self):
        """
        The improvement should change 2 meals
        """
        nb_modifications = self._test_improve(2, 1000)
        # 3 different recipes now ! (2 modifications)
        self.assertEqual(nb_modifications, 3)

    def test_limited_improve1(self):
        """
        Because of a penalty, only one recipe should change
        """
        nb_modifications = self._test_improve(1, 1000)
        # 2 different recipes expected (1 modification)
        self.assertEqual(nb_modifications, 2)

    def test_limited_improve2(self):
        """
        Penalty on the second change, but still more interesting than no change
        """
        nb_modifications = self._test_improve(1, 80)
        # 3 different recipes expected (2 modifications)
        self.assertEqual(nb_modifications, 3)

    @empty_diet_decorator
    def test_improve_api(self):
        """
        Just checking that the API is working
        """
        response = self.client.post('/api/user/%i/improve/%s' % (self.user.id, self.days[0].date),
                                                                 {'nb_days': self.NB_DAYS})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['modifications']), 2)
        self.assertEqual(response.data['new_indicators']['total_cost'], 0)

    def _test_improve_api_day(self, day, expected_nb_modifications):
        """
        Generic part to test the improvement of one day only
        """
        for d in self.days:
            if d.id != day.id:
                d.skipped = False  # Other days can't be modified
                d.save()
        
        response = self.client.post('/api/user/%i/day/%s/improve' % (self.user.id, day.date))
        self.assertEqual(response.status_code, 200)

        ## There are 2 days on day 1, they should be both modified
        self.assertEqual(len(response.data['suggestions']), expected_nb_modifications)

        dish_ids_to_modify = [s['dish_id'] for s in response.data['suggestions']]
        dish_ids_day = Dish.objects.filter(meal_slot__day=day)
        dish_ids_day = [d.id for d in dish_ids_day]

        self.assertEqual(sorted(dish_ids_to_modify), sorted(dish_ids_day))

    @fake_today_decorator(2014, 3, 1)
    @empty_diet_decorator
    def test_improve_api_day1(self):
        """
        Checking that the API is working for a one-day optimization
        -> on day 1, the 2 dishes should be modified
        """
        self._test_improve_api_day(self.days[0], 2)

    @fake_today_decorator(2014, 3, 1)
    @empty_diet_decorator
    def test_improve_api_day2(self):
        """
        Checking that the API is working for a one-day optimization
        -> on day 2, the only dish should be modified. This doesn't solve totally the problem
        """
        self._test_improve_api_day(self.days[1], 1)