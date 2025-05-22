from mock                       import patch

from common.test                import TestAPIWithLogin, OptalimTest
from common.mock_tools          import FakeNow, fake_today_decorator
from common.date                import make_utc
from common.model               import reload_object

from profile_mgr.controller     import calculate_auto_time_window
from profile_mgr.models         import Profile, ProfileValue, ProfileMetric

import datetime
import json

class TestProfileValuesHistory(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        with FakeNow(2014, 1, 1):
            self.profile = self.create_db_profile(weight=56, height=None)
        
        with FakeNow(2014, 1, 3):
            self.profile.weight = 60
            self.profile.height = 167
            self.profile.save()
        
        with FakeNow(2014, 2, 5):
            self.profile.metabolism = 1.2
            self.profile.save()

    def _stringify_res(self, res):
        return [(date.strftime('%Y-%m-%d'), value) for (date, value) in res]
   
    def _get_history_values(self, key):
        return self._stringify_res(self.profile.history_values(key))
        
    def test_history_values(self):
        # History of weight should be 56, then 60 and 60
        self.assertEqual(self._get_history_values("weight"),
                         [('2014-01-01', 56), ('2014-01-03', 60), ('2014-02-05', 60)])
        
        # History of height should be 167 and 167
        self.assertEqual(self._get_history_values("height"),
                         [('2014-01-03', 167), ('2014-02-05', 167)])
        
        # Metabolism, default value (1.0) then 1.2 - without having the same value saved twice
        self.assertEqual(self._get_history_values("metabolism"),
                         [('2014-01-01', 1.0), ('2014-02-05', 1.2)])
        
        
    def test_cannot_create_profile_value(self):
        """
        Testing that creating a ProfileValue is not possible in the standard way
        """
        def fcn():
            ProfileValue.objects.create(profile=self.profile, metric=ProfileMetric.objects.first(),
                                        float_value=2.3)
        self.assertRaises(AssertionError, fcn)

    def test_metric_history_api(self):
        response = self.client.get('/api/user/%i/profile/%i/metric_history' % (self.user.id, self.profile.id),
                                   {'key': 'weight'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._stringify_res(response.data['values']),
                         [('2014-01-01', 56), ('2014-01-03', 60), ('2014-02-05', 60)])

    def test_metric_history_api_with_minmaxdate(self):
        response = self.client.get('/api/user/%i/profile/%i/metric_history' % (self.user.id, self.profile.id),
                                   {'key': 'weight',
                                    'min_date': "2014-01-02T00:00:00Z",
                                    'max_date': "2014-01-15T00:00:00Z"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._stringify_res(response.data['values']),
                         [('2014-01-03', 60)])

    @fake_today_decorator(2014, 2, 5)
    def test_override_current_day(self):
        """
        Testing that setting two values on the same day -> only the last one is kept
        """
        with FakeNow(2014, 2, 5, 11, 0, 0):
            self.profile.metabolism = 1.4
            self.profile.save()

        with FakeNow(2014, 2, 5, 15, 0, 0):
            self.assertEqual(self._get_history_values("metabolism"),
                            [('2014-01-01', 1.0), ('2014-02-05', 1.4)])


    def test_set_metric_value_api(self):
        response = self.client.post('/api/user/%i/profile/%i/update_metrics' % (self.user.id, self.profile.id),
                                   {'metrics': json.dumps({'weight': 142.42})})
        self.assertEqual(response.status_code, 200)
        reload_object(self.profile)
        
        self.assertEqual(self.profile.weight, 142.42)
        


class TestAutoTimeWindow(OptalimTest):
    def setUp(self):
        super().setUp()
        self.profile = self.create_db_profile()
    
    def build_fake_history_values(self, entries):
        def fcn(*args, **kargs):
            res = []
            for entry in entries:
                year, month, day = entry[0]
                value = entry[1]
                res.append((datetime.datetime(year, month, day, 12, 0, 0), value))
            return res
        return fcn
    
    def test_too_close_times(self):
        """
        The first value should be dropped because it's less than stddev/2 (timely speaking)
        """
        VALUES = [((2014, 4, 1), 20),
                  ((2014, 4, 2), 30),
                  ((2014, 4, 15), 12),
                  ((2014, 4, 30), 32)]
        with patch.object(Profile, 'history_values', self.build_fake_history_values(VALUES)):
            min_date, max_date = calculate_auto_time_window(self.profile, "plop")
            self.assertEqual(min_date.strftime("%Y-%m-%d"), "2014-04-02")
            self.assertTrue(max_date is None)
            
            
    def test_too_distant_times(self):
        """
        The first value should be dropped because it's more than stddev*2 (timely speaking)
        """
        VALUES = [((2014, 4, 1), 20),
                  ((2014, 4, 26), 30),
                  ((2014, 4, 28), 12),
                  ((2014, 4, 30), 32)]
        with patch.object(Profile, 'history_values', self.build_fake_history_values(VALUES)):
            min_date, max_date = calculate_auto_time_window(self.profile, "plop")
            self.assertEqual(min_date.strftime("%Y-%m-%d"), "2014-04-26")
            self.assertTrue(max_date is None)