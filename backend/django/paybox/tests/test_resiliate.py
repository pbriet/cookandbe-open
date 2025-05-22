
from common.mock_tools          import fake_today_decorator
from common.model               import reload_object

from emailing                   import MessageType

from paybox.models              import Transaction, Subscription
from paybox.tests               import BasePayboxTest

from mock                       import patch, Mock
import datetime
import requests
import paybox.controller

# class FakeRequestResponse(object):
#     def __init__(self, text):
#         self.text = text

# class MockPayboxPPS(object):
#     def __init__(self, return_value_dict):
#         """
#         @param return_value_dict:  {TYPE argument value: paybox response}
#         TYPE is either '00011' (transaction existence) or '00005' (cancelling transaction)
#         """
#         self.return_value_dict = return_value_dict
#         self.calls = []
#         self.call_count = 0

#     def __call__(self, *args, **kargs):

#         self.call_count += 1
#         self.calls.append((args, kargs))

#         # Retrieving "type" value in called querystring
#         type_of_call = kargs['data'].split("TYPE=")[1]
#         type_of_call = type_of_call.split('&')[0]

#         # Response corresponding to type of call
#         response = self.return_value_dict[type_of_call]

#         return Mock(status_code=200, text=response)

# def mock_gen_numquestion(user_id, additional_seconds=0):
#     return '012345678' + str(additional_seconds)

# class ResiliationTest(BasePayboxTest):

#     def setUp(self):
#         super().setUp()
#         self.subscription, dummy_transaction = self._create_dummy_transaction(Transaction.STATUS_CONFIRMED)
#         self.subscription.enabled = True
#         self.subscription.save()

#     @patch.object(paybox.controller, 'gen_pps_num_question', mock_gen_numquestion)
#     @fake_today_decorator(2012, 4, 26)
#     def _call_resiliate(self):
#         return self.client.post('/secure/api/resiliate/')

#     @patch.object(requests, 'post', MockPayboxPPS({'00011': 'CODEREPONSE=00000&NUMTRANS=2342&NUMAPPEL=322&NUMQUESTION=0123456780', '00005': 'CODEREPONSE=00000&NUMQUESTION=0123456781'}))
#     @patch.object(Subscription, 'can_be_resiliated', lambda *args: True)
#     @patch('paybox.controller.sendmail_template')
#     def test_resiliation_success(self, mock_sendmail_template):
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'ok')

#         self.assertEqual(requests.post.call_count, 2)

#         args1, kargs1 = requests.post.calls[0]
#         self.assertEqual(args1[0], 'https://ppps.paybox.com/PPPS.php')
#         # checking transaction existence, with this amount, and this reference
#         self.assertEqual(kargs1['data'],
#                 "REFERENCE=totoref&CLE=test&DATEQ=26042012000000&DEVISE=978&MONTANT=5994&NUMQUESTION=0123456780&RANG=98&SITE=1999888&TYPE=00011&VERSION=00104")

#         args2, kargs2 = requests.post.calls[1]
#         self.assertEqual(args2[0], 'https://ppps.paybox.com/PPPS.php')
#         self.assertEqual(kargs2['data'],
#                           "REFERENCE=totoref&CLE=test&DATEQ=26042012000000&DEVISE=978&MONTANT=5994" +
#                           "&NUMAPPEL=322&NUMQUESTION=0123456781&NUMTRANS=2342&RANG=98" +
#                           "&SITE=1999888&TYPE=00005&VERSION=00104")
#         self.assertEqual(mock_sendmail_template.call_count, 1)
#         args, kargs = mock_sendmail_template.call_args

#         self.assertEqual(args[0], MessageType.REALTIME)
#         self.assertEqual(args[1], 'paybox/templates/resiliation.html')
#         self.assertEqual(args[3], 'Votre abonnement a été résilié')

#         template_vars = args[2]
#         self.assertEqual(template_vars['transaction_ref'], 'totoref')

#         reload_object(self.subscription)
#         self.assertEqual(self.subscription.enabled, True)
#         self.assertEqual(self.subscription.cancelled, True)

#     @fake_today_decorator(2012, 4, 26)
#     def _assert_subscription_equal(self, subscription):
#         if subscription is not None:
#             reload_object(subscription)
#         reload_object(self.user)
#         self.assertEqual(self.user.current_subscription, subscription)

#     @patch.object(requests, 'post', MockPayboxPPS({'00011': 'CODEREPONSE=00000&NUMTRANS=2342&NUMAPPEL=322&NUMQUESTION=0123456780', '00005': 'CODEREPONSE=00000&NUMQUESTION=0123456781'}))
#     @patch('paybox.controller.sendmail_template')
#     def test_resiliation_two_enabled_subscriptions(self, mock_sendmail_template):
#         """
#         Test that resiliation disable the current subscription and re-enable the previsous one
#         """
#         self.subscription2, dummy_transaction = self._create_dummy_transaction(Transaction.STATUS_CONFIRMED, ref='totoref2', enabled=True)
#         self._assert_subscription_equal(self.subscription2)
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 200)
#         self._assert_subscription_equal(self.subscription)
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 200)
#         self._assert_subscription_equal(None)

#     def test_resiliation_no_enabled_subscriptions(self):
#         """
#         Test that resiliation fails if there is no enabled subscription for this user
#         """
#         self.subscription.enabled = False
#         self.subscription.save()

#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 400)

#     def test_resiliation_cancelled_subscriptions(self):
#         """
#         Test that resiliation fails if there is no enabled subscription for this user
#         """
#         self.subscription.cancelled = True
#         self.subscription.save()

#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 400)

#     @patch.object(Subscription, 'can_be_resiliated', lambda *args: False)
#     def test_resiliation_trial_date_passed(self):
#         """
#         Test that resiliation fails if the trial date is passed
#         """
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 400)


#     @patch.object(Subscription, 'can_be_resiliated', lambda *args: True)
#     @patch.object(requests, 'post', MockPayboxPPS({'00011': 'CODEREPONSE=00022&NUMQUESTION=0123456780'}))
#     def test_resiliation_bank_failure1(self):
#         """
#         Test that resiliation fails if the bank returned a failure status when checking existence
#         """
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'error')

#     @patch.object(Subscription, 'can_be_resiliated', lambda *args: True)
#     @patch.object(requests, 'post', MockPayboxPPS({'00011': 'CODEREPONSE=00000&NUMTRANS=2342&NUMAPPEL=322&NUMQUESTION=0123456780', '00005': 'CODEREPONSE=00002&NUMQUESTION=0123456781'}))
#     def test_resiliation_bank_failure2(self):
#         """
#         Test that resiliation fails if the bank returned a failure status when cancelling
#         """
#         response = self._call_resiliate()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.data['status'], 'error')

#     @fake_today_decorator(2014, 2, 5)
#     def test_can_be_resiliated_yes(self):
#         for y, m, d in ((2014, 2, 5), (2014, 2, 7), (2014, 3, 12), (2015, 1, 3)):
#             self.subscription.trial_period_end = datetime.date(y, m, d)
#             self.subscription.save()
#             self.assertTrue(self.subscription.can_be_resiliated())

#     @fake_today_decorator(2014, 2, 5)
#     def test_can_be_resiliated_no(self):
#         for y, m, d in ((2014, 2, 4), (2014, 1, 25), (2013, 12, 1)):
#             self.subscription.trial_period_end = datetime.date(y, m, d)
#             self.subscription.save()
#             self.assertFalse(self.subscription.can_be_resiliated())

