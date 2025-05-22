from common.test                import TestAPIWithLogin
from user_mgr.models            import User

class TestProfileMgrPermissions(TestAPIWithLogin):
    CREATE_DEFAULT_USER = False
    LOGIN = 'test@test.fr'
    PASSWORD = 'test'

    def setUp(self):
        food_tag = self.create_db_food_tag()
        # Creating a "simple" user
        self.user = User.objects.create_user('test@test.fr', 'test')
        self.other_user = User.objects.create_user('other@other.fr', 'other')

        self.my_profile = self.create_db_profile(creator=self.user)
        self.my_taste = self.create_db_taste(food_tag, profile=self.my_profile)
        self.my_restricted_food = self.create_db_restricted_food(food_tag, profile=self.my_profile)

        self.his_profile = self.create_db_profile(creator=self.other_user)
        self.his_taste = self.create_db_taste(food_tag, profile=self.his_profile)
        self.his_restricted_food = self.create_db_restricted_food(food_tag, profile=self.his_profile)
        super().setUp()

    def test_read(self):
        # You should be able to read everything (profile / taste / restricted food)
        for url, expected_result in\
                [('user/%i/profile/%i' % (self.user.id, self.my_profile.id), 200),
                ('taste/%s' % self.my_taste.id, 200),
                ('restricted_food/%s' % self.my_restricted_food.id, 200),
                ('user/%i/profile/%s' % (self.other_user.id, self.his_profile.id), 403),
                ('taste/%s' % self.his_taste.id, 403),
                ('restricted_food/%s' % self.his_restricted_food.id, 403)]:
            print(url)
            response = self.client.get('/api/' + url)
            self.assertEqual(response.status_code, expected_result)

    def test_write(self):
        # You should only be able to write your own profiles/tastes/restricted_foods
        for url, expected_result in [
                    ('user/%i/profile/%s' % (self.user.id, self.my_profile.id), 400),
                    ('taste/%s' % self.my_taste.id, 400),
                    ('restricted_food/%s' % self.my_restricted_food.id, 400),
                    ('user/%i/profile/%s' % (self.other_user.id, self.his_profile.id), 403),
                    ('taste/%s' % self.his_taste.id, 403),
                    ('restricted_food/%s' % self.his_restricted_food.id, 403),
                ]:
            print(url)
            response = self.client.put('/api/' + url)
            self.assertEqual(response.status_code, expected_result)
