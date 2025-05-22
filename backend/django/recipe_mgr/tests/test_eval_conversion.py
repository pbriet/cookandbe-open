from common.test                import OptalimTest
from recipe_mgr.helpers         import evaluate_conversion, food_conversions
from mock                       import Mock

class TestEvalConversion(OptalimTest):


    def _test_conversion(self, conversion_dict, loss_coeff=0, default_loss_coeff=0):
        # Creating a mock FoodConversion
        mock_conversion = Mock(value=conversion_dict['value'], loss_coeff=loss_coeff,
                               unit=conversion_dict['name'],
                               splittable=conversion_dict.get('splittable', True))

        # Creating a mock default Conversion
        mock_default_conversion = Mock(loss_coeff=default_loss_coeff)
        
        res = evaluate_conversion(mock_conversion, conversion_dict['grams'], mock_default_conversion)
        return res

    def test_eval_conversion(self):

        # CASE 1 : 2 oranges, precisely
        CONVERSION1 = {'name': 'orange',
                       'grams': 120,
                       'value': 60}
        res = self._test_conversion(CONVERSION1)
        self.assertEqual(res['value'], 2)  # 2 oranges
        self.assertEqual(res['loss'], 0.0) # No data loss
        self.assertTrue(res['score'] <= 0.07) # Low score, good conversion

        # CASE 2 : 500g, precisely
        CONVERSION2 = {'name': 'grams',
                       'grams': 500,
                       'value': 1}
        res = self._test_conversion(CONVERSION2)
        self.assertEqual(res['value'], 500)  # 500g
        self.assertEqual(res['loss'], 0.0) # No data loss
        self.assertTrue(res['score'] >= 0.6 and res['score'] <= 0.7) # High score, because high value

        # CASE 3: 1.21 bowl of rice  (1 bowl when rounded)
        CONVERSION3 = {'name': 'bowl',
                       'grams': 145.2,
                       'value': 120}
        res = self._test_conversion(CONVERSION3)
        self.assertEqual(res['value'], 1)  # 1 bowl
        self.assertEqual(round(res['loss'], 1), 17.4) # Big data loss
        self.assertTrue(res['score'] >= 2 and res['score'] <= 3) # High score, because of data loss

        # CASE 4: 483g of rice (480g when rounded)
        CONVERSION4 = {'name': 'grams',
                       'grams': 483,
                       'value': 1}
        res = self._test_conversion(CONVERSION4)
        self.assertEqual(res['value'], 480)  # 480g
        self.assertEqual(round(res['loss'], 1), 0.6) # Low data loss
        self.assertTrue(res['score'] >= 0.6 and res['score'] <= 0.7) # High score
        
        
        # CASE 5: 0.67 bowl of rice  (2/3)
        CONVERSION5 = {'name': 'bowl',
                       'grams': 80,
                       'value': 120}
        res = self._test_conversion(CONVERSION5)
        self.assertEqual(res['value'], 0.67)  # 2/3 bowl
        self.assertEqual(round(res['loss'], 1), 0) # No data loss
        self.assertTrue(res['score'] < 0.5) # Low score, this is a good conversion

    def test_eval_small_conversion(self):

        # 1 spoon
        CONVERSION1 = {'name': 'spoon',
                       'grams': 2,
                       'value': 1.5}
        res = self._test_conversion(CONVERSION1)
        self.assertEqual(res['value'], 1.5)  # 1.5 spoons = 2.25g
        self.assertEqual(res['loss'], 12.5) # Data loss is high
        self.assertTrue(res['score'] <= 0.2) # But not a bad score because we are in low values
        
        # 1 ml
        CONVERSION1 = {'name': 'ml',
                       'grams': 2,
                       'value': 1}
        res = self._test_conversion(CONVERSION1)
        self.assertEqual(res['value'], 2)  # 2ml
        self.assertEqual(res['loss'], 0.0) # No loss
        self.assertTrue(res['score'] > 0.2) # Penalty because "base"
        


    def test_floats_penality(self):
        # CASE 1: 1.5 orange -- no loss
        CONVERSION1 = {'name': 'orange',
                       'grams': 225,
                       'value': 150}
        # CASE 2: 2 small oranges -- very small loss
        CONVERSION2 = {'name': 'small oranges',
                       'grams': 230,
                       'value': 120}

        score_oranges = self._test_conversion(CONVERSION1)['score']
        score_small_oranges = self._test_conversion(CONVERSION2)['score']

        # We want the small oranges to be taken
        self.assertTrue(score_small_oranges < score_oranges)
        
        # By setting "orange" as not splittable, score should be higher and conversion value should be 2
        CONVERSION3 = {'name': 'orange',
                       'grams': 225,
                       'value': 150,
                       'splittable': False}
        non_splittable = self._test_conversion(CONVERSION3)
        self.assertEqual(non_splittable['value'], 2)
        self.assertTrue(non_splittable['score'] > score_oranges)
        
                       

    def test_loss_calculations(self):
        """
        Test that the loss_coeff is correctly taken into account in the conversion
        """
        # 1 toto is 100g, we have 80g
        CONVERSION  = {'name': 'toto',
                       'grams': 80,
                       'value': 100}

        # But 1 toto has 20% loss, so in reality, 100g gives 80g
        res = self._test_conversion(CONVERSION, loss_coeff=0.2, default_loss_coeff=0)
        self.assertEqual(res['loss'], 0)
        self.assertEqual(res['value'], 1)  # 1 toto !

        # Still playing with 1 toto, but this time the default conversion had also a 20% loss
        res = self._test_conversion(CONVERSION, loss_coeff=0.2, default_loss_coeff=0.2)
        self.assertEqual(res['value'], 0.75)  # 80g is now 3/4 of a toto
        self.assertEqual(res['loss'], 6.25) # with some loss

        # Last case : the default conversion had a higher loss coeff (50% vs 20%)
        res = self._test_conversion(CONVERSION, loss_coeff=0.2, default_loss_coeff=0.5)
        # there is 80g. But it was stored with a 50% loss conversion. Reality => 40g
        # A toto is 100g, but with 20% loss it is 80g.  Reality  = 0.5 totos.
        self.assertEqual(res['value'], 0.5)
        

class TestFoodConversions(OptalimTest):
    
    def setUp(self):
        super().setUp()
        self.food = self.create_db_food("thing")
        
        self.basic_cnv = self.create_db_food_conversion(food=self.food, unit="g", value=1)
        self.cnv = self.create_db_food_conversion(food=self.food, unit="piece", value=100)
        self.cnv_with_loss = self.create_db_food_conversion(food=self.food,
                                                            unit="piece with water",
                                                            loss_coeff=0.685,
                                                            value=500)
    
    def test_food_conversions_with_basic(self):
        
        best, default = food_conversions(self.food, 160)
        
        # Ensure the best option is "piece with water"
        self.assertEqual(best['unit'], 'piece with water')
        self.assertEqual(best['value'], 1)
        
        # Ensure the default option is "g", and value is 510
        self.assertEqual(default['unit'], 'g')
        self.assertEqual(default['value'], 510) # And not 160g ! It should be with loss included
        self.assertEqual(default['html_value'], '510')
        