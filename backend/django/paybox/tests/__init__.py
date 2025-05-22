
from common.test                import TestAPIWithLogin
from common.date                import tz_datetime, today_aware, add_days

from django.utils               import timezone

from paybox.models              import Transaction

import datetime


class BasePayboxTest(TestAPIWithLogin):
    NB_MONTHS = 6
    
    def _create_dummy_transaction(self, status, enabled=False, ref='totoref'):
        """
        Creates a subscription and a transaction "started" on this subscription
        """
        
        kargs = {
            'level': 2,
            'start_date': datetime.date(2012, 4, 25),
            'nb_months': self.NB_MONTHS,
            'end_date': datetime.date(2012, 10, 25),
            'total_amount': 999*self.NB_MONTHS,
            'enabled': enabled
        }
        
        subscription = self.create_db_subscription(**kargs)
        
        kargs = {
            'ref': ref,
            'price': 999*self.NB_MONTHS,
            'ip': '127.0.0.1',
            'status': status,
            'created_at': tz_datetime(2012, 4, 25, 5)
        }
        
        if status != Transaction.STATUS_STARTED:
            kargs['transaction_id'] = 222
        
        return subscription, self.create_db_transaction(subscription, **kargs)
    
    def _create_dummy_transaction_today(self, status, ref = 'totoref', enabled = False):
        """
        Creates a subscription and a transaction "started" on this subscription
        """
        
        kargs = {
            'level': 2,
            'start_date': add_days(today_aware(), -1),
            'nb_months': self.NB_MONTHS,
            'end_date': add_days(today_aware(), 30 * self.NB_MONTHS),
            'total_amount': 999*self.NB_MONTHS,
            'enabled': enabled,
        }

        subscription = self.create_db_subscription(**kargs)
        
        kargs = {
            'ref': ref,
            'price': 999*self.NB_MONTHS,
            'ip': '127.0.0.1',
            'status': status,
            'created_at': today_aware()
        }
        
        if status == Transaction.STATUS_CONFIRMED:
            kargs['concluded_at'] = timezone.now()
        
        if status != Transaction.STATUS_STARTED:
            kargs['transaction_id'] = 222
        
        return subscription, self.create_db_transaction(subscription, **kargs)
