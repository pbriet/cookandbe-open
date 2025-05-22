
from common.model               import reload_object
from common.test                import TestAPIWithLogin
from common.date                import tz_aware

import datetime

class TestUserInfos(TestAPIWithLogin):

    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.date       = tz_aware(datetime.datetime(2015, 1, 1, 13, 37, 42))
        self.another    = self.create_db_user(name = "someone", date_joined = self.date,    auto_create_main_profile = True)
        self.admin      = self.create_db_user(name = "god",     roles = ("admin", ),        auto_create_main_profile = True)
        self.dietician  = self.create_db_user(name = "thierry", roles = ("dietician", ),    auto_create_main_profile = True)

    def api_get_user_infos(self, user, target, expected_code = 200):
        self.change_user(user = user)
        response = self.client.get('/secure/api/user/%i' % target.id)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def test_infos_access(self):
        expected = (
            (None,              401), # anonymous
            (self.user,         403), # admin area so... no
            (self.another,      403), # admin area so... no
            (self.admin,        200),
            (self.dietician,    200),
        )
        for user, expected_code in expected:
            print(user and user.first_name)
            self.api_get_user_infos(user, self.another, expected_code = expected_code)

    def test_infos_content(self):
        expected = {
            'first_name': self.another.first_name,
            'last_name': self.another.last_name,
            'email': self.another.email,
            'subscription_level': 0,
            'userid': self.another.id,
            'username': self.another.first_name,
            'creation_date': self.date,
            'main_address': None,
            'is_admin': False,
            'is_author': False,
            'is_moderator': False,
            'is_reviewer': False,
            'is_operator': False,
            'is_developer': False,
            'is_staff': False,
            'is_dietician': False,
        }
        data = self.api_get_user_infos(self.dietician, self.another)
        for key, value in expected.items():
            self.assertEqual(data[key], value, key)

class TestUserAddress(TestAPIWithLogin):

    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.another    = self.create_db_user(name = "someone", auto_create_main_profile = True)
        self.admin      = self.create_db_user(name = "god",     roles = ("admin", ),        auto_create_main_profile = True)
        self.dietician  = self.create_db_user(name = "thierry", roles = ("dietician", ),    auto_create_main_profile = True)

    def check_main_address(self, user, expected_address, expected_code = 200):
        self.change_user(user = user)
        response = self.client.get('/api/current_user/')
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data['main_address'] == expected_address

    def api_set_postal_code(self, user, target, postal_code, expected_code = 201):
        self.change_user(user = user)
        response = self.client.post("/api/user/%i/set_postal_code" % target.id, { "postal_code": postal_code })
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 201:
            return None
        return response.data

    def test_postal_code_rights(self):
        expected = (
            (None,              401), # anonymous
            (self.user,         201),
            (self.another,      403),
            (self.admin,        201),
            (self.dietician,    403),
        )
        for user, expected_code in expected:
            print(user and user.first_name)
            self.api_set_postal_code(user, self.user, "123456", expected_code = expected_code)

    def test_postal_code_data(self):
        TEST_CODE = "123456"
        self.check_main_address(self.user, None)
        data = self.api_set_postal_code(self.user, self.user, TEST_CODE)
        self.check_main_address(self.user, { "postal_code": TEST_CODE, "address": None })
        data = self.api_set_postal_code(self.user, self.user, TEST_CODE + "7")
        self.check_main_address(self.user, { "postal_code": TEST_CODE + '7', "address": None })
