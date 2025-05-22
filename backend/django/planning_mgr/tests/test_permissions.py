from common.test                import TestAPIWithLogin
from common.date                import get_next_week
from user_mgr.models            import User

class TestPlanningMgrPermissions(TestAPIWithLogin):
    CREATE_DEFAULT_USER = False
    LOGIN = 'test@test.fr'
    PASSWORD = 'test'

    def setUp(self):
        # Creating a "simple" user
        self.user = User.objects.create_user('test@test.fr', 'test')
        self.other_user = User.objects.create_user('other@other.fr', 'other')
        
        super().setUp()
        self.init_default_meal_type_settings()
        dish_type = self.create_db_dishtype()
        

        first_day_next_week = get_next_week()[0]

        # A planning that belongs to this user
        self.my_meta_planning = self.create_db_meta_planning(user=self.user)
        my_planning           = self.create_db_planning(user=self.user, start_date=first_day_next_week)
        self.my_days          = my_planning.sorted_days
        self.my_mealslot      = self.create_db_mealslot(self.my_days[0])
        self.my_dish          = self.create_db_dish(self.my_mealslot, dish_type)
        self.user.meta_planning = self.my_meta_planning
        self.user.save()

        # A planning that doesn't belong to this user
        self.his_meta_planning = self.create_db_meta_planning(user=self.other_user)
        his_planning      = self.create_db_planning(user=self.other_user, start_date=first_day_next_week)
        self.his_days     = his_planning.sorted_days
        self.his_mealslot = self.create_db_mealslot(self.his_days[0])
        self.his_dish     = self.create_db_dish(self.his_mealslot, dish_type)
        self.other_user.meta_planning = self.his_meta_planning
        self.other_user.save()

        self.day0 = self.my_days[0].date

    def test_read(self):
        # READ
        # The planning/mealslot/dish should be readable only for the owner
        for url, expected_result in\
                [('meal_slot/%s' % self.my_mealslot.id, 200),
                ('dish/%s' % self.my_dish.id, 200),
                ('user/%s/day/%s' % (self.user.id, self.day0), 200),
                ('user/%s/menu/%s' % (self.user.id, self.day0), 200),
                ('meal_slot/%s' % self.his_mealslot.id, 403),
                ('dish/%s' % self.his_dish.id, 403),
                ('user/%s/day/%s' % (self.other_user.id, self.day0), 403),
                ('user/%s/menu/%s' % (self.other_user.id, self.day0), 403)]:
            print(url)
            response = self.client.get('/api/' + url)
            self.assertEqual(response.status_code, expected_result)

    def test_write(self):
        # WRITE (update)
        # The dish should be writable only for the owner
        for url, expected_result in\
                [('dish/%s' % self.my_dish.id, 400),
                ('dish/%s' % self.his_dish.id, 403)]:
            print(url)
            response = self.client.put('/api/' + url)
            self.assertEqual(response.status_code, expected_result)

        # WRITE (post)
        for url, args, expected_result in\
                [('user/%s/set_dishrecipes/%s' % (self.user.id, self.my_dish.id), {}, 400),
                 ('user/%s/add_days/%s' % (self.user.id, self.day0), {}, 400),
                 ('user/%s/add_days/%s' % (self.other_user.id, self.day0), {}, 403),
                 ('user/%s/set_dishrecipes/%s' % (self.user.id, self.his_dish.id), {'recipe_ids': [1]}, 403),
                 ('user/%s/set_dishrecipes/%s' % (self.other_user.id, self.my_dish.id), {'recipe_ids': [1]}, 403),]:
            print(url, args)
            response = self.client.post('/api/' + url, args)
            print(response.data)
            self.assertEqual(response.status_code, expected_result)