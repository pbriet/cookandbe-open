from django.conf import settings
from django.test import override_settings

from common.test            import OptalimTest
from common.date            import tz_aware
from mock                   import patch
from emailing.tasks         import send_email
from emailing.tools         import sendmail_template, MessageType
import emailing.tasks
import emailing.tools
import datetime

EXPECTED_MESSAGE = {'auto_text': True,
             'bcc_address': 'cc@localhost',
             'from_email': 'noreply@localhost',
             'from_name': settings.APP_BRAND_NAME.replace('&', ' and '),
             'headers': {'Reply-To': 'noreply@localhost'},
             'html': "<b>This is my template with plop inside !</b>\n",
             'important': False,
             'inline_css': True,
             'preserve_recipients': False,
             'subject': "message title",
             'tags': ["plip", "tag_to_track"],
             'to': [{'email': "the_customer@somewhere.com",
                     'name': "the_customer@somewhere.com",
                     'type': 'to'}],
             'track_clicks': True,
             'track_opens': True
            }

class FakePreMailer(object):
    def __init__(self, message, **args):
        self.message = message

    def transform(self, *args, **kargs):
        return self.message

class TestSendEmail(OptalimTest):

    @override_settings(ENABLE_AUTO_BCC=True)
    @patch('emailing.tools.send_email')
    @patch.object(emailing.tools.premailer, 'Premailer', FakePreMailer)
    def test_sendmail_template_sync(self, mock_send_email):
        sendmail_template(MessageType.REALTIME, 'emailing/fixtures/test_email_template.html', {'toto': 'plop'},
                          "message title", email="the_customer@somewhere.com",
                          tags=["plip", "tag_to_track"], no_personal_infos=True)

        mock_send_email.assert_called_once_with(EXPECTED_MESSAGE)

        self.assertTrue(True)

    @override_settings(ENABLE_AUTO_BCC=True)
    @patch('emailing.tools.send_email.apply_async')
    @patch.object(emailing.tools.premailer, 'Premailer', FakePreMailer)
    def test_sendmail_template_async(self, mock_send_email):
        sendmail_template(MessageType.REALTIME, 'emailing/fixtures/test_email_template.html', {'toto': 'plop'},
                          "message title", email="the_customer@somewhere.com",
                          tags=["plip", "tag_to_track"], send_async=True, no_personal_infos=True)

        args, kwargs = mock_send_email.call_args
        print(kwargs)
        self.assertEqual(kwargs,
                         {'args': [EXPECTED_MESSAGE],
                          'eta': None,
                          'expires': 60*60})

        self.assertTrue(True)

    @override_settings(ENABLE_AUTO_BCC=True)
    @patch('emailing.tools.send_email.apply_async')
    @patch.object(emailing.tools.premailer, 'Premailer', FakePreMailer)
    def test_sendmail_template_async_eta(self, mock_send_email):
        eta = tz_aware(datetime.datetime(2011, 4, 3, 17, 46, 00))
        sendmail_template(MessageType.REALTIME, 'emailing/fixtures/test_email_template.html', {'toto': 'plop'},
                          "message title", email="the_customer@somewhere.com",
                          tags=["plip", "tag_to_track"], send_async=True,
                          eta=eta, no_personal_infos=True)

        args, kwargs = mock_send_email.call_args
        self.assertEqual(kwargs,
                         {'args': [EXPECTED_MESSAGE],
                          'eta': eta,
                          'expires': tz_aware(datetime.datetime(2011, 4, 3, 18, 46, 00))})

        self.assertTrue(True)

class BaseTestSendMail(OptalimTest):
    def setUp(self):
        super().setUp()
        self.my_user = self.create_db_user()

    @patch('emailing.tools.send_email')
    def _test_send(self, message_type, should_be_called, mock_send):
        sendmail_template(message_type, 'emailing/fixtures/test_email_template.html', {}, "plip", users=[self.my_user],
                                         no_personal_infos=True)
        self.assertEqual(mock_send.called, should_be_called)

class TestSendEmailDisabledAccount(BaseTestSendMail):
    def setUp(self):
        super().setUp()
        self.my_user.enabled = False
        self.my_user.save()

    def test_no_send_newsletter_or_notification(self):
        for m_type in (MessageType.NEWSLETTER, MessageType.NOTIFICATION, MessageType.MAIN_INFO):
            self._test_send(m_type, False)

    def test_send_realtime_email(self):
        self._test_send(MessageType.REALTIME, True)

