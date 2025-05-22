
from common.test            import TestAPIWithLogin, add_permissions
from common.model           import reload_object
from common.mock_tools      import fake_today_decorator, fake_django_login

from django.conf            import settings
from user_mgr.auth          import update_user_subscription_level
from user_mgr.models        import User

import datetime

if settings.ENABLE_PUBLIC_PAYMENT:

    class TestAdminSubscription(TestAPIWithLogin):
        @fake_today_decorator(2012, 1, 2)
        def setUp(self):
            super().setUp()
            self.check_user_subscription(level = 0)

        @fake_django_login
        def check_user_subscription(self, level):
            update_user_subscription_level(self.user)
            self.assertEqual(self.user.subscription_level, level)
            if level == 0:
                self.assertEqual(self.user.current_subscription, None)
            else:
                self.assertNotEqual(self.user.current_subscription, None)

        def get_default_kargs(self, **kargs):
            defaults = {
                'start_date': "2012-01-01",
                'trial_period_end': "2012-01-06",
                'end_date': "2012-02-01",
                'enabled': True,
                'cancelled': False,
                'discount': 0,
                'level': 1,
                'nb_months': 1,
                'nb_days': 0,
                'total_amount': 42,
                'user': self.user.id,
            }
            defaults.update(**kargs)
            return defaults

        def test_user_create_subscription_forbidden(self):
            res = self.client.post('/secure/api/subscription', self.get_default_kargs())
            self.assertEqual(res.status_code, 403)

        @fake_today_decorator(2012, 1, 2)
        @add_permissions("admin")
        def test_admin_create_subscription(self):
            res = self.client.post('/secure/api/subscription', self.get_default_kargs())
            self.assertEqual(res.status_code, 201)
            self.check_user_subscription(level = 1)

        # @fake_today_decorator(2012, 1, 2)
        # @add_permissions("admin")
        # def test_admin_create_multiple_subscriptions(self):
        #     res = self.client.post('/secure/api/subscription', self.get_default_kargs(level = 0))
        #     self.assertEqual(res.status_code, 201)
        #     self.check_user_subscription(level = 1)
        #     res = self.client.post('/secure/api/subscription', self.get_default_kargs(level = 2))
        #     self.assertEqual(res.status_code, 201)
        #     self.check_user_subscription(level = 2)

        def test_user_update_subscription_forbidden(self):
            subscription = self.create_db_subscription(level = 1, enabled = True)
            res = self.client.put('/secure/api/subscription/%i' % (subscription.id), self.get_default_kargs(id = subscription.id))
            self.assertEqual(res.status_code, 403)

        @fake_today_decorator(2012, 1, 2)
        @add_permissions("admin")
        def test_admin_update_subscriptions(self):
            res = self.client.post('/secure/api/subscription', self.get_default_kargs(level = 1))
            self.assertEqual(res.status_code, 201)
            self.check_user_subscription(level = 1)
            subscription = self.user.current_subscription
            changes = {
                'start_date': "2011-12-31",
                'end_date': "2012-02-10",
                'trial_period_end': "2012-01-10",
                'cancelled': True,
            }
            for key, ref in changes.items():
                kargs = {"id": subscription.id, key: ref}
                res = self.client.put('/secure/api/subscription/%i' % (subscription.id), self.get_default_kargs(**kargs))
                self.assertEqual(res.status_code, 200)
                reload_object(subscription)
                value = subscription.__dict__[key]
                if type(value) is datetime.date:
                    value = value.strftime("%Y-%m-%d")
                self.assertEqual(value, ref)

        @fake_today_decorator(2012, 1, 2)
        @add_permissions("admin")
        def test_admin_update_subscriptions_forbidden(self):
            res = self.client.post('/secure/api/subscription', self.get_default_kargs(level = 1))
            self.assertEqual(res.status_code, 201)
            self.check_user_subscription(level = 1)
            user2 = self.create_db_user()
            subscription = self.user.current_subscription
            changes = {
                'enabled': not subscription.enabled,
                'level': 2,
                'discount': subscription.discount + 3,
                'nb_months': subscription.nb_months + 1,
                'total_amount': subscription.total_amount + 1,
                'user_id': user2.id,
            }
            for key, ref in changes.items():
                kargs = {"id": subscription.id, key: ref}
                res = self.client.put('/secure/api/subscription/%i' % (subscription.id), self.get_default_kargs(**kargs))
                self.assertEqual(res.status_code, 403)
                reload_object(subscription)
                value = subscription.__dict__[key]
                if type(value) is datetime.date:
                    value = value.strftime("%Y-%m-%d")
                self.assertNotEqual(value, ref)

        def test_user_destroy_subscription_forbidden(self):
            subscription = self.create_db_subscription(level = 1, enabled = True)
            res = self.client.delete('/secure/api/subscription/%i' % (subscription.id))
            self.assertEqual(res.status_code, 403)

        @fake_today_decorator(2012, 1, 2)
        @add_permissions("admin")
        def test_admin_destroy_subscriptions_forbidden(self):
            subscription = self.create_db_subscription(level = 1, enabled = True)
            res = self.client.delete('/secure/api/subscription/%i' % (subscription.id))
            self.assertEqual(res.status_code, 403)
