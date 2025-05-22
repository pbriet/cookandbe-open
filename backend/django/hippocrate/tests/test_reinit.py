
from common.date                        import tz_aware
from common.mock_tools                  import fake_today_decorator
from common.test                        import TestAPIWithLogin

from mock                               import patch

from optalim.settings                   import TESTING_WITH_PGSQL

from planning_mgr.controller.meta       import check_can_auto_update_from_meta
from planning_mgr.controller.planning   import build_planning
from planning_mgr.models                import Day, Planning

from shopping_mgr.models                import ShoppingList

import datetime
import hippocrate.views.api

class TestReinit(TestAPIWithLogin):
    """
    Test reinitialization of planning  (metaplanning change) :
    - detection
    - application
    """

    def setUp(self):
        super().setUp()
        self._init_default_planning()
        self.reload_user()
    
    @fake_today_decorator(2014, 1, 23)
    def _init_default_planning(self):
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
    
    def _build_days(self, from_date):
        days = build_planning(self.user, from_date, 7)
        return days
    
    def _call_suggest_api(self, date):
        response = self.client.post('/api/user/%i/suggest/%s' % (self.user.id, date), {'init': True})
        self.assertEqual(response.status_code, 200)
        return response
    
    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2014, 1, 23)
    def _test_auto_reinit(self, suggest_date, mock_planning_generation):
        """
        - having a block of 7 days with skipped=None, shopping_list=None
        - Asking for suggestions on the some day
        - With a new metaplanning
        
        check that :
        - it rebuilds the correct days
        - it calls darwin
        """
        creation_date = datetime.date(2014, 1, 24)
        days = self._build_days(creation_date)
        
        self.user.meta_planning.set_modified(tz_aware(datetime.datetime(2014, 1, 23, 12, 0, 0)))
        
        self._call_suggest_api(suggest_date)
        
        self.assertEqual(mock_planning_generation.call_count, 1)
        
        
        for day in days:
            in_db = list(Day.objects.filter(pk=day.id))
            if len(in_db) == 0: in_db = None
            else:               in_db = in_db[0]
            if day.date >= suggest_date:
                if TESTING_WITH_PGSQL:
                    # This check doesn't work with SQLite, as
                    # newly created days take the ids of the previously
                    # deleted ones !
                    self.assertTrue(in_db is None) # rebuilt
                self.assertTrue(Day.objects.filter(date=day.date).count(), 1)
            else:
                self.assertTrue(in_db is not None) # not rebuilt
    
    def test_auto_reinit_second_day(self):
        """
        Autoreinit on second day : it should create a new planning, and delete 6 days of the initial planning
        """
        suggest_date = datetime.date(2014, 1, 25)
        self._test_auto_reinit(suggest_date)
        
        self.assertEqual(Day.objects.filter(date__gte=datetime.date(2008, 1, 1)).count(), 8) # The old first day + the new block of 7 days
        plannings = sorted(Planning.objects.all(), key=lambda x: x.id)
        self.assertEqual(len(plannings), 2)
        self.assertEqual(plannings[0].days.count(), 1)
        self.assertEqual(plannings[1].days.count(), 7)
    
    def test_shopping_list_should_be_deleted(self):
        """
        Test that a shopping list created on days reinitialized is deleted
        IF it belongs to user, of course...
        """
        other_user = self.create_db_user("user2")
        my_shopping_list = self.create_db_shopping_list(datetime.date(2014, 1, 20), datetime.date(2014, 1, 28))
        my_old_shopping_list = self.create_db_shopping_list(datetime.date(2014, 1, 20), datetime.date(2014, 1, 23))
        his_shopping_list = self.create_db_shopping_list(datetime.date(2014, 1, 20), datetime.date(2014, 1, 28), user=other_user)
        
        suggest_date = datetime.date(2014, 1, 24)
        self._test_auto_reinit(suggest_date)
        
        self.assertEqual(ShoppingList.objects.count(), 2)
        shopping_list_ids = [shl.id for shl in ShoppingList.objects.all()]
        self.assertEqual(sorted(shopping_list_ids), [my_old_shopping_list.id, his_shopping_list.id])

    def test_auto_reinit_first_day(self):
        """
        Autoreinit on first day : it should create a new planning,
        and delete all the previous days + planning
        """
        suggest_date = datetime.date(2014, 1, 24)
        self._test_auto_reinit(suggest_date)
        
        self.assertEqual(Day.objects.filter(date__gte=datetime.date(2008, 1, 1)).count(), 7) # The new block of 7 days
        plannings = sorted(Planning.objects.all(), key=lambda x: x.id)
        self.assertEqual(len(plannings), 1)
        self.assertEqual(plannings[0].days.count(), 7)
    
    @fake_today_decorator(2014, 1, 23)
    def test_check_can_auto_update_from_meta(self):
        """
        Test the function check_can_auto_update_from_meta
        """
        creation_date = datetime.date(2014, 1, 24)
        days = self._build_days(creation_date)
        day = [d for d in days if d.date.day == 25][0] # 25/01/2014
        later_day = [d for d in days if d.date.day == 27][0] # 27/01/2014
        
        def _check_res(val):
            # Calls check_can_auto_update_from_meta
            self.assertEqual(check_can_auto_update_from_meta(self.user, day), val)
        
        # Metaplanning is not modified
        _check_res(False)
        
        self.user.meta_planning.set_modified(tz_aware(datetime.datetime(2014, 1, 23, 12, 0, 0)))
        
        # Now, it is modified
        _check_res(True)
        
        # It has a shopping_list !
        shopping_list = self.create_db_shopping_list()
        day.shopping_list = shopping_list
        day.save()
        
        # shopping_list <> locked
        _check_res(False)
        
        # It is skipped !
        day.shopping_list = None
        day.skipped = True
        day.save()
        
        # Skipped ? Will not update... no use
        _check_res(False)
        
        # It is validated !
        day.skipped = False
        day.save()
        
        # Validated ? Don't reset user suggestions without asking
        _check_res(False)
        
        day.skipped = None
        day.save()
        
        # Back to "default"
        _check_res(True)
        
        # A later day is skipped
        later_day.skipped = True
        later_day.save()
        
        # Shouldn't be an issue
        _check_res(True)
        
        # A later day is validated
        later_day.skipped = False
        later_day.save()
        
        # Don't update automatically
        _check_res(False)
        
        