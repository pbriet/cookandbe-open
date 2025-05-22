from hippocrate.tests           import HpUnidishApiTest
from common.boost               import to_dict
from common.mock_tools          import empty_diet_decorator
from hippocrate_cpp.core            import set_random_seed, load_darwin_config
from recipe_mgr.models          import DishType

import optalim.mongo

from mock                       import patch

class FakeMongoIndicators:
    def __init__(self): self.values = None
    def find_one(self, *args): return self.values
    def update_one(self, query, set_query, **kargs):
        self.values = set_query["$set"]
        self.values['_id'] = "FAKE_ID"


class TestMonotonousDishTypes(HpUnidishApiTest):
    NB_RECIPES          = 20
    NB_FOODS            = 1
    NB_MEALSLOTS        = 3
    NB_DISHES_PER_MEAL  = 3
    NB_PROFILES         = 1

    def init_problem(self):
        # Set the default dishtype as monotonous
        self.defaultDishType.monotonous = True
        self.defaultDishType.save()
        super().init_problem()

    def test_should_be_monotonous(self):
        load_darwin_config(self.get_fixture_path(__file__, "darwin_no_crossover.yml"))
        set_random_seed(42)
        # Generate a full planning
        solution = self._solve_with_no_api()
        recipes = self._get_recipe_ids(solution)

        # All the recipes should be the sames
        self.assertEqual(len(set(recipes)), 1)


        self._test_indicators()

    @empty_diet_decorator
    def _test_indicators(self):
        # Retrieving indicators
        # Just ensuring it doesn't crash

        fmi = FakeMongoIndicators()
        def fake_indicators_tables(table_name):
            assert table_name == 'indicators_v2'
            return fmi

        with patch.object(optalim.mongo.Mongo, 'hp_table', fake_indicators_tables):
            response = self.client.get('/api/user/%i/day/%s/indicators' % (self.user.id, self.START_DATE))

        self.assertTrue(response.status_code, 200)

