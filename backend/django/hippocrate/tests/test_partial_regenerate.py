from hippocrate.tests           import HpUnidishApiTest
from planning_mgr.models        import DishRecipe

class TestNaive(HpUnidishApiTest):
    def test_partial_reload(self):
        # Generate a full week
        solution = self.problem.solve_darwin()
        self.problem.save_solution(solution)
        
        # Retrieving infos about this first week
        dish_recipe = {}
        dish_ids = []
        for day in self.days:
            for meal in day.meal_slots.all():
                for dish in meal.dishes.all():
                    dish_ids.append(dish.id)
                    dish_recipe[dish.id] = list(dish.recipes.all())[0].id
        
        # Reload only the first dish
        only_mutable_dish_id = dish_ids[0]
        self.init_problem(dish_ids=[only_mutable_dish_id])
        solution = self.problem.solve_darwin()
        self.problem.clean_previous_solution()
        self.problem.save_solution(solution)
        
        # Retrieving infos on the second week (partially regenerated)
        new_dish_recipe = {}
        new_dish_ids = []
        for day in self.days:
            for meal in day.meal_slots.all():
                for dish in meal.dishes.all():
                    new_dish_ids.append(dish.id)
                    new_dish_recipe[dish.id] = list(dish.recipes.all())[0].id
        
        # Check that the recipes are similar on the other dishes, and 
        # that the first dish has changed
        self.assertEqual(dish_ids, new_dish_ids)
        for dish_id, old_recipe_id in dish_recipe.items():
            if dish_id == only_mutable_dish_id:
                self.assertNotEqual(old_recipe_id,
                                    new_dish_recipe[dish_id])
            else:
                self.assertEqual(old_recipe_id,
                                 new_dish_recipe[dish_id])
        