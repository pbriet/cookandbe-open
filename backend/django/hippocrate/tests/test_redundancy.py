from hippocrate.tests           import HpUnidishApiTest
from common.boost               import to_dict
from hippocrate_cpp.core            import set_random_seed, load_darwin_config
from recipe_mgr.models          import DishType

class TestRedundancySolo(HpUnidishApiTest):
    NB_RECIPES          = 3
    NB_FOODS            = 1
    NB_MEALSLOTS        = 3
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1

    def init_foods(self):
        # Only one DishType used (fruit, for which we encourage redundancy)
        self.defaultDishType = self.create_db_dishtype(DishType.DT_FRUIT)
        super().init_foods(False)

    def test_should_be_redundant(self):
        load_darwin_config(self.get_fixture_path(__file__, "darwin_config_test_advanced.yml"))
        set_random_seed(42)
        # Generate a full planning
        solution = self._solve_with_no_api(False)
        recipe_ids = set(self._get_recipe_ids(solution))
        # All the recipes should be the same, because we encourage redundancy on fruits
        self.assertEqual(len(set(recipe_ids)), 1)

class TestRedundancyFamily(TestRedundancySolo):
    """
    Redundancy should be of minimum 5 portions for families (more than one profile)
    """
    NB_RECIPES      = 3
    NB_MEALSLOTS    = 5
    NB_PROFILES     = 2
