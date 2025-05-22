from common.test                import TestAPIWithLogin


class TestCookingMethod(TestAPIWithLogin):
    PERMISSIONS = ("operator", )
    
    def setUp(self):
        TestAPIWithLogin.setUp(self)

        self.food_type = self.create_db_foodtype()

        self.food = self.create_db_food(food_type=self.food_type)

        self.cooking_methods = {
            "cru":      self.create_db_cooking_method(name = "test cru"),
            "cuit":     self.create_db_cooking_method(name = "test cuit"),
            "calcine":  self.create_db_cooking_method(name = "test calciné"),
        }
        
        self.cooked_effect = self.create_db_cooking_method_effect(self.food_type, self.cooking_methods["cuit"], 0.8)
    
    def test_retrieving(self):
        response = self.client.get('/secure/api/food_type/%i/cooking_method_effects' % self.food_type.id)
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['weight_ratio'], 0.8)
        self.assertEqual(data[0]['food_type'], self.food_type.id)
        self.assertEqual(data[0]['cooking_method'], self.cooking_methods["cuit"].id)
    
    def test_set_not_existing(self):
        response = self.client.post('/secure/api/food_type/%i/set_cooking_method_effect' % self.food_type.id,
                                    {'cooking_method_id': self.cooking_methods["calcine"].id,
                                     'weight_ratio': 0.2})
        self.assertEqual(response.status_code, 201)
        
        response = self.client.get('/secure/api/food_type/%i/cooking_method_effects' % self.food_type.id)
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        self.assertEqual(len(data), 2)
        
        self.assertEqual(data[0]['weight_ratio'], 0.8)
        self.assertEqual(data[0]['cooking_method'], self.cooking_methods["cuit"].id)
        self.assertEqual(data[1]['weight_ratio'], 0.2)
        self.assertEqual(data[1]['cooking_method'], self.cooking_methods["calcine"].id)
        
    def test_set_existing(self):
        response = self.client.post('/secure/api/food_type/%i/set_cooking_method_effect' % self.food_type.id,
                                    {'cooking_method_id': self.cooking_methods["cuit"].id,
                                     'weight_ratio': 0.4})
        self.assertEqual(response.status_code, 201)
        
        response = self.client.get('/secure/api/food_type/%i/cooking_method_effects' % self.food_type.id)
        self.assertEqual(response.status_code, 200)
        
        data = response.data['data']
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['weight_ratio'], 0.4)
        self.assertEqual(data[0]['food_type'], self.food_type.id)
    