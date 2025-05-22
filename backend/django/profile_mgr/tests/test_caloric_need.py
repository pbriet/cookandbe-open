from common.test                import OptalimTest
from django.utils               import timezone

import datetime

class TestCaloricNeed(OptalimTest):

    def _test_caloric_need(self, expected_calories, age=40, sex="female", weight=80, height=185,
                                work_score=1, moving_score=1, sport_score=0, metabolism=1.0,
                                forced_base_calories=None):

        birth_date = timezone.now() - datetime.timedelta(365*age + 180)

        self.profile = self.create_db_profile(birth_date=birth_date, sex=sex, weight=weight, height=height,
                                              work_score=work_score, moving_score=moving_score,
                                              sport_score=sport_score, metabolism=metabolism,
                                              forced_base_calories=forced_base_calories)

        self.assertEqual(round(self.profile.caloric_need()), expected_calories)

    def test_basic(self):
        self._test_caloric_need(2194)

    def test_menopause(self):
        self._test_caloric_need(2132, age=49, sex="female")
        self._test_caloric_need(2125, age=50, sex="female")
        self._test_caloric_need(1889, age=51, sex="female")
        self._test_caloric_need(1859, age=57, sex="female")

    def test_young_children(self):
        self._test_caloric_need(1147, age=3, weight=20, height=100)
        # Doesnt not depend on weight/height
        self._test_caloric_need(1147, age=3, weight=30, height=120)
        self._test_caloric_need(1052, age=2, weight=30, height=120)
        self._test_caloric_need(1960, age=9, weight=30, height=120)

        # Difference with male
        self._test_caloric_need(2103, age=9, weight=30, height=120, sex="male")


    def test_children(self):
        self._test_caloric_need(2112, age=12, weight=38, height=140, sport_score=4)

        # Test with default weight / height
        self._test_caloric_need(2141, age=12, weight=None, height=None, sport_score=4)

        # Test difference with male
        self._test_caloric_need(2304, age=12, sex="male", weight=None, height=None, sport_score=4)

        # Test different ages
        self._test_caloric_need(1938, age=10, weight=None, height=None, sport_score=4)
        self._test_caloric_need(2021, age=11, weight=None, height=None, sport_score=4)
        self._test_caloric_need(2036, age=10, sex="male", weight=None, height=None, sport_score=4)
        self._test_caloric_need(2154, age=11, sex="male", weight=None, height=None, sport_score=4)
        self._test_caloric_need(2232, age=13, weight=None, height=None, sport_score=4)
        self._test_caloric_need(2452, age=15, weight=None, height=None, sport_score=4)
        self._test_caloric_need(2506, age=17, weight=None, height=None, sport_score=4)


    def test_high_imc(self):
        self._test_caloric_need(2209, weight=125)
        self._test_caloric_need(2209, weight=175)

    def test_low_imc(self):
        self._test_caloric_need(2128, weight=55)
        self._test_caloric_need(2128, weight=25)

    def test_with_sport(self):
        self._test_caloric_need(2511, work_score=3, moving_score=3, sport_score=0)
        self._test_caloric_need(2670, work_score=3, moving_score=3, sport_score=10)
        self._test_caloric_need(2670, work_score=3, moving_score=3, sport_score=100)


    def test_with_provided_data(self):
        # Calories should be 1140 * 1.5 (NAP) = 1710
        self._test_caloric_need(1710, forced_base_calories=1140)