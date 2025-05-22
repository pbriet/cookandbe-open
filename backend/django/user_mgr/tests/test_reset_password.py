
from django.contrib.auth        import logout

from common.test                import OptalimTest

from user_mgr.models            import UserOperation
from user_mgr.controller        import get_reset_code
from user_mgr.views             import RESET_PASSWORD_OPERATION

from rest_framework.test            import APIClient

import datetime
import json

class TestResetPassword(OptalimTest):
    def setUp(self):
        super().setUp()
        self.client = APIClient()

    def test_code(self):
        self.assertFalse(self.is_authenticated())
        # Bad user
        response = self.client.post('/api/forgot_password/', json.dumps({"usermail" : "x@y.z",
                                                                         'app': "public"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "error")
        # Création de la demande de reset (pas de passage par l'API car envoie un email...)
        good_key = "424242"
        bad_key  = "123456"
        reset    = UserOperation.objects.create(user = self.user, key = good_key, ip = "127.0.0.1", operation = RESET_PASSWORD_OPERATION)
        values   = (
            ({"usermail" : "x@y.z"},    "error"),   # Bad user
            ({"usermail" : self.LOGIN}, "error"),   # Missing code
            ({"usermail" : self.LOGIN, "code" : bad_key},  "error"),    # Bad code
            ({"usermail" : self.LOGIN, "code" : good_key}, "error"),    # No password
            ({"usermail" : self.LOGIN, "code" : good_key, "password" : "toto"},        "error"),    # Invalid password
            ({"usermail" : self.LOGIN, "code" : good_key, "password" : self.PASSWORD}, "ok"),       # All good
            ({"usermail" : self.LOGIN, "code" : good_key, "password" : self.PASSWORD}, "error")     # Already logged
        )
        for kargs, status in values:
            kargs["app"] = "public"
            response = self.client.post('/api/reset_password/', json.dumps(kargs), content_type = "application/json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], status)
        # Already used
        response = self.api_logout()
        response = self.client.post('/api/reset_password/', json.dumps({"app": "public", "usermail" : self.LOGIN,
                                                                        "code" : good_key, "password" : self.PASSWORD}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "error")
        # Expired
        reset.used = False
        reset.date -= datetime.timedelta(0, 60 * 60 + 1)
        reset.save()
        response = self.client.post('/api/reset_password/', json.dumps({"app": "public", "usermail" : self.LOGIN,
                                                                        "code" : good_key, "password" : self.PASSWORD}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "error")

    def test_reset_password(self):
        ANOTHER_PASSWORD = "tonthétatilotetatoue"
        self.assertFalse(self.is_authenticated())
        self.assertFalse(self.user.check_password(ANOTHER_PASSWORD))
        good_key = "424242"
        reset    = UserOperation.objects.create(user = self.user, key = good_key, ip = "127.0.0.1", operation = RESET_PASSWORD_OPERATION)
        response = self.client.post('/api/reset_password/',
                                    json.dumps({"usermail" : self.LOGIN,
                                                "app": "public",
                                                "code" : good_key,
                                                "password" : ANOTHER_PASSWORD}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")
        self.reload_user()
        self.assertTrue(self.user.check_password(ANOTHER_PASSWORD))
        print(response.data)
