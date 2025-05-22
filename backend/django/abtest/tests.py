from abtest.models          import AbCampaign, AbOption, AbChoice, AbRecord
from common.test            import TestAPIWithLogin

from mock                   import patch

import abtest.controller

class BaseTestAb(TestAPIWithLogin):
    
    def create_db_ab_option(self, key):
        return AbOption.objects.create(campaign=self.campaign, key=key)
  
    def create_db_ab_choice(self, option, user, unique_id):
        return AbChoice.objects.create(campaign=self.campaign, option=option, user=user, unique_id=unique_id)
    
    def create_db_ab_record(self, choice, objective):
        return AbRecord.objects.create(choice=choice, objective=objective)
  
    def setUp(self):
        super().setUp()
        self.client.cookies['op_uuid'] = 'AAA'
        self.campaign = AbCampaign.objects.create(key="test", description="my test")
        
        self.option1 = self.create_db_ab_option("option1")
        self.option2 = self.create_db_ab_option("option2")
        
    @patch.object(abtest.controller.random, 'choice', lambda x: x[0])
    def _test_consumption(self):
        self.assertEqual(AbChoice.objects.count(), 0)
        self.assertEqual(AbRecord.objects.count(), 0)
        
        # Initializing AB choice
        res = self.client.get('/api/ab/test/value')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["key"], "option1")
        
        self.assertEqual(AbChoice.objects.count(), 1)
        choice = AbChoice.objects.get()
        self.assertEqual(choice.unique_id, 'AAA')
        
        # Registering success
        res = self.client.post('/api/ab/test/success', {'objective': 'clicked'})
        self.assertEqual(res.status_code, 200)
        
        self.assertEqual(AbChoice.objects.count(), 1)
        self.assertEqual(AbRecord.objects.count(), 1)
        record = AbRecord.objects.get()
        self.assertEqual(record.objective, 'clicked')
        
        # Registering 2nd success
        res = self.client.post('/api/ab/test/success', { 'objective': 'clicked'})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(AbChoice.objects.count(), 1)
        self.assertEqual(AbRecord.objects.count(), 2)
        
        # Asking again for AB value
        for i in range(10):
            res = self.client.get('/api/ab/test/value')
            self.assertEqual(res.status_code, 200)
            # Should always return the same value
            self.assertEqual(res.data["key"], "option1")
            # Shouldn't create new Abchoices
            self.assertEqual(AbChoice.objects.count(), 1)
            


class TestAbReporting(BaseTestAb):
    PERMISSIONS         = ('admin',)
    
    def setUp(self):
        super().setUp()
        
        self.users = []
        for i in range(10):
            self.users.append(self.create_db_user())
    
    
    def test_reporting(self):
        user_choice = {}
        
        # User 1, 3, and 6 got option 1
        for i in (1, 3, 6):
            choice = self.create_db_ab_choice(self.option1, self.users[i], "user_%i" % i)
            user_choice[i] = choice
        
        # User 0, 2, and 4 got option 2
        for i in (0, 2, 4):
            choice = self.create_db_ab_choice(self.option2, self.users[i], "user_%i" % i)
            user_choice[i] = choice
        
        # User 1 did nothing
        # User 3 clicked once
        self.create_db_ab_record(user_choice[3], "clicked")
        # User 6 clicked twice
        for i in range(2):
            self.create_db_ab_record(user_choice[6], "clicked")
        
        # User 0 and 4 did nothing
        # User 2 clicked three times
        for i in range(3):
            self.create_db_ab_record(user_choice[2], "clicked")
            
        # User 2 bought once
        self.create_db_ab_record(user_choice[2], "bought")
            
        
        # Retrieving results
        response = self.client.get('/secure/api/ab/test/results')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
           {"key": "test",
            "description": "my test",
            "percentage":
                {"clicked": {
                    "option1": 66.67, # Users 3 and 6 YES - User 1 NO
                    "option2": 33.33, # User 2 only
                 },
                "bought": {
                    "option1": 0,
                    "option2": 33.33
                 }},
            "avg_value":
                {"clicked": {
                    "option1": 1, # 3 clicks / 3 users
                    "option2": 1, #3 clicks / 3 users
                 },
                "bought": {
                    "option1": 0,
                    "option2": 0.33
                 }},
             })


class TestAbConsumption(BaseTestAb):
    
    def test_ab_consumption_logged_in(self):
        self._test_consumption()
        
        choice = AbChoice.objects.get()
        self.assertEqual(choice.user_id, self.user.id)
        
        
    def test_success_before_value(self):
        """
        Error : calling success without calling value before !
        """
        res = self.client.post('/api/ab/test/success', { 'objective': 'clicked'})
        self.assertEqual(res.status_code, 200) # We don't want to raise an error message client-side
        self.assertEqual(res.data['status'], 'error')
        
        
class TestOfflineAbConsumption(BaseTestAb):
    LOGIN_ON_STARTUP = False

    def test_ab_consumption_not_logged_in(self):
        self._test_consumption()
        
        choice = AbChoice.objects.get()
        self.assertEqual(choice.user_id, None)
        
        # Registering test with invalid unique_id
        self.client.cookies['op_uuid'] = 'AAB'
        res = self.client.post('/api/ab/test/success', {'objective': 'clicked'})
        self.assertEqual(res.data['status'], 'error')
        
            