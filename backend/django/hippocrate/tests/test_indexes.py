
from common.test                    import OptalimTest
from hippocrate_cpp.core                import RecipeDataVector, IdVector, RecipeData
from hippocrate_cpp.core                import DetailedRecipeIndex, set_random_seed
from collections                    import defaultdict

NUTRIENT_1 = 3031

class NutrientNormalIndex(OptalimTest):


    def _pick100(self, idx, target_value, nb_picks=100, variance=-1):
        """
        Pick 100 recipes from index with nutrient value = target value
        Returns recipes sorted by number of times they were selected
        """
        picked_recipes = defaultdict(int)
        for i in range(nb_picks):
            rdata = idx.recipe_data_normal(NUTRIENT_1, target_value, variance)
            picked_recipes[rdata.recipe_id] += 1

        return sorted(picked_recipes.items(), key=lambda x: (x[1], -x[0]), reverse=True)

    def set_sorted_values(self, idx, dict_values):
        """
        Define the C++ values for Index._data_sorted_values
        std::map<long, RecipeDataValuesVector >
        """
        for nutrient_id, values in dict_values.items():
            vector = IdVector()
            for value in values:
                vector.append(value)
            idx._data_sorted_values[nutrient_id] = vector


    def set_sorted_recipe_ids(self, idx, dict_values):
        """
        Define the C++ values for Index._data_sorted_recipes
        std::map<long, RecipeDataVector>
        """
        for nutrient_id, recipe_ids in dict_values.items():
            vector = RecipeDataVector()
            for recipe_id in recipe_ids:
                vector.append(RecipeData(recipe_id))
            idx._data_sorted_recipes[nutrient_id] = vector


    def test_normal_index(self):

        set_random_seed(1666)

        idx = DetailedRecipeIndex()
        # 5 RECIPES :
        # - RECIPE 1 : 10g
        # - RECIPE 2 : 6g
        # - RECIPE 3 : 20g
        # - RECIPE 4 : 1g
        # - RECIPE 5 : 2g
        self.set_sorted_values(idx,      {NUTRIENT_1: [1, 2, 6, 10, 20]})
        self.set_sorted_recipe_ids(idx,  {NUTRIENT_1: [4, 5, 2, 1, 3]})

        # Retrieving 100 recipes at approximately NUTRIENT_1=6
        sorted_recipes = self._pick100(idx, 6)

        # In probabilities, recipe 2 (nutrient=6) is more likely than
        #                   recipe 5 (nutrient=2)
        #                   recipe 1 (nutrient=10)
        #                   etc.
        self.assertEqual(sorted_recipes,
                         [(2, 39), (1, 31), (5, 17), (4, 10), (3, 3)])

        # Same thing, but with a shorter variance
        sorted_recipes = self._pick100(idx, 6, variance=7)
        self.assertEqual(sorted_recipes,
                         [(2, 63), (1, 17), (5, 17), (4, 3)])

        # with an even shorter variance
        sorted_recipes = self._pick100(idx, 6, variance=2)
        self.assertEqual(sorted_recipes,
                         [(2, 85), (5, 9), (1, 6)])

        # with target_value = 4
        sorted_recipes = self._pick100(idx, 4, variance=2)
        self.assertEqual(sorted_recipes,
                         [(5, 52), (2, 46), (4, 2)])

        # target_value = 3
        sorted_recipes = self._pick100(idx, 3, variance=2)
        self.assertEqual(sorted_recipes,
                         [(5, 65), (2, 22), (4, 13)])

        # target_value lower than any existing
        sorted_recipes = self._pick100(idx, 0, variance=7)
        self.assertEqual(sorted_recipes,
                         [(4, 72), (5, 25), (2, 3)])

        # target_value higher than any existing
        sorted_recipes = self._pick100(idx, 22, variance=10)
        self.assertEqual(sorted_recipes,
                         [(3, 99), (1, 1)])



    def test_normal_index_with_same_values(self):

        set_random_seed(1666)

        idx = DetailedRecipeIndex()
        # 5 RECIPES :
        # - RECIPE 1 : 10g
        # - RECIPE 2 : 10g
        # - RECIPE 3 : 20g
        # - RECIPE 4 : 6g
        # - RECIPE 5 : 10g
        self.set_sorted_values(idx,      {NUTRIENT_1: [6, 10, 10, 10, 20]})
        self.set_sorted_recipe_ids(idx,  {NUTRIENT_1: [4, 5, 2, 1, 3]})

        # Check that the algorithm returns the same probability for each of the recipe with 10g of nutrients
        sorted_recipes = self._pick100(idx, 10, variance=0.1)
        self.assertEqual(sorted_recipes, [(1, 35), (2, 34), (5, 31)])

        # Check that the algorithm returns the same probability for each of the recipe with 10g of nutrients
        sorted_recipes = self._pick100(idx, 9.5, variance=0.2)
        self.assertEqual(sorted_recipes, [(1, 38), (2, 31), (5, 31)])
