
from common.date            import add_days, today
from common.model           import reload_object
from common.mock_tools      import fake_django_login
from common.test            import OptalimTest

from user_mgr.auth          import update_user_subscription_level

from functools              import update_wrapper
from mock                   import patch

import datetime

class TestExpiredCheck(OptalimTest):
    """
    Test the behaviour of login
    """
    
    @fake_django_login
    def _check_expired(self, expired=False, subscription_level=0, active_subscription=None):
        """
        Test the login function and its return values
        """
        data = update_user_subscription_level(self.user)
        self.assertEqual(data, expired)
        reload_object(self.user)
        self.assertEqual(self.user.subscription_level, subscription_level)
        if active_subscription is not None:
            self.assertEqual(self.user.current_subscription, active_subscription)
            self.assertEqual(self.user.current_subscription.enabled, True)
            self.assertEqual(self.user.current_subscription.cancelled, False)
            self.assertEqual(self.user.current_subscription.level, subscription_level)
    
    def test_login_basic(self):
        """
        Test with a simple user
        """
        self._check_expired(expired=False, subscription_level=0)
        
    @fake_django_login
    def test_activated_subscription(self):
        """
        Test with a simple user
        """
        subscription = self.create_db_subscription(level=1, enabled=True)
        self._check_expired(expired=False, subscription_level=1, active_subscription=subscription)
        
    @fake_django_login
    def test_expired_subscription(self):
        """
        Test with a simple user
        """
        self.user.subscription_level = 2
        self.user.save()
        subscription = self.create_db_subscription(level=1, enabled=True, end_date=datetime.date(2002, 4, 3)) # Kinda expired
        self._check_expired(expired=True, subscription_level=0, active_subscription=None)
        
    @fake_django_login
    def test_futur_subscription(self):
        """
        Test with a simple user
        """
        subscription = self.create_db_subscription(level=1, enabled=True, start_date=add_days(today(), 2))
        self._check_expired(expired=False, subscription_level=0, active_subscription=None)
        
    @fake_django_login
    def test_cancelled_subscription(self):
        """
        Test with a simple user
        """
        subscription = self.create_db_subscription(level=1, enabled=True, cancelled=True)
        self._check_expired(expired=False, subscription_level=0, active_subscription=None)
        
    