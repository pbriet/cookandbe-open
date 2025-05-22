
from common.mock_tools          import fake_mongo_decorator, fake_today_decorator
from common.model               import reload_object

from common.test                import TestAPIWithLogin

import datetime

class TestEmailOptions(TestAPIWithLogin):

    @fake_today_decorator(2012, 4, 5)
    @fake_mongo_decorator
    def test_email_options(self, mock_mongo):
        response = self.client.get('/api/user/%i/email_options' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"enabled": True,
                                         "notifications": True,
                                         "daily": True,
                                         "suggestion": True,
                                         "newsletter": True})

        response = self.client.post('/api/user/%i/set_email_options' % self.user.id, {"enabled": True, "notifications": False, "newsletter": False})
        self.assertEqual(response.status_code, 201)

        reload_object(self.user)

        self.assertTrue(self.user.enabled)
        self.assertFalse(self.user.mail_notifications)
        self.assertFalse(self.user.mail_newsletter)

        response = self.client.get('/api/user/%i/email_options' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"enabled": True,
                                         "daily": True,
                                         "suggestion": True,
                                         "notifications": False,
                                         "newsletter": False})

        response = self.client.post('/api/user/%i/set_email_options' % self.user.id,
                                    {"enabled": False,
                                     "why_leaving_us": "because !",})
        self.assertEqual(response.status_code, 201)

        response = self.client.get('/api/user/%i/email_options' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"enabled": False,
                                         "daily": True,
                                         "suggestion": True,
                                         "notifications": False,
                                         "newsletter": False})

        why_leaving_data = mock_mongo['why_leaving_us'].written_data
        self.assertEqual(len(why_leaving_data), 1)
        self.assertEqual(why_leaving_data[0]['user_id'], str(self.user.id))
        self.assertEqual(why_leaving_data[0]['text'], "because !")
        self.assertEqual(why_leaving_data[0]['created_at'].strftime("%Y-%m-%d"), "2012-04-05")