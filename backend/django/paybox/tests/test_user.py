
from django.conf                import settings

from common.mock_tools          import fake_prices_decorator
from paybox.tests               import BasePayboxTest

from paybox.models              import Transaction
import paybox.views
from mock                       import patch
import datetime

if settings.ENABLE_PUBLIC_PAYMENT:

    class PaymentTest(BasePayboxTest):

        @fake_prices_decorator
        @patch.object(paybox.views.timezone, 'now', lambda: datetime.datetime(2014, 10, 3, 15, 4, 3))
        @patch.object(paybox.views, 'APP_BASE_URL', 'https://www.plop.com')
        @patch.object(paybox.views, 'SOURCE_FILE_PATH', '/somewhere')
        @patch.object(paybox.views, 'PBX_URL', 'https://preprod-tpeweb.e-transactions.fr/php/')
        def test_paying(self):
            """
            Test that pressing on the "buy" button calls the CGI script with the correct data
            """
            response = self.client.get('/payment/pay/', {'subscription_level': 1, 'nb_months': 3, 'user_id': self.user.pk}, HTTP_X_REAL_IP='133.22.11.1')
            self.assertEqual(response.status_code, 302)

            redirect_url = response.headers['location']
            redirect_url = redirect_url.split("&PBX_HMAC")[0] # Removing random part

            expected_ref = "premium_3_20141003150403_%#06d" % self.user.id

            print(redirect_url)

            self.assertEqual(redirect_url,
                "https://preprod-tpeweb.e-transactions.fr/php/" +
                "?PBX_ANNULE=https%3A%2F%2Fwww.plop.com%2Fpayment%2Fcancelled%2F" +
                "&PBX_CMD=%s" % expected_ref +
                "&PBX_DEVISE=978" +
                "&PBX_EFFECTUE=https%3A%2F%2Fwww.plop.com%2Fpayment%2Faccepted%2F" +
                "&PBX_IDENTIFIANT=668355985" +
                "&PBX_LANGUE=FRA" +
                "&PBX_PORTEUR=test%40test.fr" +
                "&PBX_RANG=01&PBX_REFUSE=https%3A%2F%2Fwww.plop.com%2Fpayment%2Frefused%2F" +
                "&PBX_REPONDRE_A=https%3A%2F%2Fwww.plop.com%2Fop-paybox-validation%2F" +
                "&PBX_RETOUR=amount%3AM%3Bref%3AR%3Bauto%3AA%3Btrans%3AT%3Bpayment%3AP%3Bcard%3AC%3Bidtrans%3AS%3Bcountry%3AY%3Berror%3AE%3Bvalidity%3AD%3Bip%3AI%3BBIN6%3AN%3Bdigest%3AH%3Bsign%3AK" +
                "&PBX_SITE=1585024" +
                "&PBX_TOTAL=1200")

            self.assertEqual(Transaction.objects.count(), 1)
            transaction = Transaction.objects.get()
            self.assertEqual(transaction.status, Transaction.STATUS_STARTED)
            self.assertEqual(transaction.ip, '133.22.11.1')
            self.assertEqual(transaction.price, 1200)
            self.assertEqual(transaction.ref, expected_ref)


        @patch.object(paybox.views, 'APP_BASE_URL', 'https://www.plop.com')
        @fake_prices_decorator
        def _test_payment_return(self, url, expected_redirection, create_transaction=True,
                                 expected_transaction_status=None, check_transaction_after=True):
            if create_transaction:
                self.subscription, dummy_transaction = self._create_dummy_transaction(Transaction.STATUS_STARTED)

            get_args = {'ref': 'totoref', 'trans': '9035433', 'subscription': '9632144', 'payment': 'CB',
                        'amount': 999, 'ip': '127.0.0.1'}
            response = self.client.get(url, get_args)
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers['location'], expected_redirection)
            ## Django 1.7
            #self.assertRedirects(response, expected_redirection, fetch_redirect_response=False)

            if check_transaction_after:
                transaction = Transaction.objects.get()
                self.assertEqual(transaction.transaction_id, 9035433)
                self.assertEqual(transaction.payment_type, 'CB')
                self.assertEqual(transaction.ip, '127.0.0.1')
                self.assertEqual(transaction.price, 999)
                if expected_transaction_status is not None:
                    self.assertEqual(transaction.status, expected_transaction_status)


        def test_success(self):
            self._test_payment_return('/payment/accepted/', 'https://www.plop.com/payment_status/accepted',
                                      expected_transaction_status=Transaction.STATUS_ACCEPTED)

        def test_refused(self):
            self._test_payment_return('/payment/refused/', 'https://www.plop.com/payment_status/refused',
                                      expected_transaction_status=Transaction.STATUS_REFUSED)

        def test_cancelled(self):
            self._test_payment_return('/payment/cancelled/', 'https://www.plop.com/payment_status/cancelled',
                                      expected_transaction_status=Transaction.STATUS_CANCELLED)

        def test_error(self):
            self._test_payment_return('/payment/error/', 'https://www.plop.com/payment_status/error',
                                      expected_transaction_status=Transaction.STATUS_ERROR)

        def test_with_no_transaction(self):
            """
            Test the erroneous case when there is no transaction initiated when payment is accepted/refused/any
            """
            # Not transaction in the DB
            for status in ('accepted', 'refused', 'cancelled', 'error'):
                self._test_payment_return("/payment/%s/" % status, 'https://www.plop.com/critical_error',
                                          create_transaction=False, check_transaction_after=False)

