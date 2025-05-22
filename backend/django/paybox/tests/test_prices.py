from common.test        import TestAPIWithLogin

from django.conf                import settings
from paybox.prices      import get_prices_and_discount
from common.mock_tools  import fake_prices_decorator, fake_today_decorator
import paybox.controller

from mock               import patch

import datetime

if settings.ENABLE_PUBLIC_PAYMENT:

    DEFAULT_EXPECTED_TARIFFS = {
        1: {1: {'discount': 0, 'monthly_cost': 5.0, 'after_discount': 5.0},
            3: {'discount': 0, 'monthly_cost': 4.0, 'after_discount': 4.0},
            12: {'discount': 0, 'monthly_cost': 3.0, 'after_discount': 3.0}}
     }

    class BaseTestPrices(TestAPIWithLogin):

        @fake_prices_decorator
        def _assert_no_discount(self):
            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)

            self.assertEqual(res.data, DEFAULT_EXPECTED_TARIFFS)


    class TestPrices(BaseTestPrices):

        def test_api_tariff(self):
            self._assert_no_discount()

        @fake_prices_decorator
        @fake_today_decorator(2015, 2, 4)
        def test_api_tariff_discount(self):

            self.create_db_global_special_offer(datetime.datetime(2015, 2, 3), datetime.datetime(2015, 2, 6), 50)

            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)

            expected = {1: {1: {'discount': 50, 'monthly_cost': 5.0, 'after_discount': 2.5},
                            3: {'discount': 50, 'monthly_cost': 4.0, 'after_discount': 2.0},
                            12: {'discount': 50, 'monthly_cost': 3.0, 'after_discount': 1.5}}}

            self.assertEqual(res.data, expected)

            # Adding a better discount
            self.create_db_global_special_offer(datetime.datetime(2015, 2, 3), datetime.datetime(2015, 2, 8), 80)
            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)
            for level, level_values in res.data.items():
                for nb_month, month_values in level_values.items():
                    self.assertEqual(month_values['discount'], 80)

        @fake_prices_decorator
        @fake_today_decorator(2015, 2, 4)
        def test_api_tariff_no_discount(self):

            # Offer is expired
            self.create_db_global_special_offer(datetime.datetime(2015, 1, 3), datetime.datetime(2015, 1, 6), 50)

            # Offer starts later
            self.create_db_global_special_offer(datetime.datetime(2015, 2, 5), datetime.datetime(2015, 2, 8), 50)

            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)

            self.assertEqual(res.data, DEFAULT_EXPECTED_TARIFFS)

        @fake_prices_decorator
        @fake_today_decorator(2015, 2, 4)
        def test_api_tariff_discount_on_level(self):

            # Discount applied on level 2 only
            self.create_db_global_special_offer(datetime.datetime(2015, 2, 3), datetime.datetime(2015, 2, 6), 50,
                                                level=2)

            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)

            expected = {1: {1: {'discount': 0, 'monthly_cost': 5.0, 'after_discount': 5.0},
                            3: {'discount': 0, 'monthly_cost': 4.0, 'after_discount': 4.0},
                            12: {'discount': 0, 'monthly_cost': 3.0, 'after_discount': 3.0}}}

            self.assertEqual(res.data, expected)

    class TestUserSpecialOffer(BaseTestPrices):

        def setUp(self):
            super().setUp()
            self.user2 = self.create_db_user()

        @fake_prices_decorator
        def _assert_50_discount(self):

            res = self.client.get('/api/tariffs/')
            self.assertEqual(res.status_code, 200)

            expected = {1: {1: {'discount': 50,  'monthly_cost': 5.0, 'after_discount': 2.5},
                            3: {'discount': 50,  'monthly_cost': 4.0, 'after_discount': 2.0},
                            12: {'discount': 50, 'monthly_cost': 3.0, 'after_discount': 1.5}}}


            self.assertEqual(res.data, expected)


        def test_with_two_users(self):
            """
            Test with 2 users having different discounts. Check the values are correct.
            """
            # -50% for main user
            self.create_db_user_special_offer(50, user=self.user)
            # -75% for other user
            self.create_db_user_special_offer(50, user=self.user2)

            self._assert_50_discount()

        def test_with_expired_offer(self):
            self.create_db_user_special_offer(50, user=self.user, until=datetime.datetime(2014, 2, 3))

            self._assert_no_discount()


        def test_with_two_offers(self):
            self.create_db_user_special_offer(50, user=self.user)
            self.create_db_user_special_offer(25, user=self.user)
            self._assert_50_discount()