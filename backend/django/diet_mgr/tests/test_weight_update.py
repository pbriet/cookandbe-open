
from common.test                import OptalimTest
from common.mock_tools          import FakeNow, fake_today_decorator

from mock                       import patch

import diet_mgr.tasks

class TestWeightReminderTask(OptalimTest):
    
    @patch('diet_mgr.tasks.sendmail_template')
    @fake_today_decorator(2014, 2, 5)
    def _test_weight_reminder(self, expected_user_id, mock_sendmail, expected_update_date=None, create_recent_day=True):
        if create_recent_day:
            self.create_db_day("2014-02-03") # User has recent activity
        diet_mgr.tasks.remind_weight_update()
        if expected_user_id is None:
            self.assertFalse(mock_sendmail.called)
            return
        self.assertTrue(mock_sendmail.called)
        args, kwargs = mock_sendmail.call_args
        self.assertEqual(args[2]['last_update'].strftime("%Y-%m-%d"), expected_update_date)
        self.assertEqual(len(kwargs['users']), 1)
        self.assertEqual(kwargs['users'][0].id, expected_user_id)
    
    def _test_with_update_required(self, expect_success=True, create_recent_day=True):
        if expect_success:
            user_id = self.user.id
        else:
            user_id = None
        with FakeNow(2013, 10, 7, 12, 45):
            # Updated 120 days before yesterday
            self.create_db_profile()
        self._test_weight_reminder(user_id, expected_update_date="2013-10-07", create_recent_day=create_recent_day)
    
    def test_update_required_std(self):
        self._test_with_update_required()
    
    def test_update_required_but_no_activity(self):
        self._test_with_update_required(expect_success=False, create_recent_day=False)
        
    def test_update_required_but_dated_activity1(self):
        self.create_db_day("2014-01-27") # User has dated activity
        self._test_with_update_required(expect_success=False, create_recent_day=False)
        
    def test_update_required_but_dated_activity2(self):
        self.create_db_day("2013-01-02") # User has very dated activity
        self._test_with_update_required(expect_success=False, create_recent_day=False)
    
    def test_update_not_required_std(self):
        with FakeNow(2013, 10, 6, 12, 45):
            # Updated 121 days before yesterday
            self.create_db_profile()
        self._test_weight_reminder(None)
        
    def test_update_not_required_std2(self):
        with FakeNow(2013, 10, 8, 12, 45):
            # Updated 119 days before yesterday
            self.create_db_profile()
        self._test_weight_reminder(None)
        
    
    def test_slim_diet(self):
        """
        With slim diet, update date is 7 days instead of 120
        """
        self.slim = self.create_db_diet("slim")
        self.assign_diet_user(self.user, self.slim, objective=60, mode='eat_different')
        
        with FakeNow(2013, 10, 7, 12, 45):
            # Updated 120 days before yesterday
            profile = self.create_db_profile()
        self._test_weight_reminder(None)
        
        with FakeNow(2014, 1, 28, 12, 45):
            # Updated 7 days before yesterday
            profile.weight = 55
            profile.save()
        self._test_weight_reminder(self.user.id, expected_update_date="2014-01-28", create_recent_day=False)
        
        with FakeNow(2014, 1, 29, 12, 45):
            # Updated 7 days before today
            profile.weight = 57
            profile.save()
        self._test_weight_reminder(None, create_recent_day=False)
        
        with FakeNow(2014, 2, 4, 12, 45):
            # Updated yesterday
            profile.weight = 57
            profile.save()
        self._test_weight_reminder(None, create_recent_day=False)
            