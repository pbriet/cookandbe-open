from common.test                import TestAPIWithLogin, OptalimTest
from nutrient.helpers           import AdditionalNutrientsCalculator, NutrientCalculatorCache, RecipeNutrientCalculator
from optalim.config             import Config
from nutrient.models            import Nutrient
from mock                       import patch

import nutrient.helpers

class TestAdditionalNutrients(OptalimTest):

    def setUp(self):
        OptalimTest.setUp(self)
        NutrientCalculatorCache.reset()
        self.a = Nutrient.objects.create(name="A", unit="a", key="a")
        self.b = Nutrient.objects.create(name="B", unit="b", key="b")
        self.c = Nutrient.objects.create(name="C", unit="c", key="c")

    @patch.object(Config, 'nutrient_calculations', [{"name": "C", "sum": ["A", "B"]}])
    def test_sum(self):
        values = {self.a.id: 10, self.b.id: 15}
        availabilities = {self.a.id: 0.3, self.b.id: 0.5}
        AdditionalNutrientsCalculator(values, availabilities).apply()

        self.assertEqual(values, {self.a.id: 10, self.b.id: 15, self.c.id: 25})
        self.assertEqual(availabilities, {self.a.id: 0.3, self.b.id: 0.5, self.c.id: 0.4})

    @patch.object(Config, 'nutrient_calculations', [{"name": "C", "multiply": ["A", {"minus": ["B", "A"]}]}])
    def test_complex(self):
        values = {self.a.id: 10, self.b.id: 15}
        availabilities = {self.a.id: 0.3, self.b.id: 0.5}
        AdditionalNutrientsCalculator(values, availabilities).apply()

        # C = A * (B - A)
        self.assertEqual(values, {self.a.id: 10, self.b.id: 15, self.c.id: 50})
        self.assertEqual(availabilities, {self.a.id: 0.3, self.b.id: 0.5, self.c.id: 0.4})
        
        
class TestAddedSugar(OptalimTest):
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        
        veggies = self.create_db_foodtype("Légumes")
        milk = self.create_db_foodtype("Laits")
        other = self.create_db_foodtype("Autre")
        
        
        self.veggie = self.create_db_food("food", food_type=veggies)
        self.milk = self.create_db_food("food", food_type=milk)
        self.other = self.create_db_food("food", food_type=other)
        
        self.recipe = self.create_db_recipe()
        
        self.veggie_ingredient = self.create_db_ingredient(self.recipe, self.veggie, grams = 250)
        self.milk_ingredient = self.create_db_ingredient(self.recipe, self.milk, grams = 120)
        self.other_ingredient = self.create_db_ingredient(self.recipe, self.other, grams = 80)
        
        self.sugar = self.create_db_nutrient("sucrestotaux")
        self.added_sugar = self.create_db_nutrient("added_sugar")
        self.vitaminc = self.create_db_nutrient("vitaminc")
        
    
    def _test_added_sugars(self, nutrient_values, ingredient):
        with patch.object(nutrient.helpers, 'ADD_ADDED_SUGAR', True):
            NutrientCalculatorCache.init_added_sugars_food_types()
            
            calc = RecipeNutrientCalculator(self.recipe)
            calc._add_added_sugars(nutrient_values, ingredient)
        
    def test_calculate_with_veggie_sugar(self):
        """
        Veggies don't have added sugar
        """
        nutrient_values = {self.sugar.id: 70,
                           self.vitaminc.id: 50}
        
        self._test_added_sugars(nutrient_values, self.veggie_ingredient)
        
        self.assertEqual(nutrient_values, 
                         {self.sugar.id: 70,
                          self.added_sugar.id: 0,
                          self.vitaminc.id: 50})
        
    def test_calculate_with_milky_sugar(self):
        """
        Milk has sugar - weight*4% of added sugars
        """
        nutrient_values = {self.sugar.id: 70,
                           self.vitaminc.id: 50}
        
        self._test_added_sugars(nutrient_values, self.milk_ingredient)
        
        self.assertEqual(nutrient_values, 
                         {self.sugar.id: 70,
                          self.added_sugar.id: 65.2,
                          self.vitaminc.id: 50})
        
        ## Test with a minimum of 0 added sugars
        nutrient_values = {self.sugar.id: 2,
                           self.vitaminc.id: 50}
        
        self._test_added_sugars(nutrient_values, self.milk_ingredient)
        
        self.assertEqual(nutrient_values, 
                         {self.sugar.id: 2,
                          self.added_sugar.id: 0,
                          self.vitaminc.id: 50})
        
        
    def test_calculate_with_fully_added_sugar(self):
        """
        By default, all the sugar is added sugar
        """
        
        nutrient_values = {self.sugar.id: 70,
                           self.vitaminc.id: 50}
        
        self._test_added_sugars(nutrient_values, self.other_ingredient)
        
        self.assertEqual(nutrient_values, 
                         {self.sugar.id: 70,
                          self.added_sugar.id: 70,
                          self.vitaminc.id: 50})