class TestSendEmailUnsubscribe(BaseTestSendMail):
    def test_send_success(self):
        for m_type in (MessageType.NEWSLETTER, MessageType.NOTIFICATION, MessageType.MAIN_INFO, MessageType.REALTIME):
            self._test_send(m_type, True)

    def test_send_fail_with_notifications_disabled(self):
        self.my_user.mail_notifications = False
        self.my_user.save()
        self._test_send(MessageType.NOTIFICATION, False)
        for m_type in (MessageType.NEWSLETTER, MessageType.MAIN_INFO, MessageType.REALTIME):
            self._test_send(m_type, True)

    def test_send_fail_with_newsletter_disabled(self):
        self.my_user.mail_newsletter = False
        self.my_user.save()
        self._test_send(MessageType.NEWSLETTER, False)
        for m_type in (MessageType.NOTIFICATION, MessageType.MAIN_INFO, MessageType.REALTIME):
            self._test_send(m_type, True)



class TestUserEmailParams(OptalimTest):
    """
    Automatic data displayed in the email left column
    """
    def setUp(self):
        super().setUp()
        self.my_user = self.create_db_user(name="toto")
        self.other_user = self.create_db_user()
        self.create_db_profile(creator=self.my_user, height=150, weight=70)

        for i in range(10):
            if i > 2 :
                user = self.my_user
            else:
                user = self.other_user
            internal = i%2 == 1
            self.create_db_recipe(author=user, internal=internal)


    @patch.object(emailing.tools.premailer, 'Premailer', FakePreMailer)
    @patch('emailing.tools.send_email')
    def test_user_email_params_send(self, mock_send):
        message_type = MessageType.MAIN_INFO
        sendmail_template(message_type, 'emailing/fixtures/user_data.html', {}, "plip", users=[self.my_user])
        expected_message = "NB_RECIPES=3;USERNAME=toto;OBJECTIVE=Classique;IMC_VALUE=31,1;IMC_NAME=surpoids"

        args, kwargs = mock_send.call_args
        kargs = args[0]
        self.assertEqual(kargs['html'], expected_message)



class TestEmailMode(OptalimTest):
    """
    Test the EMAIL_MODE setting
    """

    MESSAGE = {
            'bcc_address': 'cc@cookandbe.com',
            'html': '<header>Plop</header><body>Hi there !</body>',
            'subject': 'a new mail for you',
            'to': [{'email': 'toto@titi.fr', 'name': 'Mr Toto', 'type': 'to'}],
            'track_clicks': True,
            'track_opens': True
        }

    @patch.object(emailing.tasks, 'TESTING', False)
    def _send_message(self):
        # Be careful to mock really_send_sendgrid_email !
        send_email(self.MESSAGE)

    @patch.object(emailing.tasks, 'EMAIL_MODE', 'send')
    @patch('emailing.tasks.really_send_sendgrid_email')
    @patch('emailing.tasks.log_email')
    def test_user_email_params_send(self, mock_log_email, mock_send_sendgrid):
        self._send_message()
        self.assertEqual(mock_log_email.call_count, 0)
        self.assertEqual(mock_send_sendgrid.call_count, 1)

        args, kwargs = mock_send_sendgrid.call_args

        self.assertEqual(args[0], self.MESSAGE)


    @patch.object(emailing.tasks, 'EMAIL_MODE', 'log')
    @patch('emailing.tasks.really_send_sendgrid_email')
    @patch('emailing.tasks.log_email')
    def test_user_email_params_log(self, mock_log_email, mock_send_sendgrid):
        self._send_message()
        self.assertEqual(mock_log_email.call_count, 1)
        self.assertEqual(mock_send_sendgrid.call_count, 0)

        args, kwargs = mock_log_email.call_args

        self.assertEqual(args[0], self.MESSAGE)


    @patch.object(emailing.tasks, 'EMAIL_MODE', 'send_to_staging')
    @patch('emailing.tasks.really_send_sendgrid_email')
    @patch('emailing.tasks.log_email')
    def test_user_email_params_log(self, mock_log_email, mock_send_sendgrid):
        self._send_message()
        self.assertEqual(mock_log_email.call_count, 0)
        self.assertEqual(mock_send_sendgrid.call_count, 1)

        args, kwargs = mock_send_sendgrid.call_args

        EXPECTED_MESSAGE = {
            'html': '<header>Plop</header><body><b>SENT TO : toto@titi.fr</b><br/><br/><br/>Hi there !</body>',
            'subject': '[STAGING] a new mail for you',
            'to': [{'email': 'preprod@cookandbe.com', 'name': 'Staging', 'type': 'to'}],
            'track_clicks': False,
            'track_opens': False
        }

        self.assertEqual(args[0], self.MESSAGE)
