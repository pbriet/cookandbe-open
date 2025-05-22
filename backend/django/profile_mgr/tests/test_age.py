
from common.test            import OptalimTest
from common.mock_tools      import fake_today_decorator
from profile_mgr.models     import Profile
from common.date            import timezone, tz_aware
from mock                   import patch
import profile_mgr.models
from datetime               import datetime

class TestAge(OptalimTest):
    def setUp(self):
        self.profile  = self.create_db_profile(birth_date = datetime(1985, 1, 13))
        self.profile2 = self.create_db_profile(birth_date = datetime(1974, 5, 1))

    @fake_today_decorator(2013, 11, 3)
    def test_age_after_birthday(self):
        self.assertEqual(self.profile.age, 28)

    @fake_today_decorator(2014, 1, 3)
    def test_age_before_birthday(self):
        self.assertEqual(self.profile.age, 28)
        
    @fake_today_decorator(2014, 1, 13)
    def test_age_at_birthday(self):
        self.assertEqual(self.profile.age, 29)

    @fake_today_decorator(2014, 1, 15)
    def test_day_bigger_1(self):
        self.assertEqual(self.profile2.age, 39)
        
    @fake_today_decorator(2014, 5, 15)
    def test_day_bigger_2(self):
        self.assertEqual(self.profile2.age, 40)
        