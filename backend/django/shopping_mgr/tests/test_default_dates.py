from common.mock_tools          import fake_today_decorator
from common.test                import TestAPIWithLogin

import datetime

class TestShoppingAvailableDays(TestAPIWithLogin):


    @fake_today_decorator(2012, 5, 1)
    def _available_days(self, expected_start=None, expected_end=None, expected_planned_dates=None):
        response = self.client.get('/api/user/%i/shopping_list/available_days' % self.user.id)
        self.assertEqual(response.status_code, 200)
        
        if expected_start is None:
            self.assertEqual(response.data['status'], 'no_planned_day')
            self.assertEqual(response.data['planned_dates'], [])
            return
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['start_date'].strftime("%Y-%m-%d"), expected_start)
        self.assertEqual(response.data['end_date'].strftime("%Y-%m-%d"), expected_end)
        self.assertEqual([d.strftime("%Y-%m-%d") for d in response.data['planned_dates']], expected_planned_dates)
    
    def test_with_no_days(self):
        # No days at all
        self._available_days()
        
        # No day planned
        self.create_db_day(date="2012-05-08", skipped=None)
        self.create_db_day(date="2012-05-06", skipped=True)
        self._available_days()
    
    def test_standard_planned_days(self):
        
        self.create_db_day(date="2012-05-08", skipped=False)
        self.create_db_day(date="2012-05-06", skipped=False)
        self.create_db_day(date="2012-05-07", skipped=False)
        
        self._available_days("2012-05-06", "2012-05-08", ["2012-05-06", "2012-05-07", "2012-05-08"])
        
    def test_one_day(self):
        self.create_db_day(date="2012-05-08", skipped=False)
        self._available_days("2012-05-08", "2012-05-08", ["2012-05-08", ])
        
    def test_with_skipped_day(self):
        
        self.create_db_day(date="2012-05-08", skipped=False)
        self.create_db_day(date="2012-05-06", skipped=False)
        self.create_db_day(date="2012-05-07", skipped=True)
        
        self._available_days("2012-05-06", "2012-05-08", ["2012-05-06", "2012-05-08"])
        
    def test_with_not_visited_day(self):
        
        self.create_db_day(date="2012-05-08", skipped=False)
        self.create_db_day(date="2012-05-06", skipped=False)
        self.create_db_day(date="2012-05-07", skipped=None)
        
        self._available_days("2012-05-06", "2012-05-08", ["2012-05-06", "2012-05-08"])

    def test_one_day_remaining(self):
        
        self.create_db_day(date="2012-05-08", skipped=True)
        self.create_db_day(date="2012-05-06", skipped=False)
        self.create_db_day(date="2012-05-07", skipped=None)
        
        self._available_days("2012-05-06", "2012-05-06", ["2012-05-06", ])
        
        
    def test_today_should_be_included(self):
        
        self.create_db_day(date="2012-05-01", skipped=False)
        self.create_db_day(date="2012-05-02", skipped=False)
        
        self._available_days("2012-05-01", "2012-05-02", ["2012-05-01", "2012-05-02"])
        
    def test_today_should_not_be_included_if_in_another_list(self):
        
        self.create_db_day(date="2012-05-01", skipped=False)
        self.create_db_shopping_list(start_date="2012-05-01", end_date="2012-05-01")
        
        self.create_db_day(date="2012-05-02", skipped=False)
        
        self._available_days("2012-05-02", "2012-05-02", ["2012-05-02"])
        
    def test_with_shopping_lists(self):
        
        # From 01/05/2012 to 09/05/2012
        for i in range(1, 10):
            self.create_db_day(date="2012-05-0%i" % i, skipped=False)
        
        self.create_db_shopping_list(start_date="2012-05-03", end_date="2012-05-05")
        
        self._available_days("2012-05-01", "2012-05-09", ["2012-05-01", "2012-05-02", "2012-05-06", "2012-05-07", "2012-05-08", "2012-05-09", ])
            
        
        
        