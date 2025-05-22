from common.test                import TestAPIWithLogin
from profile_mgr.models         import Profile, User
from planning_mgr.models        import MealSlotEater

class iTestMealSharing(TestAPIWithLogin):
    SUBSCRIPTION_LEVEL = 1 # Enable premium
    def setUp(self):
        super().setUp()
        # Some places
        self.places = dict()
        for place_key in ("home", "outside", "donoteat"):
            self.places[place_key] = self.create_db_mealplace(place_key)
        # Some user and profiles
        self.user2 = User.objects.create_user('test2', password='test')
        self.main_profile = self.create_db_profile(creator=self.user)
        self.user1_profile2 = self.create_db_profile(creator=self.user, auto_set_main_profile=False)
        self.user2_profile1 = self.create_db_profile(creator=self.user2, auto_set_main_profile=False)
        # Creating metaplanning
        self.meta = self.create_db_meta_planning(self.user, with_n_days=3)
        self.days = self.meta.sorted_days
        eaters = [self.create_db_eater(self.main_profile), self.create_db_eater(self.user1_profile2)]
        self.mt1 = self.create_db_mealtype("mt1")
        self.mt2 = self.create_db_mealtype("mt2")
        timetable = (
            # Day   Type         PlaceName      Eaters
            (0,     self.mt1,    "home",        eaters),
            (0,     self.mt2,    "outside",     eaters[:1]),
            (1,     self.mt1,    "donoteat",    []),
            (1,     self.mt2,    "home",        eaters[:1]),
            (2,     self.mt1,    "home",        eaters),
            (2,     self.mt2,    "outside",     eaters[:1]),
        )
        for week_day, meal_type, place_key, meal_eaters in timetable:
            self.create_db_mealslot(self.days[week_day], meal_type = meal_type, meal_place = self.places[place_key], with_eaters = meal_eaters)

    def get_meal_name(self, meals, meal_id):
        g = (meal['name'] for meal in meals if meal["id"] == meal_id)
        meal_name = next(g)
        self.assertRaises(StopIteration, next, g)
        return meal_name

class TestProfileAttendance(iTestMealSharing):
    def test_get_attendances(self):
        # Main profile
        response = self.client.get('/api/planning/%i/attendance' % self.user.meta_planning.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
            1 : {"mt2" : {self.main_profile.id : "home", self.user1_profile2.id : "donoteat"}},
            2 : {"mt1" : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
        }
        print(response.data["days"])
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(1, len(day_data))
            for meal_id, presences in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                for eater_profile_id, place_name in presences.items():
                    self.assertEqual(expectedAttendance[week_day][meal_name][eater_profile_id], place_name)

    def test_set_attendances(self):
        # Main profile should always be at the 5 non-'donoteat' meals
        self.assertEqual(MealSlotEater.objects.filter(eater__profile=self.main_profile).count(), 5)

        # This is quite high...  this feature needs some real refactoring
        with self.assertNumQueries(27):
            # Changing attendances
            self.response = self.client.put('/api/planning/%i/attendance' % self.user.meta_planning.id,
                                        {'days' : [
                                            {self.mt1.id : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
                                            {self.mt2.id : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
                                            {self.mt1.id : {self.main_profile.id : "home", self.user1_profile2.id : "donoteat"}},
                                        ]
                                        }, format = 'json')


        response = self.response
        self.assertEqual(response.status_code, 200)
        # Main profile
        response = self.client.get('/api/planning/%i/attendance' % self.user.meta_planning.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
            1 : {"mt2" : {self.main_profile.id : "home", self.user1_profile2.id : "home"}},
            2 : {"mt1" : {self.main_profile.id : "home", self.user1_profile2.id : "donoteat"}},
        }
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(1, len(day_data))
            for meal_id, presences in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                for eater_profile_id, place_name in presences.items():
                    self.assertEqual(expectedAttendance[week_day][meal_name][eater_profile_id], place_name)

        # Main profile should always be at all the meals
        self.assertEqual(MealSlotEater.objects.filter(eater__profile=self.main_profile).count(), 6)

    def test_set_attendances_forbidden(self):
        # Changing current user
        self.assertTrue(self.api_login(login = "test2", password = "test"))
        # Changing other user profile attendances
        response = self.client.put('/api/planning/%i/attendance' % self.user.meta_planning.id,
                                    {'days' : [
                                        {self.mt1.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"},
                                         self.mt2.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"}},
                                        {self.mt1.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"},
                                         self.mt2.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"}},
                                        {self.mt1.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"},
                                         self.mt2.id : {self.main_profile.id : "home",  self.user1_profile2.id : "home"}}
                                        ]
                                    }, format = 'json')
        self.assertEqual(response.status_code, 403)