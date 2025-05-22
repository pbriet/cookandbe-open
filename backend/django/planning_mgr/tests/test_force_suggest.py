from common.test                import TestAPIWithLogin
from common.model               import reload_object

import datetime

class TestDayForceSuggest(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.init_db_profile_eater()
        self.planning = self.create_db_planning(nb_days = 3, start_date = datetime.date(2014, 3, 3))
        self.days = self.planning.sorted_days

    def test_force_suggest(self):
        data = [
            # Day,  suggest,    response,   skipped
            (0,     True,       200,        False),
            (1,     False,      200,        True),
            (2,     '',       400,        None),
        ]
        for day_index, suggest, response_code, skipped in data:
            day = self.days[day_index]
            response = self.client.post('/api/user/%i/day/%s/force_as_filled' % (self.user.id, day.date), {"value": suggest})
            self.assertEqual(response.status_code, response_code)
            reload_object(day)
            self.assertEqual(day.skipped, skipped)

    def test_force_suggest_shopped_day(self):
        shopping_list = self.create_db_shopping_list(start_date = datetime.date(2014, 3, 3), end_date = datetime.date(2014, 3, 7))
        for day in self.days:
            reload_object(day)
            self.assertEqual(day.shopping_list_id, shopping_list.id)
        for day_index, suggest in enumerate([True, False, '']):
            response = self.client.post('/api/user/%i/day/%s/force_as_filled' % (self.user.id, self.days[day_index].date), {"value": suggest})
            self.assertEqual(response.status_code, 400)
