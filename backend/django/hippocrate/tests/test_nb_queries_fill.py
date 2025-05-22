"""
The purpose of this test is to check that the number of queries remains low when
asking to fill a planning  (serialization included)
"""

from hippocrate.tests               import HpUnidishApiTest
from common.mock_tools              import fake_today_decorator, empty_diet_decorator, fake_ratios_decorator

class HippocrateNgQueriesTest(HpUnidishApiTest):
    def init_problem(self):
        """
        No, there is no problem :)
        <We are using the API to generate the problem>
        """
        pass

    @fake_today_decorator()
    @fake_ratios_decorator(1)
    @empty_diet_decorator
    def test_nb_queries_fill(self):

        def go_fill_planning():
            # Calls the API to fill the planning
            res = self._fill_through_api()

            # Just checking that it works correctly
            self.assertEqual(res.status_code, 201)
            self.assertEqual(len(res.data['days']), 7)

        # Expected number of SQL queries !
        with self.assertNumQueries(52):
            go_fill_planning()
        with self.assertNumQueries(52):
            go_fill_planning()


    @fake_today_decorator()
    @fake_ratios_decorator(1)
    @empty_diet_decorator
    def test_nb_queries_suggest(self):

        def go_suggest():
            # Calls the API to fill the planning
            res = self._suggest_through_api()

            # Just checking that it works correctly
            self.assertEqual(res.status_code, 200)

        # Expected number of SQL queries !
        with self.assertNumQueries(59):
            go_suggest()
        with self.assertNumQueries(58):
            go_suggest()

        with self.assertNumQueries(57):
            # Restarting from existing planning
            res = self._suggest_through_api(start_from_existing=True)
            # Just checking that it works correctly
            self.assertEqual(res.status_code, 200)
