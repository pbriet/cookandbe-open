from hippocrate.tests                   import HpUnidishApiTest
from common.boost                       import to_dict
from hippocrate_cpp.core                    import set_random_seed, IdVector
from hippocrate.models.constraints      import UnicityFoodTagConstraint
from recipe_mgr.models                  import DishType

class TestFoodTagUnicity(HpUnidishApiTest):
    """
    Test that a main food tag in a recipe cannot appear more than one time in a given day
    """
    # 3 recipes, each one with 1 food. 2 meals.
    # First food is tagged with one tag, like the third one. The second one is tagged with the 2 same tags.
    # Solution is then 1st and 3rd recipe, to avoid redundancies
    NB_RECIPES          = 3
    NB_FOODS            = 3
    NB_MEALSLOTS        = 2
    NB_SLOTS_PER_DAY    = 2
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 1

    def setUp(self):
        self.food_tag1 = self.create_db_food_tag("pastas")
        self.food_tag2 = self.create_db_food_tag("chocolate")
        super().setUp()
        

    def init_problem(self, forced_constraints=None, **kargs):
        food_tag_ids  = IdVector()
        for tag in (self.food_tag1, self.food_tag2):
            food_tag_ids.append(tag.id)
        unicity_food_tag = UnicityFoodTagConstraint(1500, food_tag_ids)
        return super().init_problem(forced_constraints=[unicity_food_tag], **kargs)
        
    def init_food(self, i):
        food = super().init_food(i)
        if i <= 1:
            self.db_assign_food_to_foodtag(food, self.food_tag1)
        if i >= 1:
            self.db_assign_food_to_foodtag(food, self.food_tag2)
        return food

    def test_food_tag_unicity(self):
        set_random_seed(42)
        # Generate a full planning
        solution = self.problem.solve_darwin()
        recipes = []
        for dish_id, recipe_list in to_dict(solution.get_recipes()).items():
            for r in recipe_list:
                recipes.append(r.recipe_id)

        # Recipe 1 and 3 are expected, because there's no food tag redundancy
        self.assertEqual(sorted(recipes), [self.recipes[0].id, self.recipes[2].id])
