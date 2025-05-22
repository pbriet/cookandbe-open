from common.test                        import TestAPIWithLogin
from planning_mgr.models                import MealSlotEater, MealType
from planning_mgr.controller.planning   import build_planning
import datetime


class TestGetMenu(TestAPIWithLogin):
    """
    Test retrieving a menu
    """

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()

        # Creating a metaplanning
        self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.reload_user()

        # Creating 7 days
        self.days = build_planning(self.user, datetime.date(2013, 2, 1), 7)

        # Adding another eater and recipes to every dish
        self.profile = self.create_db_profile()
        self.eater = self.create_db_eater(self.profile)
        self.recipe = self.create_db_recipe()

        for day in self.days:
            for meal_slot in day.meal_slots.all():
                MealSlotEater.objects.create(meal_slot=meal_slot, eater=self.eater)
                for dish in meal_slot.dishes.all():
                    self.create_db_dishrecipe(dish, self.recipe)

    def test_nb_queries(self):
        with self.assertNumQueries(11):
            self.client.get('/api/user/%i/menu/%s' % (self.user.id, self.days[0].date))


    def test_suggest_only_lunch_and_dinner(self):
        response = self.client.get('/api/user/%i/menu/%s' % (self.user.id, self.days[0].date))
        day0 = response.data['content']['days'][0]
        meal_type_ids = []
        for meal_type_id, meal_slot_content in day0['meal_slots'].items():
            if meal_slot_content['suggest']:
                meal_type_ids.append(meal_type_id)
        meal_types = [MealType.objects.get(pk=mid).name for mid in meal_type_ids]
        self.assertEqual(sorted(meal_types), ['Déjeuner', 'Dîner'])

