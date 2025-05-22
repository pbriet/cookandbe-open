from common.test                import TestAPIWithLogin
from user_mgr.models            import User

class TestRecipeMgrPermissions(TestAPIWithLogin):
    CREATE_DEFAULT_USER = False
    LOGIN = 'test@test.fr'
    PASSWORD = 'test'

    def setUp(self):
        # Creating a "simple" user
        self.user = User.objects.create_user('test@test.fr', 'test')
        self.other_user = User.objects.create_user('other@other.fr', 'other')
        super().setUp()

        self.nutrient = self.create_db_nutrient()
        self.food = self.create_db_food()
        self.init_default_ingredient_settings()
        self.conversion = self.create_db_food_conversion(self.food)
        self.food_tag = self.create_db_food_tag()
        self.recipe_tag = self.create_db_recipe_tag()
        self.dish_type = self.create_db_dishtype()

        self.URLS = [
            '/secure/api/nutrient/%s' % self.nutrient.id,
            '/secure/api/food/%s' % self.food.id,
            '/secure/api/raw_state/%s' % self.raw.id,
            '/secure/api/cooking_method/%s' % self.not_cooked.id,
            '/secure/api/food_type/%s' % self.food_type.id,
            '/secure/api/food_conversion/%s' % self.conversion.id,
            '/secure/api/food_tag/%s' % self.food_tag.id,
            '/secure/api/recipe_tag/%s' % self.recipe_tag.id,
            '/secure/api/dish_type/%s' % self.dish_type.id
        ]

    def test_read(self):
        # You should be able to read everything (profile / taste / restricted food)
        for url in self.URLS:
            print(url)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_write(self):
        # You should not be able to update anything
        for url in self.URLS:
            print(url)
            response = self.client.put(url)
            self.assertEqual(response.status_code, 403)
            response = self.client.post(url)
            self.assertEqual(response.status_code, 403)
