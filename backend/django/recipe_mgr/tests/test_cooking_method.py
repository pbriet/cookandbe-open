from common.test                import TestAPIWithLogin, add_permissions
from nutrient.models            import Nutrient, FoodNutrient
from recipe_mgr.models          import Food, FoodTag, Ingredient, RawState,\
                                       CookingMethod
from mock                       import patch

class TestCookingMethod(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)

        self.food = self.create_db_food()

        self.cooking_methods = {
            "cru":      self.create_db_cooking_method(name = "test cru"),
            "cuit":     self.create_db_cooking_method(name = "test cuit"),
            "calcine":  self.create_db_cooking_method(name = "test calciné"),
        }

        self.raw     = RawState.objects.create(name = "frais")
        tmp_nutrient = Nutrient.objects.create(name = "fake nutrient")

        self.create_db_foodnutrient(self.food, tmp_nutrient, 0.5, cooking_method = self.cooking_methods['cru'])
        self.create_db_foodnutrient(self.food, tmp_nutrient, 0.5, cooking_method = self.cooking_methods['cuit'])

    def _check_cooking_methods(self, expected_code, expected_methods = None, food = None):
        kargs   = dict()
        api_url = '/api/cooking_method'
        if food is not None:
            api_url += '/food/%i' % food.id
        response = self.client.get(api_url, kargs)
        print(api_url, response.data)
        self.assertEqual(expected_code, response.status_code)
        self.assertEqual(CookingMethod.objects.count(), len(response.data))
        if food is not None:
            cm_ids = set([cm.id for cm in expected_methods])
            for cm in response.data:
                self.assertTrue((cm['id'] in cm_ids) is cm['available'])

    def test_all_cooking_methods(self):
        self.assertTrue(self.is_authenticated())
        self.assertEqual(self.user.user_roles.count(), 0)
        self._check_cooking_methods(200)

    def test_food_cooking_methods(self):
        self.assertTrue(self.is_authenticated())
        self.assertEqual(self.user.user_roles.count(), 0)
        self._check_cooking_methods(200, set([self.cooking_methods[cm_str] for cm_str in ('cru', 'cuit')]), food = self.food)
