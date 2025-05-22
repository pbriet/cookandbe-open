from common.test                import TestAPIWithLogin, add_permissions
from common.model               import reload_object
from recipe_mgr.models          import Food, Ingredient, Recipe, CookingMethod, RawState, FoodConversion
import json

class TestIngredientAPI(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.other_user = self.create_db_user()
        self.recipe1    = self.create_db_recipe(name = "carottes aux oranges", author = self.user, nb_people = 2)
        self.carottes   = self.create_db_food("carottes")
        self.oranges    = self.create_db_food("oranges")
        self.cru        = self.create_db_cooking_method(name = "cru")
        self.cuit       = self.create_db_cooking_method(name = "cuit")
        self.frais      = self.create_db_raw_state(name = "frais")
        self.default_carrots_cnv = self.create_db_food_conversion(food = self.carottes)

        # No more super powers
        self.user.user_roles.all().delete()
        self.user.save()
        self.assertFalse(self.user.is_admin)

    def test_add_get_remove(self):
        """
        Test adding, getting and removing an ingredient
        """
        response = self.client.post('/api/ingredient', {'food': self.carottes.id, 'recipe': self.recipe1.id,
                                                        'grams': 500, 'cooking_method': self.cru.id,
                                                        'raw_state': self.frais.id})
        self.assertEqual(response.status_code, 201)
        ingredient_id = response.data['id']

        response = self.client.get('/api/ingredient/%i' % ingredient_id)
        self.assertEqual(response.data['grams'], 500.0)
        self.assertEqual(response.data['recipe'], self.recipe1.id)
        self.assertEqual(response.data['cooking_method'], self.cru.id)
        self.assertEqual(response.data['previously_cooked'], False)
        self.assertEqual(response.data['default_conversion'], self.default_carrots_cnv.id)
        self.assertEqual(response.data['food']['name'], 'carottes')

        response = self.client.delete('/api/ingredient/%i' % ingredient_id)
        self.assertEqual(response.status_code, 204)

    def test_change_cooking_method(self):
        """
        Test changing the way the ingredient is cooked
        """
        ingredient = self.create_db_ingredient(self.recipe1, self.carottes, 500,
                                               cooking_method=self.cru, raw_state=self.frais)

        # Invalid query
        response = self.client.post('/api/ingredient/%i/set_cooking_method' % ingredient.id,
                         json.dumps({"wrong_parameter": 3}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

        # Right query
        response = self.client.post('/api/ingredient/%i/set_cooking_method' % ingredient.id,
                         json.dumps({"cooking_method_id": self.cuit.id}), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        reload_object(ingredient)
        self.assertEqual(ingredient.cooking_method, self.cuit)

        # Testing set_previously_cooked method

        # Invalid query (1)
        response = self.client.post('/api/ingredient/%i/set_previously_cooked' % ingredient.id,
                         json.dumps({"wrong_parameter": 3}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

        # Invalid query (2)
        response = self.client.post('/api/ingredient/%i/set_previously_cooked' % ingredient.id,
                         json.dumps({"previously_cooked": "plop"}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

        # Invalid query (2)
        response = self.client.post('/api/ingredient/%i/set_previously_cooked' % ingredient.id,
                         json.dumps({"previously_cooked": "yes"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)

        reload_object(ingredient)
        self.assertEqual(ingredient.previously_cooked, True)

    @add_permissions("admin")
    def test_permission_super_user(self):
        # Recipe belonging to another user
        self.recipe2 = self.create_db_recipe(name = "carottes aux oranges", author = self.other_user)
        self.init_default_ingredient_settings()

        # Adding ingredient
        response = self.client.post('/api/ingredient', {
            'food': self.carottes.id, 'recipe': self.recipe2.id,
            'grams': 500, 'cooking_method': self.cru.id,
            'raw_state': self.frais.id
        })
        self.assertEqual(response.status_code, 201)

        # Reading ingrédient
        ingredient2 = self.create_db_ingredient(recipe = self.recipe2, food = self.carottes, grams = 42,
                                               cooking_method=self.cru, raw_state=self.frais)
        response = self.client.get('/api/ingredient/%i' % ingredient2.id)
        self.assertEqual(response.status_code, 200)

        # Modifying ingredient
        response = self.client.get('/api/ingredient')
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/ingredient/%i/set_cooking_method' % ingredient2.id,
                         json.dumps({"cooking_method_id": self.cuit.id}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/ingredient/%i/set_previously_cooked' % ingredient2.id,
                         json.dumps({"previously_cooked": "yes"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        response = self.client.delete('/api/ingredient/%i' % ingredient2.id)
        self.assertEqual(response.status_code, 204)

    def test_permission_simple_user(self):
        # Recipe belonging to another user
        self.recipe2 = self.create_db_recipe(name = "carottes aux oranges", author = self.other_user)
        self.init_default_ingredient_settings()

        # Adding ingredient
        response = self.client.post('/api/ingredient', {
            'food': self.carottes.id, 'recipe': self.recipe2.id,
            'grams': 500, 'cooking_method': self.cru.id,
            'raw_state': self.frais.id
        })
        self.assertEqual(response.status_code, 403)

        # Reading ingredient
        ingredient2 = self.create_db_ingredient(recipe = self.recipe2, food = self.carottes, grams = 42,
                                               cooking_method=self.cru, raw_state=self.frais)
        response = self.client.get('/api/ingredient/%i' % ingredient2.id)
        self.assertEqual(response.status_code, 200)

        # Modifying ingredient
        response = self.client.get('/api/ingredient')
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/ingredient/%i/set_cooking_method' % ingredient2.id,
                         json.dumps({"cooking_method_id": self.cuit.id}), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        response = self.client.post('/api/ingredient/%i/set_previously_cooked' % ingredient2.id,
                         json.dumps({"previously_cooked": "yes"}), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        response = self.client.delete('/api/ingredient/%i' % ingredient2.id)
        self.assertEqual(response.status_code, 403)


class TestIngredientDefaultValues(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.test_food   = self.create_db_food("no default", with_conversion = True)
        self.assertTrue(self.test_food.conversions.count() == 1)
        self.default_food_conversion = self.test_food.conversions.get()
        self.cru         = self.create_db_cooking_method(name = "cru")
        self.frais       = self.create_db_raw_state(name = "frais")
        self.test_recipe = self.create_db_recipe(name = "gloubiboulga", author = self.user, nb_people=2)
        self.nutrients   = {
            "G": self.create_db_nutrient("G", "G"),
            "T": self.create_db_nutrient("T", "T"),
            "A": self.create_db_nutrient("A", "A"),
            "C": self.create_db_nutrient("C", "C"),
        }

    def _check_ingredient_default_values(self, food, expected, conversion = None, raw_state = None, cooking_method = None):
        kargs = {}
        if conversion is not None:
            kargs["conversion"] =  conversion
        if raw_state is not None:
            kargs["raw_state"] = raw_state
        if cooking_method is not None:
            kargs["cooking_method"] = cooking_method

        response = self.client.post("/secure/api/food/%i/set_defaults" % food.id,
                                    kargs)
        self.assertEqual(response.status_code, 201)
        response = self.client.post('/api/ingredient', {
            'food': food.id,
            'recipe': self.test_recipe.id,
            'grams': 500,
        })
        print(response.data)
        self.assertEqual(response.status_code, 201)
        for key, value in expected.items():
            self.assertEqual(response.data[key], value)

    @add_permissions("admin")
    def test_no_default_values(self):
        self._check_ingredient_default_values(self.test_food,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.cru.id, 'default_conversion': self.default_food_conversion.id}
        )

    @add_permissions("admin")
    def test_default_raw_state(self):
        self.test_state1 = self.create_db_raw_state(name = "test state 1")
        self.test_state2 = self.create_db_raw_state(name = "test state 2")
        self.test_state3 = self.create_db_raw_state(name = "test state 3")
        # From food nutrients
        self.create_db_foodnutrient(self.test_food, self.nutrients["G"], 0.5, self.test_state1, self.cru)
        self.create_db_foodnutrient(self.test_food, self.nutrients["C"], 0.5, self.test_state1, self.cru)
        self.create_db_foodnutrient(self.test_food, self.nutrients["G"], 0.5, self.test_state2, self.cru)
        self._check_ingredient_default_values(self.test_food,
            expected = {'raw_state': self.test_state1.id, 'cooking_method': self.cru.id, 'default_conversion': self.default_food_conversion.id},
        )
        # From food default
        self._check_ingredient_default_values(self.test_food, raw_state = self.test_state3.id,
            expected = {'raw_state': self.test_state3.id, 'cooking_method': self.cru.id, 'default_conversion': self.default_food_conversion.id},
        )

    @add_permissions("admin")
    def test_default_cooking_method(self):
        self.test_cooking1 = self.create_db_cooking_method(name = "test cooking 1")
        self.test_cooking2 = self.create_db_cooking_method(name = "test cooking 2")
        self.test_cooking3 = self.create_db_cooking_method(name = "test cooking 3")
        # From food nutrients
        self.create_db_foodnutrient(self.test_food, self.nutrients["G"], 0.5, self.frais, self.test_cooking1)
        self.create_db_foodnutrient(self.test_food, self.nutrients["C"], 0.5, self.frais, self.test_cooking2)
        self.create_db_foodnutrient(self.test_food, self.nutrients["G"], 0.5, self.frais, self.test_cooking2)
        self._check_ingredient_default_values(self.test_food,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.test_cooking2.id, 'default_conversion': self.default_food_conversion.id},
        )
        # From food default
        self._check_ingredient_default_values(self.test_food, cooking_method = self.test_cooking3.id,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.test_cooking3.id, 'default_conversion': self.default_food_conversion.id},
        )

    @add_permissions("admin")
    def test_default_conversion(self):
        self.default_food_conversion.delete()
        # Only one
        self.test_conversion1 = self.create_db_food_conversion(unit = "g", food = self.test_food)
        self.assertEqual(FoodConversion.objects.filter(food = self.test_food).count(), 1)
        self._check_ingredient_default_values(self.test_food,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.cru.id, 'default_conversion': self.test_conversion1.id},
        )
        # Avoiding generic units ('ml', 'litre', 'g', ...)
        self.test_conversion2 = self.create_db_food_conversion(unit = "portion", food = self.test_food)
        self._check_ingredient_default_values(self.test_food,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.cru.id, 'default_conversion': self.test_conversion2.id},
        )
        # From food default
        self.test_conversion3 = self.create_db_food_conversion(unit = "ml", food = self.test_food)
        self._check_ingredient_default_values(self.test_food, conversion = self.test_conversion3.id,
            expected = {'raw_state': self.frais.id, 'cooking_method': self.cru.id, 'default_conversion': self.test_conversion3.id},
        )
