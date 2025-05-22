
from django.conf                import settings
from django.test                import Client

from common.model               import reload_object
from common.mock_tools          import fake_today_decorator

from emailing                   import MessageType

from paybox.models              import Transaction
from paybox.tests               import BasePayboxTest

from mock                       import patch
import paybox.controller
import os
import base64
import copy
import urllib

if settings.ENABLE_PUBLIC_PAYMENT:

    TEST_FILE_PATH = os.path.abspath(os.path.dirname(__file__))
    CORRECT_QUERY_STRING = "ref=totoref&auto=something&error=00000&amount=5994&trans=222&ip=127.0.0.1"

    class BankValidationTest(BasePayboxTest):

        @patch('paybox.controller.sendmail_template')
        def _test_bank_return(self, querystring, mock_sendmail_template, ip=None, initial_status=None):
            """
            Encrypt "data_to_sign", adds it to the querystring URL, and
            calling the API from the virtual IP.

            Returns the reponse
            """
            if initial_status is None:
                initial_status = Transaction.STATUS_ACCEPTED
            if ip is None:
                ip = '194.2.122.158' # correct IP

            # Create an initial transaction, to status 'accepted'
            self.subscription, transaction = self._create_dummy_transaction(initial_status, enabled=True)

            # Simulating a client coming from a given IP
            client = Client(HTTP_X_REAL_IP=ip)

            # Calling the API
            response = client.get('/op-paybox-validation/?%s' % (querystring))

            return response, mock_sendmail_template

        def _check_transaction(self, expected_status, concluded=True, **kargs):
            """
            Check that the still unique transaction is correctly set
            """
            transaction = Transaction.objects.get()
            self.assertEqual(transaction.status, expected_status)
            self.assertEqual(transaction.concluded_at is not None, concluded)

            for param_name, param_value in kargs.items():
                self.assertEqual(getattr(transaction, param_name), param_value)

        def _assert_subscription_enabled(self, value, cancelled=False):
            reload_object(self.subscription)
            reload_object(self.user)
            if value:
                self.assertEqual(self.user.current_subscription, self.subscription)
            else:
                self.assertNotEqual(self.user.current_subscription, self.subscription)

            self.assertEqual(self.subscription.cancelled, cancelled)

        def _assert_success_email(self, mock_sendmail_template):
            # Test that a success email has been sent to the user
            self.assertEqual(mock_sendmail_template.call_count, 1)
            args, kargs = mock_sendmail_template.call_args
            self.assertEqual(len(kargs['users']), 1)
            self.assertEqual(kargs['users'][0].id, self.user.id)

            self.assertEqual(args[0], MessageType.REALTIME)
            self.assertEqual(args[1], 'paybox/templates/payment_success.html')
            self.assertEqual(args[3], 'Votre commande a bien été prise en compte')

            template_vars = args[2]
            self.assertEqual(template_vars['date'].strftime("%Y-%m-%d"), "2012-04-25")

            payment_details = template_vars['payment_details']
            self.assertEqual(payment_details['N° transaction'], '222')
            self.assertEqual(payment_details['Référence'], 'totoref')
            self.assertEqual(payment_details['Prix'], "59.94 euros")
            self.assertEqual(payment_details['Durée'], '183 jours')
            self.assertEqual(payment_details['Date de fin'],"25/10/2012" )

        def _assert_no_email(self, mock_sendmail_template):
            self.assertEqual(mock_sendmail_template.call_count, 0) # No mail

        def _assert_failure_email(self, mock_sendmail_template, error_code, transaction_status):
            self.assertEqual(mock_sendmail_template.call_count, 1)
            args, kargs = mock_sendmail_template.call_args
            self.assertEqual(len(kargs['users']), 1)
            self.assertEqual(kargs['users'][0].id, self.user.id)

            self.assertEqual(args[0], MessageType.REALTIME)
            self.assertEqual(args[1], 'paybox/templates/payment_failure.html')
            self.assertEqual(args[3], 'Votre commande a échoué')

            template_vars = args[2]
            self.assertEqual(template_vars['date'].strftime("%Y-%m-%d"), "2012-04-25")

            payment_details = template_vars['payment_details']
            self.assertEqual(payment_details['N° transaction'], '222')
            self.assertEqual(payment_details['Référence'], 'totoref')
            self.assertEqual(payment_details['Code erreur'], error_code)
            self.assertEqual(payment_details['Statut de la transaction'], transaction_status)

        @fake_today_decorator(2012, 4, 26)
        def test_paymentvalidation(self):
            """
            Test the most important : confirmation _from the bank_ that the payment is ok (or not)
            Mostly : the security checks must work
            """
            # Calling the API with valid data :
            # - signing the correct query string
            # - from an authorized IP
            response, mock_sendmail_template = self._test_bank_return(CORRECT_QUERY_STRING)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b'')

            self._check_transaction(Transaction.STATUS_CONFIRMED)
            self._assert_success_email(mock_sendmail_template)

            self._assert_subscription_enabled(True)

        @fake_today_decorator(2012, 4, 26)
        def test_invalid_ip(self):
            # Calling the API with valid data, but from an invalid IP
            response, mock_sendmail_template = self._test_bank_return(CORRECT_QUERY_STRING, ip='200.0.0.0')
            self.assertEqual(response.status_code, 400)

            self._check_transaction(Transaction.STATUS_ACCEPTED, concluded=False) # Unaffected
            self._assert_no_email(mock_sendmail_template)
            self._assert_subscription_enabled(True) # This is a wrong source of infos, don't trust him

        @fake_today_decorator(2012, 4, 26)
        def test_invalid_reference(self):
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('ref=totoref', 'ref=titiref')
            response, mock_sendmail_template = self._test_bank_return(querystring)
            self.assertEqual(response.status_code, 400)

            self._check_transaction(Transaction.STATUS_ACCEPTED, concluded=False) # Unaffected
            self._assert_no_email(mock_sendmail_template)
            self._assert_subscription_enabled(True) # This is a wrong source of infos, don't trust him

        @fake_today_decorator(2012, 4, 26)
        def test_invalid_authorization_code(self):
            # There must be a non-empty authorization code
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('auto=something', 'auto=')
            response, mock_sendmail_template = self._test_bank_return(querystring)
            self.assertEqual(response.status_code, 200)

            self._check_transaction(Transaction.STATUS_POST_CANCEL)
            self._assert_failure_email(mock_sendmail_template, 0, Transaction.STATUS_POST_CANCEL)
            self._assert_subscription_enabled(False, cancelled=True)

        @fake_today_decorator(2012, 4, 26)
        def test_invalid_authorization_code2(self):
            # There must be an authorization code
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('&auto=something', '')
            response, mock_sendmail_template = self._test_bank_return(querystring)
            self.assertEqual(response.status_code, 200)

            self._check_transaction(Transaction.STATUS_POST_CANCEL)
            self._assert_failure_email(mock_sendmail_template, 0, Transaction.STATUS_POST_CANCEL)
            self._assert_subscription_enabled(False, cancelled=True)

        @fake_today_decorator(2012, 4, 26)
        def test_unknown_error(self):
            # Error 00002 : unkonwn. Was error, and error is confirmed
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('error=00000', 'error=00002')
            response, mock_sendmail_template = self._test_bank_return(querystring, initial_status=Transaction.STATUS_ERROR)
            self.assertEqual(response.status_code, 200)

            self._check_transaction(Transaction.STATUS_ERROR)
            self._assert_failure_email(mock_sendmail_template, 2, Transaction.STATUS_ERROR)
            self._assert_subscription_enabled(False, cancelled=True)

        @fake_today_decorator(2012, 4, 26)
        def test_invalid_card_not_allowed(self):
            # Error 00021 : card not allowed. Was refused, and refusal is confirmed
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('error=00000', 'error=00021')
            response, mock_sendmail_template = self._test_bank_return(querystring, initial_status=Transaction.STATUS_REFUSED)
            self.assertEqual(response.status_code, 200)

            self._check_transaction(Transaction.STATUS_REFUSED)
            self._assert_failure_email(mock_sendmail_template, 21, Transaction.STATUS_REFUSED)
            self._assert_subscription_enabled(False, cancelled=True)

        @fake_today_decorator(2012, 4, 26)
        def test_unexpected_amount(self):
            # Amount is not the same as in the transaction
            querystring = copy.copy(CORRECT_QUERY_STRING)
            querystring = querystring.replace('amount=5994', 'amount=5992')
            response, mock_sendmail_template = self._test_bank_return(querystring, initial_status=Transaction.STATUS_ERROR)
            self.assertEqual(response.status_code, 200)

            self._check_transaction(Transaction.STATUS_WRONG_AMOUNT, price=5992)
            self._assert_failure_email(mock_sendmail_template, 0, Transaction.STATUS_WRONG_AMOUNT)
            self._assert_subscription_enabled(False, cancelled=True)


