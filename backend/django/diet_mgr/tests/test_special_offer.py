
from common.test                import OptalimTest
from common.mock_tools          import fake_today_decorator

from django.utils               import timezone

from mock                       import patch

from diet_mgr.models            import Diet

from paybox.models              import UserSpecialOffer

import diet_mgr.tasks

class TestSpecialOfferTask(OptalimTest):

    def setUp(self):
        super().setUp()

        # Balanced diet exists by default
        # Adding "slim" and "easy_digest"
        self.create_db_diet("slim", title="Perdre du poids",
                            description="blah", min_subscription_level=1)
        self.create_db_diet("easy_digest", title="Faciliter la digestion",
                            description="blih", min_subscription_level=1)

        # User who joined 1 days ago
        self.user1 = self.create_db_user(subscription_level=0,
                                         date_joined=timezone.datetime(2014, 2, 19))
        self.set_diet_subscription(self.user1, 'slim')

        # User who joined 10 days ago
        self.user2 = self.create_db_user(subscription_level=0,
                                            date_joined=timezone.datetime(2014, 2, 10))
        self.set_diet_subscription(self.user2, 'slim')

        ### Users who joined 2 days ago

        # With a balanced diet, very happy with it !
        self.user3 = self.create_db_user(subscription_level=0,
                                         date_joined=timezone.datetime(2014, 2, 18))
        self.set_diet_subscription(self.user3, 'balanced')

        # With a slim diet, and a premium subscription
        self.user4 = self.create_db_user(subscription_level=1,
                                         date_joined=timezone.datetime(2014, 2, 18))
        self.set_diet_subscription(self.user4, 'slim')

        # With a slim diet and no subscription
        self.user5 = self.create_db_user(subscription_level=0,
                                         date_joined=timezone.datetime(2014, 2, 18))
        self.set_diet_subscription(self.user5, 'slim')

        # With a easy_digest diet and no subscription
        self.user6 = self.create_db_user(subscription_level=0,
                                         date_joined=timezone.datetime(2014, 2, 18))
        self.set_diet_subscription(self.user6, 'easy_digest')


    def set_diet_subscription(self, user, diet_key):
        user.diet = Diet.objects.get(key=diet_key)
        user.save()


    @patch('diet_mgr.tasks.sendmail_template')
    @fake_today_decorator(2014, 2, 20)
    def test_special_offer(self, mock_sendmail):
        """
        Special offer should be sent to user5 and user6
        """
        diet_mgr.tasks.auto_diet_special_offer()

        self.assertEqual(mock_sendmail.call_count, 2)

        args1, kargs1 = mock_sendmail.call_args_list[0]
        self.assertEqual(args1[2]['diet'].title, "Perdre du poids")
        self.assertEqual(args1[2]['subscription_name'], "Premium")
        self.assertEqual(args1[2]['best_tariff'], "5")
        self.assertEqual(len(kargs1['users']), 1)
        self.assertEqual(kargs1['users'][0].id, self.user5.id)

        args2, kargs2 = mock_sendmail.call_args_list[1]
        self.assertEqual(args2[2]['diet'].title, "Faciliter la digestion")
        self.assertEqual(args2[2]['subscription_name'], "Premium")
        self.assertEqual(args2[2]['best_tariff'], "5")
        self.assertEqual(len(kargs2['users']), 1)
        self.assertEqual(kargs2['users'][0].id, self.user6.id)

        offers = list(UserSpecialOffer.objects.all().order_by('user__pk'))
        self.assertEqual(len(offers), 2)
        offer1, offer2 = offers
        self.assertEqual(offer1.user_id, self.user5.id)
        self.assertEqual(offer1.discount, 50)
        self.assertEqual(offer1.until.strftime("%Y-%m-%d"), "2014-02-22")

        self.assertEqual(offer2.user_id, self.user6.id)
        self.assertEqual(offer2.discount, 50)
        self.assertEqual(offer2.until.strftime("%Y-%m-%d"), "2014-02-22")