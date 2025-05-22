from common.test                import TestAPIWithLogin
from django.utils               import timezone
import datetime

class TestNextMeal(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.init_default_meal_place_settings()
        self.dish_type = self.create_db_dishtype()
        self.recipe = self.create_db_recipe(dish_types=[self.dish_type])
        self.meta = self.create_db_meta_planning()
        
    def _create_meal_slot(self, dt, place = None, day = None):
        if day is None or day.date != dt.date():
            day = self.create_db_day(dt.date())
        meal_slot = self.create_db_mealslot(day, time = dt.time(), meal_place = place)
        dish = self.create_db_dish(meal_slot, order = 1, dish_type = self.dish_type)
        for dish in meal_slot.dishes.all():
            self.create_db_dishrecipe(dish, self.recipe)
        return meal_slot
    
    def test_no_planned_meal(self):
        response = self.client.get('/api/user/%i/next_meal' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "No meal planned"})


    def test_next_meal_is_outside(self):
        # 1 meal outside in 1h, the next meal at home in 6h
        dt = timezone.now() + datetime.timedelta(seconds = 1 * 3600)
        meal_slot_outside = self._create_meal_slot(dt, place = self.create_db_mealplace("sandwich"))
        dt = timezone.now() + datetime.timedelta(seconds = 6 * 3600)
        meal_slot_home = self._create_meal_slot(dt, place = self.places["home"], day=meal_slot_outside.day)
        
        response = self.client.get('/api/user/%i/next_meal' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], dt.date())
        self.assertEqual(len(response.data['dishes']), 1)
        self.assertEqual(response.data['meal_place'], "home")

    def test_planned_meal_now(self):
        dt = timezone.now()
        self._create_meal_slot(dt, place = self.places["home"])
        response = self.client.get('/api/user/%i/next_meal' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], dt.date())
        self.assertEqual(len(response.data['dishes']), 1)
        self.assertEqual(response.data['meal_place'], "home")

    def test_planned_meal_one_hour_ago(self):
        dt = timezone.now() - datetime.timedelta(seconds = 3600)
        self._create_meal_slot(dt, place = self.places["home"])
        response = self.client.get('/api/user/%i/next_meal' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['date'], dt.date())
        self.assertEqual(len(response.data['dishes']), 1)
        self.assertEqual(response.data['meal_place'], "home")

    def test_planned_meal_three_hours_ago(self):
        dt = timezone.now() - datetime.timedelta(seconds = 3 * 3600)
        self._create_meal_slot(dt, place = self.places["home"])
        response = self.client.get('/api/user/%i/next_meal' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "No meal planned"})

