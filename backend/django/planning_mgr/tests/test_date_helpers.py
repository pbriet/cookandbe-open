from common.date            import get_next_week, tz_aware
from common.test            import OptalimTest
from mock                   import patch
import common.date        
from django.utils           import timezone
from datetime               import datetime

def fakeNow(year, month, day):
    return lambda: tz_aware(datetime(year, month, day))
    
class TestGetNextWeek(OptalimTest):
    """
    Test if the function get_next_week is working correctly
    """
    def _test_next_week(self, expected_first, expected_last, **kargs):
        first, last = get_next_week(**kargs)
        self.assertEqual(first.strftime("%Y-%m-%d"), expected_first)
        self.assertEqual(last.strftime("%Y-%m-%d"), expected_last)
        
    
    @patch.object(common.date.timezone, 'now', fakeNow(2013, 11, 27))
    def test_next_week(self):
        self._test_next_week("2013-12-02", "2013-12-08")

    @patch.object(common.date.timezone, 'now', fakeNow(2013, 11, 24))
    def test_next_week_when_sunday(self):
        self._test_next_week("2013-11-25", "2013-12-01")

    @patch.object(common.date.timezone, 'now', fakeNow(2013, 11, 18))
    def test_next_week_when_monday(self):
        self._test_next_week("2013-11-25", "2013-12-01")

    @patch.object(common.date.timezone, 'now', fakeNow(2013, 11, 27))
    def test_skip_weeks(self):
        self._test_next_week("2013-12-16", "2013-12-22", skip_weeks=2)
        