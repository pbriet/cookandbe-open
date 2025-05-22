
from common.test                    import OptalimTest
from hippocrate.models.recipe       import RecipeData, RecipeDataBuilder
from hippocrate.models.recipestorage import MainRecipeStorage
from common.boost                   import to_dict, to_list
from mock                           import patch, MagicMock
import hippocrate.models.recipe
import pickle

import sys

# Makes the nutrient calculator returning a specific value
class MockNutrientCalculator(object):
    def __init__(self):
        self.aggregated_nutrients = {8: 42, 25: 51}
        self.nutrients_data_availability = {11: 0.4, 16: 0.6}

    def compute(self): return self

class RecipeDataTest(OptalimTest):
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        # Fake dish types
        fk_dish_types = []
        for dt_id in (15, 20, 22):
            fk_dish_types.append(MagicMock(id=dt_id))

        # Fake ingredients
        fk_ingredients = []
        for (food_id, cooking_method_id, grams) in (13, 4, 100), (16, 4, 100), (18, 50, 100), (13, 4, 50):
            fk_ingredients.append(MagicMock(food_id=food_id, cooking_method_id=cooking_method_id, grams=grams, id=1))

        # Fake ustensils
        fk_ustensils = []
        for ustensil_id in (1, 2):
            fk_ustensils.append(MagicMock(id = ustensil_id))

        # Faking an ORM iterator
        class MockIterator(object):
            def __init__(self, values):
                self.values = values
            def prefetch_related(self, *args, **kargs):
                return self
            def all(self, *args, **kargs):
                return self.values

        # Fake recipe
        class MockRecipe(object):
            id = 4
            name = "pain au chocolat"
            price = 2
            status = 4
            prep_minutes = 5
            cook_minutes = 30
            rest_minutes = 3
            difficulty = 2
            perceived_healthy = True
            internal = False
            dish_types = MockIterator(fk_dish_types)
            ingredients = MockIterator(fk_ingredients)
            ustensils = MockIterator(fk_ustensils)

        self.mock_recipe = MockRecipe()


    @patch('hippocrate.models.recipe.RecipeNutrientCalculator')
    def test_recipe_data(self, mck_nutrient_calculator):

        mck_nutrient_calculator.return_value = MockNutrientCalculator()

        recipe_data = RecipeDataBuilder().build(4, self.mock_recipe)
        self.assertEqual(recipe_data.recipe_id, 4)
        self.assertEqual(recipe_data.name, "pain au chocolat")
        self.assertEqual(recipe_data.get_data_from_key("price"), 2)
        self.assertEqual(recipe_data.get_data_from_key("prep_minutes"), 5)
        self.assertEqual(recipe_data.get_data_from_key("cook_minutes"), 30)
        self.assertEqual(recipe_data.get_data_from_key("rest_minutes"), 3)
        self.assertEqual(recipe_data.get_data_from_key("difficulty"), 2)
        self.assertEqual(set(recipe_data.dish_type_ids), set([15, 20, 22]))
        self.assertEqual(set(recipe_data.cooking_method_ids), set([4, 50]))
        self.assertEqual(to_dict(recipe_data.foods), {13: 150, 16: 100, 18: 100})
        self.assertEqual(to_list(recipe_data.ustensils), [1, 2])



class HpUnidishApiTest(OptalimTest):

    def test_pickle_recipe_data(self):

        self.create_db_nutrient("test1")
        self.create_db_nutrient("test2")

        MainRecipeStorage.init_indexer()

        a = RecipeData(10)
        a.allocate_data()
        a.name = "plop"
        a.foods[4] = 29
        a.foods[6] = 30
        a.cooking_method_ids.append(40)
        a.dish_type_ids.append(3)
        a.dish_type_ids.append(5)
        a.food_tag_ids.append(7)
        a.main_food_tag_ids.append(33)
        a.main_food_tag_ids.append(34)
        a.recipe_tag_ids.append(2)
        a.add_data("price", 50)
        a.add_data("prep_minutes", 43)
        a.add_data("rest_minutes", 777)
        a.add_data("cook_minutes", 900)
        a.add_data("difficulty", 25)
        a.add_data("test1", 0)
        a.add_data("test2", 33)
        a.ustensils.append(4)
        a.ustensils.append(2)

        dumped = pickle.dumps(a)
        b = pickle.loads(dumped)

        self.assertEqual(b.recipe_id, 10)
        self.assertEqual(b.name, "plop")
        self.assertEqual(to_dict(b.foods), {4: 29, 6: 30})
        self.assertEqual(to_list(b.cooking_method_ids), [40])
        self.assertEqual(to_list(b.dish_type_ids), [3, 5])
        self.assertEqual(to_list(b.food_tag_ids), [7])
        self.assertEqual(to_list(b.main_food_tag_ids), [33, 34])
        self.assertEqual(to_list(b.recipe_tag_ids), [2])
        self.assertEqual(b.get_data_from_key("price"), 50)
        self.assertEqual(b.get_data_from_key("prep_minutes"), 43)
        self.assertEqual(b.get_data_from_key("rest_minutes"), 777)
        self.assertEqual(b.get_data_from_key("cook_minutes"), 900)
        self.assertEqual(b.get_data_from_key("test1"), 0)
        self.assertEqual(b.get_data_from_key("test2"), 33)
        self.assertEqual(to_list(b.ustensils), [4, 2])
        self.assertEqual(sorted(to_list(b.defined_data_ids)), list(range(7)))
