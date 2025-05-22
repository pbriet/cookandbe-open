from common.test                import TestAPIWithLogin, add_permissions
from common.model               import reload_object
from recipe_mgr.models          import Ingredient, FoodConversion

class TestConversions(TestAPIWithLogin):
    INITIALIZE_RECIPE_INDEXER = True
    def setUp(self):
        super().setUp()
        self.chocolate = self.create_db_food(name="chocolate")

        self.chocolate_grams = self.create_db_food_conversion(self.chocolate, "g", 1)
        self.chocolate_chunk = self.create_db_food_conversion(self.chocolate, "chunk", 10)
        self.chocolate_tablet = self.create_db_food_conversion(self.chocolate, "tablet", 100)
        self.chocolate_other = self.create_db_food_conversion(self.chocolate, "other", 400)

        self.recipe1 = self.create_db_recipe("chocolate cake", nb_people=2)
        self.recipe2 = self.create_db_recipe("chocolate praline")
        self.recipe3 = self.create_db_recipe("chocolate bar")

        self.init_default_ingredient_settings()
        # In the chocolate cake, add 16 chunks of chocolate
        self.ing0 = self.create_db_ingredient(self.recipe1, self.chocolate, 160, default_conversion=self.chocolate_chunk)

        # In the chocolate praline, add 6 chunks of chocolate
        self.ing1 = self.create_db_ingredient(self.recipe2, self.chocolate, 60, default_conversion=self.chocolate_chunk)
        
        # In the chocolate bar, add 1 tablet
        self.ing2 = self.create_db_ingredient(self.recipe3, self.chocolate, 100, default_conversion=self.chocolate_tablet)


    @add_permissions("admin")
    def test_propagate_conversion_change(self):
        """
        Test that when a FoodConversion value is changed, it affects all recipes
        with this conversion as default
        """
        # We now decide that a chunk of chocolate is 5g (not 10g)
        response = self.client.put('/secure/api/food_conversion/%i' % self.chocolate_chunk.id, {'value': 5,
                                                                                         'food': self.chocolate.id,
                                                                                         'unit': "chunk",
                                                                                         'unit_plural': "chunks"})

        self.assertEqual(response.status_code, 200)

        # Reload the ingredients
        ings = [Ingredient.objects.get(pk=i.id) for i in (self.ing0, self.ing1, self.ing2)]

        # ing0 and ing1 quantities are divided by 2
        self.assertEqual(ings[0].grams, 80)
        self.assertEqual(ings[1].grams, 30)

        # ing2 remains unaffected
        self.assertEqual(ings[2].grams, 100)
        
        
    @add_permissions("admin")
    def test_deleting_only_unused_conversions(self):
        """
        Check that it is not authorized to delete a conversion that is already in use
        """
        response = self.client.delete('/secure/api/food_conversion/%i' % self.chocolate_chunk.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'error')
        
        response = self.client.delete('/secure/api/food_conversion/%i' % self.chocolate_tablet.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'error')
        
        response = self.client.delete('/secure/api/food_conversion/%i' % self.chocolate_other.id)
        self.assertEqual(response.status_code, 204)
        
        self.assertEqual(FoodConversion.objects.count(), 3)
        
        
    def test_conversion_recipes(self):
        """
        Test the retrieval of the recipes using a given conversion
        """
        response = self.client.get('/secure/api/food_conversion/%i/recipes' % self.chocolate_chunk.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(sorted([recipe['name'] for recipe in response.data]), ['chocolate cake', 'chocolate praline'])
    
    def test_recipe_ratio_conversions(self):
        response = self.client.get('/api/recipe/%i/with_ingredients' % self.recipe1.id, {'ratio': 1})
        chocolate = response.data['ingredients'][0]
        chocolate_conversions = chocolate['conversions']
        print(chocolate_conversions)
        self.assertEqual(chocolate_conversions['basic']['id'], self.chocolate_grams.id)
        
    @add_permissions("admin")
    def test_update_conversion(self):
        """
        Test modifying unit
        """
        response = self.client.get('/secure/api/food_conversion/%i' % self.chocolate_chunk.id)
        self.assertEqual(response.status_code, 200)
        chocolate_chunk_dict = response.data
        chocolate_chunk_dict['unit'] = "pompom"
        response = self.client.put('/secure/api/food_conversion/%i' % self.chocolate_chunk.id,
                                   chocolate_chunk_dict)
        self.assertEqual(response.status_code, 200)
        reload_object(self.chocolate_chunk)
        self.assertEqual(self.chocolate_chunk.unit, "pompom")
                                    
        