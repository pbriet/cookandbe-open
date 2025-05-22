from common.mock_tools          import fake_today_decorator
from common.model               import reload_object
from common.test                import TestAPIWithLogin

from django.conf                import settings
from django.utils               import timezone

from paybox.models              import Subscription

import datetime

if settings.ENABLE_PUBLIC_PAYMENT:

    class TestFreeTrial(TestAPIWithLogin):


        def setUp(self):
            super().setUp()

            self.diet_free = self.create_db_diet("free diet", min_subscription_level=0,
                                                 free_trial_days=7)

            self.diet_1_month = self.create_db_diet("diet with 1 month", min_subscription_level=2,
                                                    free_trial_days=30)


        def _subscribe_to_diet(self, diet):
            self.user.diet = diet
            self.user.save()


        @fake_today_decorator(2012, 1, 2)
        def test_try_1_month(self):
            self._subscribe_to_diet(self.diet_1_month)
            response = self.client.post('/api/user/%i/activate_free_trial/' % self.user.id)
            self.assertEqual(response.status_code, 200)
            reload_object(self.user)

            self.assertEqual(Subscription.objects.count(), 1)
            sub = Subscription.objects.get()

            self.assertEqual(sub.level, 2)
            self.assertEqual(self.user.subscription_level, 2)
            self.assertEqual(sub.user_id, self.user.id)
            self.assertEqual(sub.end_date, datetime.date(2012, 2, 1))
            self.assertEqual(sub.nb_days, 30)
            self.assertTrue(sub.trial_period_end < datetime.date.today())
            self.assertTrue(sub.discount is None)
            self.assertEqual(sub.total_amount, 0)
            self.assertEqual(sub.cancelled, False)
            self.assertEqual(sub.enabled, True)


            # Test activating again
            response = self.client.post('/api/user/%i/activate_free_trial/' % self.user.id)
            self.assertEqual(response.status_code, 400)

        def test_activate_with_no_diet(self):
            response = self.client.post('/api/user/%i/activate_free_trial/' % self.user.id)
            self.assertEqual(response.status_code, 400)

        @fake_today_decorator(2012, 1, 2)
        def test_try_free_diet(self):
            """
            Test that activating a free trial on a free diet enables the "freedom" level
            """

            self._subscribe_to_diet(self.diet_free)
            response = self.client.post('/api/user/%i/activate_free_trial/' % self.user.id)
            self.assertEqual(response.status_code, 200)
            reload_object(self.user)

            self.assertEqual(Subscription.objects.count(), 1)
            sub = Subscription.objects.get()

            self.assertEqual(sub.level, 1)
            self.assertEqual(self.user.subscription_level, 1)
            self.assertEqual(sub.end_date, datetime.date(2012, 1, 9))
            self.assertEqual(sub.nb_days, 7)