from common.test                import TestAPIWithLogin
from django.utils               import timezone
from planning_mgr.models        import MealSlot
from mock                       import patch
import datetime


class TestDayMeals(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.init_db_profile_eater()

        r1 = self.r1 = self.create_db_recipe("r1")
        r1b = self.r1b = self.create_db_recipe("r1b")
        r2 = self.r2 = self.create_db_recipe("r2")
        r3 = self.r3 = self.create_db_recipe("r3")
        
        self.dish_type = self.create_db_dishtype()

        planning = self.create_db_planning()
        self.days = planning.sorted_days

        self.meal_type1 = self.create_db_mealtype("Petit déjeuner")
        self.meal_type2 = self.create_db_mealtype("Déjeuner")
        self.meal_type3 = self.create_db_mealtype("Dîner")
        
        self.meal_slot1 = self.create_db_mealslot(self.days[0], time=datetime.time(8), meal_type = self.meal_type1)
        self.meal_slot1b = self.create_db_mealslot(self.days[0], time=datetime.time(12), meal_type = self.meal_type2)
        self.meal_slot2 = self.create_db_mealslot(self.days[2], time=datetime.time(20), meal_type = self.meal_type3)

        self.dish1 = self.create_db_dish(self.meal_slot1, self.dish_type)
        self.create_db_dishrecipe(self.dish1, r1)
        self.dish1b = self.create_db_dish(self.meal_slot1b, self.dish_type)
        self.create_db_dishrecipe(self.dish1b, r1b)
        
        self.dish2_1 = self.create_db_dish(self.meal_slot2, self.dish_type)
        self.create_db_dishrecipe(self.dish2_1, r2)
        
        self.dish2_2 = self.create_db_dish(self.meal_slot2, self.dish_type)
        self.create_db_dishrecipe(self.dish2_2, r3)

    def test_in_two_days(self):
        
        response = self.client.get('/api/user/%i/day/%s' % (self.user.id, self.days[2].date))
        
        self.assertEqual(response.status_code, 200)

        self.assertTrue(len(response.data['content']), 1)

        self.assertEqual(response.data['content'][0]['meal_type'], 'Dîner')
        self.assertEqual(response.data['content'][0]['id'], self.meal_slot2.id)


    def test_first_day(self):

        response = self.client.get('/api/user/%i/day/%s' % (self.user.id, self.days[0].date))
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data['content']), 2)
        
        self.assertEqual(response.data['content'][0]['meal_type'], 'Petit déjeuner')
        self.assertEqual(response.data['content'][0]['id'], self.meal_slot1.id)

        self.assertEqual(response.data['content'][1]['meal_type'], 'Déjeuner')
        self.assertEqual(response.data['content'][1]['id'], self.meal_slot1b.id)


    def test_day_before(self):

        response = self.client.get('/api/user/%i/day/2000-01-01' % self.user.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "this day is not generated")


    def test_day_after(self):
        response = self.client.get('/api/user/%i/day/2099-01-01' % self.user.id)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], "this day is not generated")
