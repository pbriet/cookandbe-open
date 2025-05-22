
from django.conf                import settings
from common.test                import OptalimTest
from common.mock_tools          import FakeNow, fake_today_decorator

from mock                       import patch

import user_mgr.tasks
from common.mock_tools          import fake_prices_decorator

import datetime

if settings.ENABLE_PUBLIC_PAYMENT:

    class TestExpiredEmail(OptalimTest):


        @patch('user_mgr.tasks.sendmail_template')
        @fake_prices_decorator
        @fake_today_decorator(2014, 2, 5)
        def test_expired_email(self, mock_sendmail):

            self.diet       = self.create_db_diet("plop", email_title="l'alimentation miracle",
                                                  min_subscription_level=1)

            self.users = []
            for i in range(10) :
                user = self.create_db_user()
                self.users.append(user)
                user.diet = self.diet
                user.subscription_level = 1
                user.main_profile = self.create_db_profile(creator=user)
                user.save()


            # User 2 has a subscription which is active
            self.create_db_subscription(user=self.users[2], level=1, total_amount=900,
                                        end_date=datetime.date(2014, 2, 8))

            # User 3 has a subscription expired yesterday, but cancelled
            self.create_db_subscription(user=self.users[4], level=1, total_amount=0,
                                        end_date=datetime.date(2014, 2, 4), cancelled=True)

            # User 4 has a trial period expired yesterday
            self.create_db_subscription(user=self.users[4], level=1, total_amount=0,
                                        end_date=datetime.date(2014, 2, 4))

            # User 5 has a subscription expired two days ago
            self.create_db_subscription(user=self.users[5], level=1, total_amount=900,
                                        end_date=datetime.date(2014, 2, 3))

            # User 6 has a trial period expired two days ago
            self.create_db_subscription(user=self.users[6], level=1, total_amount=0,
                                        end_date=datetime.date(2014, 2, 3))

            # User 8 has a subscription expired yesterday
            self.create_db_subscription(user=self.users[8], level=1, total_amount=900,
                                        end_date=datetime.date(2014, 2, 4))

            # User 9 has an active trial period (until today included)
            self.create_db_subscription(user=self.users[9], level=1, total_amount=0,
                                        end_date=datetime.date(2014, 2, 5))

            user_mgr.tasks.expired_subscription_email()


            self.assertEqual(mock_sendmail.call_count, 2)

            args1, kargs1 = mock_sendmail.call_args_list[0]
            self.assertEqual(args1[1], 'cookandbe/templates/expired_trial.html')
            self.assertEqual(args1[2], {'diet': "l'alimentation miracle", 'subscription': 'Premium', 'best_tariff': '3'})
            self.assertEqual(args1[3], "Votre période d'essai est terminée")
            self.assertEqual(kargs1['users'][0].id, self.users[4].id)
            self.assertEqual(kargs1['tags'], ['expired_trial'])

            args2, kargs2 = mock_sendmail.call_args_list[1]
            self.assertEqual(args2[1], 'cookandbe/templates/expired_subscription.html')
            self.assertEqual(args2[2], {'diet': "l'alimentation miracle", 'subscription': 'Premium', 'best_tariff': '3'})
            self.assertEqual(args2[3], "Votre abonnement est expiré")
            self.assertEqual(kargs2['users'][0].id, self.users[8].id)
            self.assertEqual(kargs2['tags'], ['expired_subscription'])