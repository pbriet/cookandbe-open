from common.test                import TestAPIWithLogin, OptalimTest
from nutrient.models            import FoodNutrient, NutrientRawStateAlteration,\
                                       NutrientCookAlteration
from recipe_mgr.models          import CookingMethod, RawState
from nutrient.helpers           import RecipeNutrientCalculator, NutrientCalculatorCache
from optalim.config             import Config
from mock                       import patch


class TestRecipeNutrientsAPI(TestAPIWithLogin):

    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.recipe = self.create_db_recipe()

        # Our recipe contains carrots and chocolate
        self.carrots = self.create_db_food('carrots')
        self.chocolate = self.create_db_food('chocolate')

        # Everything is raw and not_cooked
        self.raw = RawState.objects.create(name="frais")
        self.not_cooked = CookingMethod.objects.create(name="cru")

        self.carrots_ingredient = self.create_db_ingredient(self.recipe, self.carrots, 100,
                                                            raw_state=self.raw, cooking_method=self.not_cooked)
        self.chocolate_ingredient = self.create_db_ingredient(self.recipe, self.chocolate, 50,
                                                              raw_state=self.raw, cooking_method=self.not_cooked)

        # Carrots gets 10mg of "vitamin C" per 100g, Chocolate has 2mg per 100g
        self.vitamin_c = self.create_db_nutrient("vitamin C", short_name="vitc", key="vitaminc")
        FoodNutrient.objects.create(food=self.carrots, nutrient=self.vitamin_c, amount_per_gram=0.1,
                                    raw_state=self.raw, cooking_method=self.not_cooked)
                                    
        FoodNutrient.objects.create(food=self.chocolate, nutrient=self.vitamin_c, amount_per_gram=0.02,
                                    raw_state=self.raw, cooking_method=self.not_cooked)

        # Chocolate has 30g per 100g of sugar, carrots is "undefined"
        self.sugar = self.create_db_nutrient("sugar", short_name="sug", unit="g", key="sugar")
        FoodNutrient.objects.create(food=self.chocolate, nutrient=self.sugar, amount_per_gram=0.3,
                                    raw_state=self.raw, cooking_method=self.not_cooked)


    @patch.object(Config, 'nutrient_calculations', [])
    def test_recipe_nutrients(self):
        """
        Getting the total nutrient values per portion
        """
        response = self.client.get('/api/recipe/%i/nutrients' % self.recipe.id)
        self.assertEqual(response.status_code, 200)

        EXPECTED_RES = {'sugar': {'value': 15.0,  # 50*0.3  [chocolate g * sugar/g chocolate]
                                  'data_availability': 0.33,
                                  'nutrient': {'id': self.sugar.id,
                                               'infoods_tagname': '',
                                               'key': 'sugar',
                                               'name': 'sugar',
                                               'short_name': 'sug',
                                               'unit': 'g'}},
                        'vitamin C': {'value': 11.0,# 100*0.1 + 50*0.02 [carrots g * vitC/ carrots +
                                                                 #                    choco g * vitC/g choco]
                                      'data_availability': 1.0,
                                      'nutrient': {'id': self.vitamin_c.id,
                                                   'infoods_tagname': '',
                                                   'name': 'vitamin C',
                                                    'key': 'vitaminc',
                                                   'short_name': 'vitc',
                                                   'unit': 'mg'}}}
        print(response.data)
        self.assertDictEqual(response.data, EXPECTED_RES)
        
    @patch.object(Config, 'nutrient_calculations', [])
    def test_with_ratio(self):
        response = self.client.get('/api/recipe/%i/nutrients' % self.recipe.id, {"ratio": 0.5})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data['sugar']['value'], 7.5)
        self.assertEqual(response.data['vitamin C']['value'], 5.5)
        


    @patch.object(Config, 'nutrient_calculations', [])
    def test_with_loss_coeff(self):
        """
        Adding a conversion with some loss, and check if that affects the nutrient values
        """
        # One carrot is 100g with 10% loss due to pealing
        one_carrot = self.create_db_food_conversion(self.carrots, "1 carotte", 100, loss_coeff=0.1)
        self.carrots_ingredient.default_conversion = one_carrot
        self.carrots_ingredient.save()
        
        response = self.client.get('/api/recipe/%i/nutrients' % self.recipe.id)
        self.assertEqual(response.status_code, 200)

         # 90*0.1 + 50*0.02 [carrots g * (1 - loss_coeff) * vitC/ carrots + choco g * vitC/g choco]
        self.assertEqual(response.data['vitamin C']['value'], 10)

        # Unaffected
        self.assertEqual(response.data['vitamin C']['data_availability'], 1.)
        self.assertEqual(response.data['sugar']['value'], 15)

