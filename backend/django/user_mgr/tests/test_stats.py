
from common.test                import TestAPIWithLogin
from django.utils               import timezone
from recipe_mgr.models          import Recipe

import datetime

class TestStats(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.profile1 = self.create_db_profile()
        self.eater1   = self.create_db_eater(self.profile1)
        self.config_stage = self.create_db_config_stage()
        # users
        self.other      = self.create_db_user(name = "Other user", auto_create_main_profile = True)
        self.dietician  = self.create_db_user(name = "Test dietician", roles = ("dietician", ), auto_create_main_profile = True)
        self.admin      = self.create_db_user(name = "God", roles = ("admin", ), auto_create_main_profile = True)

    def init_meta_planning(self):
        # AGG = 1 + 2
        self.dt1 = self.create_db_dishtype(name="dt1")
        self.planning = self.create_db_meta_planning(with_n_days=1)
        self.meal_type = self.create_db_mealtype(dish_types=[self.dt1])
        self.meal_slot = self.create_db_mealslot(self.planning.sorted_days[0], meal_type=self.meal_type)

    def init_recipes(self):
        self.recipe1 = self.create_db_recipe(dish_types = [self.dt1], author = self.user, status = Recipe.STATUS_PUBLISHED)
        self.recipe2 = self.create_db_recipe(dish_types = [self.dt1], author = self.user, status = Recipe.STATUS_VALIDATED)

    def check_stats(self, **kargs):
        data = self.get_updated_stats()
        self.assertEqual(len(data), len(kargs))
        for stat, value in kargs.items():
            if stat not in data:
                print(">", stat)
            self.assertTrue(stat in data)
            if data[stat] != value:
                print(">", stat)
                print("-", value)
                print("+", data[stat])
            self.assertEqual(data[stat], value)

    def init_days(self):
        one_day = datetime.timedelta(seconds = 24 * 3600)
        # Suggested
        self.create_db_day(timezone.now() - 1 * one_day, user = self.user)
        self.create_db_day(timezone.now() + 1 * one_day, user = self.user)
        # Skipped
        self.create_db_day(timezone.now() - 2 * one_day, user = self.user, skipped = True)
        self.create_db_day(timezone.now() + 2 * one_day, user = self.user, skipped = True)
        # Validated
        self.create_db_day(timezone.now() - 3 * one_day, user = self.user, skipped = False)
        self.last_planned_day = self.create_db_day(timezone.now() + 3 * one_day, user = self.user, skipped = False)

    def api_get_stats(self, user = None, target = None, expected_code = 200):
        self.change_user(user = user)
        if target is None:
            target = self.user
        response = self.client.get('/api/user/%i/stats' % target.id)
        self.assertEqual(response.status_code, expected_code)
        if expected_code != response.status_code:
            print(response.data)
        if response.status_code != 200:
            return None
        return response.data

    def get_updated_stats(self):
        response = self.client.get('/api/user/%i/stats' % self.user.id)
        self.assertEqual(response.status_code, 200)
        return response.data

    def add_internal_recipe(self):
        self.assertEqual(Recipe.objects.count(), 2)
        self.create_db_recipe(author = self.user, internal = True, status = Recipe.STATUS_PUBLISHED)
        self.assertEqual(Recipe.objects.count(), 3)

    def test_user_stats(self):
        stats = {
            'last_planned_day': None,
            'diet_title': None,
            'published_recipes': 0,
            'signup_date': self.user.date_joined,
            'sex': 'male',
            'imc': 16.4,
            'weight': 56,
            'height': 185,
            'age': self.user.main_profile.age,
            'created_recipes': 0,
            'nb_profiles': 1,
            'completion_percentage': 0.0,
            'name': 'Kaloo',
            'nb_shopping_lists': 0,
            'last_planning': None,
            'nb_planned_days': 0,
        }
        self.check_stats(**stats)
        # Creating additionnal profile
        self.profile2 = self.create_db_profile()
        self.eater2   = self.create_db_eater(self.profile2)
        stats['nb_profiles'] = 2
        self.check_stats(**stats)
        # Completing stage
        self.create_db_config_completion(self.config_stage)
        stats['completion_percentage'] = 100
        self.check_stats(**stats)
        # Creating metaplanning
        self.init_meta_planning()
        self.check_stats(**stats)
        # Creating recipes
        self.init_recipes()
        stats['created_recipes'] = 2
        stats['published_recipes'] = 1
        self.check_stats(**stats)
        # Diet subscription
        diet = self.create_db_diet(key = "jeun", title = "Jeun")
        self.assign_diet_user(self.user, diet)
        stats['diet_title'] = "Jeun"
        self.check_stats(**stats)
        # Planning days
        self.init_days()
        stats['nb_planned_days'] = 4 # 2 skipped + 2 validated
        stats['last_planned_day'] = self.last_planned_day.date.date()
        stats['last_planning'] = self.last_planned_day.modification_date
        self.check_stats(**stats)
        # No recipe change when adding internal
        self.add_internal_recipe()
        self.check_stats(**stats)
        # Shopping list
        self.create_db_shopping_list(start_date = self.last_planned_day.date.date(), end_date = self.last_planned_day.date.date())
        stats['nb_shopping_lists'] = 1
        self.check_stats(**stats)

    def test_rights(self):
        expected = (
            (None,              401), # Anonymous
            (self.dietician,    200), # Dietician
            (self.other,        403), # Lambda user
            (self.admin,        200), # Admin
            (self.user,         200), # Himself
        )
        for user, expected_code in expected:
            self.api_get_stats(user = user, expected_code = expected_code)
