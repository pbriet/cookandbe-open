from common.test                            import TestAPIWithLogin
from common.mock_tools                      import fake_today_decorator
from mock                                   import patch
from planning_mgr.models                    import Day
from planning_mgr.controller.planning       import build_planning
import datetime
import hippocrate.views.api
import common.date
import planning_mgr.controller

class TestSuggest(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self._init_default_planning()
        self.reload_user()
        self.recipe = self.create_db_recipe()
        
    @fake_today_decorator(2014, 1, 27)
    def _init_default_planning(self):
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        
    def _days(self):
        """
        Return the list of days (in strings) built, by exluding metaplanning days
        """
        meta_days_ids = set(d.id for d in self.user.meta_planning.days.all())
        days = Day.objects.order_by('date').exclude(id__in=meta_days_ids)
        
        # Suggest should validate the day suggested
        nb_validated_days = len([d for d in days if d.is_validated()])
        self.assertEqual(nb_validated_days, 1)
        
        return [day.date.strftime("%Y-%m-%d") for day in days]
        
    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2014, 1, 27)
    def test_suggest_with_no_days(self, mock_planning_generation):
        """
        First call to suggest : there is no days
        Check it creates 7 new ones and ask the generation
        """
        date = datetime.date(2014, 1, 28)
        response = self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {'init': True})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(self._days(), ["2014-01-28", "2014-01-29", "2014-01-30", "2014-01-31",
                                        "2014-02-01", "2014-02-02", "2014-02-03"])

        self.assertEqual(mock_planning_generation.call_count, 1)
    
    @fake_today_decorator(2014, 1, 27)
    @patch.object(hippocrate.views.api, 'MAX_NB_PLANNED_DAYS', 10)
    def test_suggest_too_far_in_future(self):
        date = datetime.date(2014, 2, 9)
        response = self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {'init': True})
        self.assertEqual(response.status_code, 200)
        
        self.assertEqual(response.data['status'], 'too_much_in_future')
        self.assertEqual(response.data['max_nb_days'], 10)
    
    @fake_today_decorator(2014, 1, 27)
    def _create_initial_week(self, from_date):
        days = build_planning(self.user, from_date, 7)
        for day in days:
            for meal_slot in day.meal_slots.all():
                for dish in meal_slot.dishes.all():
                    self.create_db_dishrecipe(dish, self.recipe)
            assert day.is_filled()
        return days
        
    @fake_today_decorator(2014, 1, 27)
    def _call_suggest_api(self, date, kargs):
        response = self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), kargs)
        self.assertEqual(response.status_code, 200)
    
    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2014, 1, 27)
    def test_suggest_in_existing_filled_week(self, mock_planning_generation):
        """
        Asking for suggestions for a day which is already included in a filled week
        """
        date = datetime.date(2014, 1, 28)
        self._create_initial_week(datetime.date(2014, 1, 24))
            
        self._call_suggest_api(date, {'init': True})
        self.assertEqual(self._days(), ["2014-01-24", "2014-01-25", "2014-01-26", "2014-01-27",
                                        "2014-01-28", "2014-01-29", "2014-01-30"])
        self.assertEqual(mock_planning_generation.call_count, 0)


    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2014, 1, 27)
    def test_suggest_with_gap(self, mock_planning_generation):
        """
        Asking for suggestions two days after the end of last generated week
        """
        date = datetime.date(2014, 1, 28)
        self._create_initial_week(datetime.date(2014, 1, 20))

        self._call_suggest_api(date, {'init': True})
        self.assertEqual(self._days(), ["2014-01-20", "2014-01-21", "2014-01-22", "2014-01-23",
                                        "2014-01-24", "2014-01-25", "2014-01-26", "2014-01-28",
                                        "2014-01-29", "2014-01-30", "2014-01-31", "2014-02-01",
                                        "2014-02-02", "2014-02-03"])
        self.assertEqual(mock_planning_generation.call_count, 1)
        
        
    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2014, 1, 27)
    def test_suggest_on_locked_day(self, mock_planning_generation):
        """
        Asking for suggestions two days after the end of last generated week
        """
        days = self._create_initial_week(datetime.date(2014, 1, 24))
        day = [d for d in days if d.date.day == 28][0] # 28/01/2014
        
        shopping_list = self.create_db_shopping_list()
        
        # Not calling the algorithm if day has a shopping list
        day.shopping_list = shopping_list
        day.save()
        self._call_suggest_api(day.date, {'recalculate': True})
        self.assertEqual(mock_planning_generation.call_count, 0)
        
        # Not calling the algorithm if day is skipped
        day.shopping_list = None
        day.skipped = True
        day.save()
        self._call_suggest_api(day.date, {'recalculate': True})
        self.assertEqual(mock_planning_generation.call_count, 0)
        
        # Checking in normal conditions
        day.skipped = False
        day.save()
        self._call_suggest_api(day.date, {'recalculate': True})
        self.assertEqual(mock_planning_generation.call_count, 1)