class TestNutrientCalculatorSelection(OptalimTest):

    def setUp(self):
        OptalimTest.setUp(self)
        NutrientCalculatorCache.reset()
        self.carrots = self.create_db_food('carrots')
        self.chocolate = self.create_db_food('chocolate')
        self.cherry = self.create_db_food('cherry')

        self.raw = RawState.objects.create(name="frais")
        self.frozen = RawState.objects.create(name="frozen")
        self.deeply_frozen = RawState.objects.create(name="deeply frozen")
        self.preserved = RawState.objects.create(name="preserved")
        self.another_raw_state = RawState.objects.create(name="bluh")
        
        self.not_cooked = CookingMethod.objects.create(name="cru")
        self.cooked = CookingMethod.objects.create(name="cooked")
        self.fried = CookingMethod.objects.create(name="fried")
        self.boiled = CookingMethod.objects.create(name="boiled")

        self.n = self.create_db_nutrient("awesomeness")

        # Fresh cherries
        self.fresh_cherries = FoodNutrient.objects.create(food=self.cherry, raw_state=self.raw, cooking_method=self.not_cooked,
                                    nutrient=self.n, amount_per_gram=15)
                                    
        # Preserved carrots
        self.preserved_carrots = FoodNutrient.objects.create(food=self.carrots, raw_state=self.preserved, cooking_method=self.not_cooked,
                                    nutrient=self.n, amount_per_gram=1)
        # Frozen carrots
        self.frozen_carrots = FoodNutrient.objects.create(food=self.carrots, raw_state=self.frozen, cooking_method=self.not_cooked,
                                    nutrient=self.n, amount_per_gram=1)
        # Frozen carrots fried
        self.frozen_fried_carrots = FoodNutrient.objects.create(food=self.carrots, raw_state=self.frozen, cooking_method=self.fried,
                                    nutrient=self.n, amount_per_gram=1)
        # Deeply frozen carrots fried
        self.deeply_frozen_fried_carrots = FoodNutrient.objects.create(food=self.carrots, raw_state=self.deeply_frozen, cooking_method=self.fried,
                                    nutrient=self.n, amount_per_gram=1)
                                    
        # Chocolate fried
        self.fried_choco = FoodNutrient.objects.create(food=self.chocolate, raw_state=self.raw, cooking_method=self.fried,
                                    nutrient=self.n, amount_per_gram=1)
        # Chocolate cooked
        self.cooked_choco = FoodNutrient.objects.create(food=self.chocolate, raw_state=self.raw, cooking_method=self.cooked,
                                    nutrient=self.n, amount_per_gram=1)
        # Frozen chocolate boiled
        self.frozen_boiled_choco = FoodNutrient.objects.create(food=self.chocolate, raw_state=self.frozen, cooking_method=self.boiled,
                                    nutrient=self.n, amount_per_gram=1)

        self.recipe = self.create_db_recipe()


        # Expected results of factorization per cooking method and raw state
        self.EXPECTED_CARROT_PER_COOKING_METHOD = {self.not_cooked.id: {self.preserved.id: set([self.preserved_carrots]),
                                                                   self.frozen.id: set([self.frozen_carrots])},
                                                   self.fried.id: {self.frozen.id: set([self.frozen_fried_carrots]),
                                                                   self.deeply_frozen.id: set([self.deeply_frozen_fried_carrots])}}
                                
        self.EXPECTED_CARROT_PER_RAW_STATE = {self.preserved.id: {self.not_cooked.id: set([self.preserved_carrots])},
                                              self.frozen.id: {self.not_cooked.id: set([self.frozen_carrots]),
                                                               self.fried.id: set([self.frozen_fried_carrots])},
                                              self.deeply_frozen.id: {self.fried.id: set([self.deeply_frozen_fried_carrots])}}
                
        self.EXPECTED_CHOCO_PER_COOKING_METHOD = {self.fried.id: {self.raw.id: set([self.fried_choco])},
                                                  self.cooked.id: {self.raw.id: set([self.cooked_choco])},
                                                  self.boiled.id: {self.frozen.id: set([self.frozen_boiled_choco])}}

        self.EXPECTED_CHOCO_PER_RAW_STATE = {self.raw.id: {self.fried.id: set([self.fried_choco]),
                                                           self.cooked.id: set([self.cooked_choco])},
                                             self.frozen.id: {self.boiled.id: set([self.frozen_boiled_choco])}}
                                             
        self.recipe_nutrient_calculator = RecipeNutrientCalculator(self.recipe)
        

    def test_retrieve_food_nutrients(self):
        """
        Test RecipeNutrientCalculator.retrieve_food_nutrients
        """
        per_cooking_method, per_raw_state = RecipeNutrientCalculator(self.recipe).\
                    retrieve_food_nutrients(self.create_db_ingredient(self.recipe, self.carrots, 100))

        self.assertDictEqual(per_cooking_method, self.EXPECTED_CARROT_PER_COOKING_METHOD)

        self.assertDictEqual(per_raw_state, self.EXPECTED_CARROT_PER_RAW_STATE)

        per_cooking_method, per_raw_state = RecipeNutrientCalculator(self.recipe).\
                    retrieve_food_nutrients(self.create_db_ingredient(self.recipe, self.chocolate, 100))

        self.assertDictEqual(per_cooking_method, self.EXPECTED_CHOCO_PER_COOKING_METHOD)
                
        self.assertDictEqual(per_raw_state, self.EXPECTED_CHOCO_PER_RAW_STATE)



    def _test_selection_on_choco(self, raw_state, cooking_method):
        """
        Test the selection of raw state and cooking method on chocolate
        available : (raw+fried), (raw+cooked), (frozen+boiled)
        """
        ing = self.create_db_ingredient(self.recipe, self.chocolate, 200,
                         raw_state=raw_state, cooking_method=cooking_method)

        return self.recipe_nutrient_calculator.select_best_cooking_parameters(ing,
                        self.EXPECTED_CHOCO_PER_RAW_STATE, self.EXPECTED_CHOCO_PER_COOKING_METHOD)
         

    def _test_selection_on_carrots(self, raw_state, cooking_method):
        """
        Test the selection of raw state and cooking method on carrots
        available : (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        """
        ing = self.create_db_ingredient(self.recipe, self.carrots, 200,
                         raw_state=raw_state, cooking_method=cooking_method)

        return self.recipe_nutrient_calculator.select_best_cooking_parameters(ing,
                        self.EXPECTED_CARROT_PER_RAW_STATE, self.EXPECTED_CARROT_PER_COOKING_METHOD)
                        
    def test_select_existing_nutrients(self):
        """
        We want data on (frozen+not cooked)
        Available: (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        It is available - we want it
        """
        res = self._test_selection_on_carrots(self.frozen, self.not_cooked)
        self.assertEqual(res, (self.frozen.id, self.not_cooked.id))

    def test_missing_cooking_method_with_default(self):
        """
        We want (frozen+boiled)
        Available: (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        The first one is the best because it has no cooking
        """
        res = self._test_selection_on_carrots(self.frozen, self.boiled)
        self.assertEqual(res, (self.frozen.id, self.not_cooked.id))


    def test_missing_raw_state_without_default(self):
        """
        We want (another_raw_state+not_cooked)
        Available: (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        Any of the first two is ok [frozen in priority because of a lower id)
        """
        res = self._test_selection_on_carrots(self.another_raw_state, self.not_cooked)
        self.assertEqual(res, (self.frozen.id, self.not_cooked.id))

    def test_missing_both(self):
        """
        We want (another_raw_state+boiled)
        Available: (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        None of them match - but still a preference for "not_cooked" (any of them) [frozen in priority because of a lower id]
        """
        res = self._test_selection_on_carrots(self.another_raw_state, self.boiled)
        self.assertEqual(res, (self.frozen.id, self.not_cooked.id))

    def test_missing_combination_priority_on_not_cooked(self):
        """
        We want (deeply_frozen+not_cooked)
        Available: (frozen+not_cooked), (preserved+not_cooked), (frozen + fried), (deeply_frozen + fried)
        not_cooked is more valuable than frozen, we want one of the two first ones [frozen in priority because of a lower id]
        """
        res = self._test_selection_on_carrots(self.deeply_frozen, self.not_cooked)
        self.assertEqual(res, (self.frozen.id, self.not_cooked.id))
        
        
    def test_missing_combination_priority_on_cooking_method(self):
        """
        We want raw+boiled
        But there are only (raw+fried), (raw+cooked), (frozen+boiled)
        Expecting -> frozen+boiled
        """
        res = self._test_selection_on_choco(self.raw, self.boiled)
        self.assertEqual(res, (self.frozen.id, self.boiled.id))

    def test_missing_both_priority_on_raw(self):
        """
        We want preserved + not_cooked
        But there are only (raw+fried), (raw+cooked), (frozen+boiled)
        Expecting -> raw+fried or raw+cooked  [cooked in priority because of lower id]
        """
        res = self._test_selection_on_choco(self.preserved, self.not_cooked)
        self.assertEqual(res, (self.raw.id, self.cooked.id))

    def test_missing_cooking_method_without_default(self):
        """
        We want frozen + not cooked
        But there are only (raw+fried), (raw+cooked), (frozen+boiled)
        Expecting -> frozen+boiled
        """
        res = self._test_selection_on_choco(self.frozen, self.not_cooked)
        self.assertEqual(res, (self.frozen.id, self.boiled.id))
        
    def test_fresh_cherry_when_frozen(self):
        
        ingredient = self.create_db_ingredient(self.recipe, self.cherry, 100, cooking_method=self.not_cooked, raw_state=self.frozen)
        
        self.recipe_nutrient_calculator.compute()
        
        values = self.recipe_nutrient_calculator.aggregated_nutrients
        self.assertEqual(len(values), 1)
        self.assertEqual(values[self.n.id], 100*15)



