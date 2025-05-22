from common.test                import TestAPIWithLogin, add_permissions
from nutrient.models            import Nutrient, FoodNutrient
from recipe_mgr.models          import Food, FoodTag, Ingredient, RawState,\
                                       CookingMethod
from mock                       import patch
import recipe_mgr.views.food

class TestFoodAPI(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)

        self.sweet = self.create_db_foodtype(name="sucré")
        self.salted = self.create_db_foodtype(name="salé")

        self.f1 = self.create_db_food(name="chocolate", food_type=self.sweet)
        self.f2 = self.create_db_food(name="carrot", food_type=self.salted)
        self.f3 = self.create_db_food(name="white chocolate", food_type=self.sweet)
        self.f4 = self.create_db_food(name="carrot cake", food_type=self.sweet)

        self.test_frais = RawState.objects.create(name="test frais")
        self.test_surgele = RawState.objects.create(name="test surgelé")

        self.test_cru = CookingMethod.objects.create(name="test cru")
        self.test_cuit = CookingMethod.objects.create(name="test cuit")

        tmp_nutrient = Nutrient.objects.create(name="fake nutrient")

        FoodNutrient.objects.create(food=self.f2, nutrient=tmp_nutrient, raw_state=self.test_frais,
                                                  cooking_method=self.test_cru, amount_per_gram=0.5)
        FoodNutrient.objects.create(food=self.f2, nutrient=tmp_nutrient, raw_state=self.test_frais,
                                                  cooking_method=self.test_cuit, amount_per_gram=0.8)

    def test_get(self):
        response = self.client.get('/secure/api/food/%i' % self.f2.id)
        self.assertEqual(response.status_code, 200)
        expected = {'id': self.f2.id, 'name': 'carrot', 'full_name': 'carrot', 'enabled': True, 'type': self.salted.id}
        for key, value in expected.items():
            self.assertEqual(response.data.get(key, ''), value)

        response = self.client.get('/secure/api/food/55')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get('/secure/api/food/invalid')
        self.assertEqual(response.status_code, 404)

    @add_permissions("admin")
    def test_put(self):
        f_temp = self.create_db_food(name="temp_food", full_name="temp_food_full", enabled=True)

        values_to_change = {'name': 'temp_food_changed', 'full_name': 'temp_food_full_changed',
                            'enabled': False, 'type': self.food_type.id,
                            'shopping_category': self.default_shopping_category.id}

        # Modification
        response = self.client.put('/secure/api/food/%i' % f_temp.id, values_to_change)
        self.assertEqual(response.status_code, 200)

        # Retrieval post-modifications
        response = self.client.get('/secure/api/food/%i' % f_temp.id)
        for key, value in values_to_change.items():
            self.assertEqual(response.data.get(key, ''), value)

        # Testing invalid values
        with patch.dict(values_to_change, {'name': ''}):
            response = self.client.put('/secure/api/food/%i' % f_temp.id, values_to_change)
            self.assertEqual(response.status_code, 400)

    @add_permissions("admin")
    def test_post(self):
        """
        Test creation of food
        """

        food_values = {'name': 'new_food', 'full_name': 'new_food_full',
                       'enabled': False, 'type': self.sweet.id,
                       'shopping_category': self.default_shopping_category.id}
        response = self.client.post('/secure/api/food', food_values)
        self.assertEqual(response.status_code, 201)
        f = Food.objects.get(name='new_food')
        for key, value in food_values.items():
            if key in ('type', 'shopping_category'):
                self.assertEqual(getattr(f, key).id, value)
            else:
                self.assertEqual(getattr(f, key), value)

    @patch.object(recipe_mgr.views.food, 'FOOD_SEARCH_SHOW_CATEGORIES_OVER', 2)
    def test_search(self):
        response = self.client.get('/api/food/search/choco', {'return_categories': True})
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([food['name'] for food in response.data['foods']], ["chocolate", "white chocolate"])
        self.assertEqual([(c['type']['name'], c['nb_food']) for c in response.data['types']], [("sucré", 2)])
        self.assertFalse(response.data['empty'])

        response = self.client.get('/api/food/search/c', {'type_id': self.salted.id, 'return_categories': True})
        self.assertEqual(response.status_code, 200)
        self.assertEqual([food['name'] for food in response.data['foods']], ["carrot"])
        self.assertEqual([(c['type']['name'], c['nb_food']) for c in response.data['types']], [("salé", 1)])
        self.assertFalse(response.data['empty'])

        response = self.client.get('/api/food/search/c')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([food['name'] for food in response.data['foods']], ["carrot", "chocolate"])
        self.assertEqual([(c['type']['name'], c['nb_food']) for c in response.data['types']], [("sucré", 3), ("salé", 1)])
        self.assertFalse(response.data['empty'])
        
        response = self.client.get('/api/food/search/poire')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['empty'])
        
    @patch.object(recipe_mgr.views.food, 'FOOD_SEARCH_SHOW_CATEGORIES_OVER', 2)
    def test_search_multiple_keywords(self):
        response = self.client.get('/api/food/search/choco%20te')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([food['name'] for food in response.data['foods']], ["chocolate", "white chocolate"])
        self.assertFalse(response.data['empty'])
        
        response = self.client.get('/api/food/search/choco%20ite')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([food['name'] for food in response.data['foods']], ["white chocolate", ])
        self.assertFalse(response.data['empty'])

    def test_search_disabled(self):
        response = self.client.get('/api/food/search/c')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 4)
        self.assertTrue(self.f1.id in set([item['id'] for item in response.data['foods']]))
        # Switching f1 to disabled
        self.f1.enabled = False
        self.f1.save()
        response = self.client.get('/api/food/search/c')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 3)
        self.assertTrue(self.f1.id not in set([item['id'] for item in response.data['foods']]))

    @add_permissions("operator")
    def test_search_disabled_operator(self):
        response = self.client.get('/api/food/search/c')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 4)
        self.assertTrue(self.f1.id in set([item['id'] for item in response.data['foods']]))
        # Switching f1 to disabled
        self.f1.enabled = False
        self.f1.save()
        response = self.client.get('/api/food/search/c')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 4)
        self.assertTrue(self.f1.id in set([item['id'] for item in response.data['foods']]))

    def test_get_available_raw_states(self):
        response = self.client.get('/secure/api/food/%i/available_raw_states' % self.f2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(d['name'] for d in response.data), set(['test frais']))

    def test_get_available_cooking_methods(self):
        response = self.client.get('/secure/api/food/%i/available_cooking_methods' % self.f2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(d['name'] for d in response.data), set(['test cuit', 'test cru']))

    def test_get_available_options(self):
        response = self.client.get('/secure/api/food/%i/available_options' % self.f2.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(d['name'] for d in response.data['cooking_methods']), set(['test cuit', 'test cru']))
        self.assertEqual(set(d['name'] for d in response.data['raw_states']), set(['test frais']))
    
