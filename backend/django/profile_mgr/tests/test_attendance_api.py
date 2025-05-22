from common.test                import TestAPIWithLogin
from planning_mgr.models        import MealSlot
from profile_mgr.models         import Profile, User
from eater_mgr.models           import Eater

class iTestProfileAttendance(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        # Some places
        self.places = dict()
        for place_key in ("home", "outside", "donoteat"):
            self.places[place_key] = self.create_db_mealplace(place_key)
        # Some user and profiles
        self.user2 = User.objects.create_user('test2', password='test')
        self.main_profile = self.create_db_profile(creator=self.user)
        self.user1_profile2 = self.create_db_profile(creator=self.user)
        self.user2_profile1 = self.create_db_profile(creator=self.user2)
        # Creating metaplanning
        self.metaplanning = self.create_db_meta_planning(self.user, with_n_days=3)
        self.days = self.metaplanning.sorted_days
        eaters = [self.create_db_eater(self.main_profile), self.create_db_eater(self.user1_profile2)]
        self.mt1 = self.create_db_mealtype("mt1")
        self.mt2 = self.create_db_mealtype("mt2")
        timetable = (
            # Day   Type         PlaceName      Eaters
            (0,     self.mt1,    "home",        eaters),
            (0,     self.mt2,    "outside",     eaters[:1]),
            (1,     self.mt1,    "home",        eaters[:1]),
            (1,     self.mt2,    "donoteat",    []),
            (2,     self.mt1,    "home",        eaters[:1]),
            (2,     self.mt2,    "outside",     eaters[:1]),
        )
        for week_day, meal_type, place_key, meal_eaters in timetable:
            self.create_db_mealslot(self.days[week_day], meal_type = meal_type, meal_place = self.places[place_key], with_eaters = meal_eaters)

    def get_meal_name(self, meals, meal_id):
        g = (meal['name'] for meal in meals if meal["id"] == meal_id)
        meal_name = next(g)
        self.assertRaises(StopIteration, next, g)
        return meal_name

class TestProfileAttendance(iTestProfileAttendance):
    def test_get_attendances(self):
        # Main profile
        response = self.client.get('/api/profile/%i/attendance' % self.main_profile.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : "home",        "mt2" : "outside"},
            1 : {"mt1" : "home",        "mt2" : "donoteat"},
            2 : {"mt1" : "home",        "mt2" : "outside"}
        }
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(2, len(day_data))
            for meal_id, place_key in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                self.assertEqual(expectedAttendance[week_day][meal_name], place_key)
        # Secondary profile
        response = self.client.get('/api/profile/%i/attendance' % self.user1_profile2.id)
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : "home",        "mt2" : "donoteat"},
            1 : {"mt1" : "donoteat",    "mt2" : "donoteat"},
            2 : {"mt1" : "donoteat",    "mt2" : "donoteat"}
        }
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(2, len(day_data))
            for meal_id, place_key in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                self.assertEqual(expectedAttendance[week_day][meal_name], place_key)

    def test_set_attendances(self):
        # Changing attendances
        response = self.client.put('/api/profile/%i/attendance' % self.main_profile.id,
                                    {'days' : [
                                        {self.mt1.id : "outside",   self.mt2.id : "home"},
                                        {self.mt1.id : "donoteat",  self.mt2.id : "home"},
                                        {self.mt1.id : "home",      self.mt2.id : "outside"}
                                        ]
                                    }, format = 'json')
        self.assertEqual(response.status_code, 200)
        
        
        # Every meal should have the main eater
        for meal_slot in MealSlot.objects.all():
            profile_ids = [eater.profile_id for eater in meal_slot.eaters.all()]
            self.assertTrue(self.main_profile.id in profile_ids)
        
        # NEW TIMETABLE SHOULD BE
        #timetable = (
            ## Day   Type         PlaceName      Eaters
            #(0,     self.mt1,    "outside",     eaters[:1]),
            #(0,     self.mt2,    "home",        eaters),
            #(1,     self.mt1,    "donoteat",    []),
            #(1,     self.mt2,    "home",        eaters),
            #(2,     self.mt1,    "home",        eaters[:1]),
            #(2,     self.mt2,    "outside",     eaters[:1]),
        #)
        
        
        # Main profile
        response = self.client.get('/api/profile/%i/attendance' % self.main_profile.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : "outside",     "mt2" : "home"},
            1 : {"mt1" : "donoteat",    "mt2" : "home"},
            2 : {"mt1" : "home",        "mt2" : "outside"}
        }
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(2, len(day_data))
            for meal_id, place_key in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                self.assertEqual(expectedAttendance[week_day][meal_name], place_key)
        # Secondary profile
        response = self.client.get('/api/profile/%i/attendance' % self.user1_profile2.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["days"]) == 3)
        expectedAttendance = {
            0 : {"mt1" : "donoteat",   "mt2" : "home"},
            1 : {"mt1" : "donoteat",   "mt2" : "home"},
            2 : {"mt1" : "donoteat",   "mt2" : "donoteat"}
        }
        for week_day, day_data in enumerate(response.data["days"]):
            self.assertEqual(2, len(day_data))
            for meal_id, place_key in day_data.items():
                meal_name  = self.get_meal_name(response.data["meals"], meal_id)
                print(week_day, meal_name, place_key)
                self.assertEqual(expectedAttendance[week_day][meal_name], place_key)

    def test_set_attendances_forbidden(self):
        # Changing other user profile attendances
        response = self.client.put('/api/profile/%i/attendance' % self.user2_profile1.id,
                                    {'days' : [
                                        {'mt1' : "outside",     'mt2' : "home"},
                                        {'mt1' : "donoteat",    'mt2' : "home"},
                                        {'mt1' : "donoteat",    'mt2' : "home"}
                                        ]
                                    }, format = 'json')
        self.assertEqual(response.status_code, 403)