class TestNutrientCalculatorAlteration(OptalimTest):
    """
    Test the process of modifying the amount of nutrients by correcting cooking_method and raw_state
    """

    def setUp(self):
        OptalimTest.setUp(self)
        NutrientCalculatorCache.reset()
        self.recipe = self.create_db_recipe()
        self.carrots = self.create_db_food('carrots')
        self.vegetables = self.create_db_foodtype("vegetables")
        self.carrots.type = self.vegetables
        self.carrots.save()
        
        self.chocolate = self.create_db_food('chocolate')


        self.raw = RawState.objects.create(name="frais")
        self.frozen = RawState.objects.create(name="frozen")

        self.not_cooked = CookingMethod.objects.create(name="cru")
        self.cooked = CookingMethod.objects.create(name="cooked")
        self.supercooked = CookingMethod.objects.create(name="supercooked")

        self.nutri = self.create_db_nutrient("awesometitude")

        # After being frozen, any food sees its awesometitude reducing by 20%
        NutrientRawStateAlteration.objects.create(nutrient=self.nutri,
                                                  raw_state=self.frozen,
                                                  ratio=0.8)

        # After being cooked, any food sees its awesometitude reducing by 50%
        NutrientCookAlteration.objects.create(nutrient=self.nutri,
                                              cooking_method=self.cooked,
                                              ratio=0.5)

        # Cooking carrots reduces by 80% its weight
        self.create_db_cooking_method_effect(self.vegetables, self.cooked, 0.2)
        # Just creating an other cooking_method_effect object
        self.create_db_cooking_method_effect(self.vegetables, self.supercooked, 0.6)
        
        self.recipe_nutrient_calculator = RecipeNutrientCalculator(None)

    def test_from_raw_state_to_frozen(self):
        """
        Impact of freezing food
        Using NutrientCookAlteration
        """
        nutri_value = FoodNutrient.objects.create(food=self.carrots, nutrient=self.nutri,
                                    amount_per_gram=10,
                                    raw_state=self.raw, cooking_method=self.not_cooked)
    
        values = {nutri_value.nutrient_id: nutri_value.amount_per_gram}
        res = self.recipe_nutrient_calculator.apply_raw_state_effect(values, self.raw.id, self.frozen.id)

        self.assertEqual(values[self.nutri.id], 8)


    def _build_food_nutrient(self, raw_state=None, cooking_method=None):
        """
        Build a food nutrient object : 10 mg of awesometitude from 100g of carrots
        """
        if raw_state is None: raw_state = self.raw
        if cooking_method is None: cooking_method = self.not_cooked
        return FoodNutrient.objects.create(food=self.carrots, nutrient=self.nutri,
                                           amount_per_gram=10,
                                           raw_state=raw_state, cooking_method=cooking_method)
        


    def test_from_not_cooked_to_cooked(self):
        """
        Impact of cooking food
        Using NutrientRawStateAlteration
        """
        nutri_value = self._build_food_nutrient(self.raw, self.not_cooked)
        ingredient = self.create_db_ingredient(self.recipe, self.carrots, 100, cooking_method=self.cooked, raw_state=self.raw)

        recipe_nutrient_calculator = RecipeNutrientCalculator(None)
        
        with patch.object(RecipeNutrientCalculator, 'select_best_cooking_parameters',
                                                    return_value=(self.raw.id, self.not_cooked.id)):
                                                        
            with patch.object(RecipeNutrientCalculator, 'retrieve_food_nutrients',
                                                        return_value=({self.not_cooked.id: {self.raw.id: [nutri_value]}}, None)):
                recipe_nutrient_calculator.compute_ingredient_nutrients(ingredient)

        # Carrots have 10g of awesometitude from 100g of non-cooked carrots
        # Cooking carrots reduce by 50% its awesometitude
        self.assertEqual(recipe_nutrient_calculator.aggregated_nutrients, {nutri_value.nutrient_id: 5 * 100})
        


    def test_from_not_cooked_raw_state_to_frozen_cooked(self):
        """
        Impact of freezing AND cooking food
        """
        nutri_value = self._build_food_nutrient(self.raw, self.not_cooked)
        ingredient = self.create_db_ingredient(self.recipe, self.carrots, 100, cooking_method=self.cooked, raw_state=self.frozen)

        recipe_nutrient_calculator = RecipeNutrientCalculator(None)

        with patch.object(RecipeNutrientCalculator, 'select_best_cooking_parameters',
                                                    return_value=(self.raw.id, self.not_cooked.id)):

            with patch.object(RecipeNutrientCalculator, 'retrieve_food_nutrients',
                                                        return_value=({self.not_cooked.id: {self.raw.id: [nutri_value]}}, None)):
                recipe_nutrient_calculator.compute_ingredient_nutrients(ingredient)
                
        # 50% because of cooking, 20% because of freezing
        self.assertEqual(recipe_nutrient_calculator.aggregated_nutrients, {nutri_value.nutrient_id: 4 * 100})
        


    def test_from_cooked_to_cooked(self):
        """
        Calculation of cooked food from 100g of "NON-COOKED" food (user entry), with nutrient data on cooked food
        """
        nutri_value = self._build_food_nutrient(self.raw, self.cooked)
        ingredient = self.create_db_ingredient(self.recipe, self.carrots, 100, cooking_method=self.cooked, raw_state=self.raw)

        for i in range(2):
            # Trying twice to ensure that the calculation is stable when called twice in a row !

            recipe_nutrient_calculator = RecipeNutrientCalculator(None)

            with patch.object(RecipeNutrientCalculator, 'select_best_cooking_parameters',
                                                        return_value=(self.raw.id, self.cooked.id)):

                with patch.object(RecipeNutrientCalculator, 'retrieve_food_nutrients',
                                                            return_value=({self.cooked.id: {self.raw.id: [nutri_value]}}, None)):
                    recipe_nutrient_calculator.compute_ingredient_nutrients(ingredient)


            # We have 100g of not_cooked carrots

            # The equivalent of cooked carrots is 20g
            # Given the nutrients per gram of cooked carrots
            # nutrients per gram of cooked carrots = nutrients / 20g
            # nutrients per gram of not cooked carrots = nutrients / 100g
            # nutrient per grams of not cooked carrots = 20 * nutrients per gram of cooked carrots / 100
            # nutrients per grams of not cooked carrots = 2
            self.assertEqual(recipe_nutrient_calculator.aggregated_nutrients, {nutri_value.nutrient_id: 2 * 100})
        