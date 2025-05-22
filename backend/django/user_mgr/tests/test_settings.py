from common.test                import TestAPIWithLogin
from common.date                import tz_aware
from user_mgr.models            import User
from profile_mgr.models         import Profile
from eater_mgr.models           import Eater
from planning_mgr.models        import MetaPlanning
from mock                       import patch
import planning_mgr.controller
import user_mgr.controller
import datetime
import json

class TestSignupAPI(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.settings_data = {'first_name': 'Pascal',
                  'last_name': 'Briet',
                  'password': 'toto',
                  'sex': 'male',
                  'birth_date': datetime.date(1985, 1, 13).strftime("%Y-%m-%d")}
        self.password_data = {'old_password': 'toto', 'new_password': 'toto42'}

    def test_successful_settings(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertNotEqual(self.user.first_name, self.settings_data['first_name'])
        self.assertNotEqual(self.user.last_name, self.settings_data['last_name'])
        # New settings
        response = self.client.put('/api/user/%i/change_settings/' % self.user.id,
                                    json.dumps(self.settings_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        # Update with last db infos
        self.reload_user()
        # Checks
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.first_name, self.settings_data['first_name'])
        self.assertEqual(self.user.last_name, self.settings_data['last_name'])

    def test_successful_login(self):
        new_mail = 'kaloo1@free.fr'
        self.assertNotEqual(self.user.email, new_mail)
        # New login (email)
        response = self.client.put('/api/user/%i/change_login/' % self.user.id,
                                    json.dumps({"email" : new_mail}),
                                    content_type="application/json")
        # Update with last db infos
        self.reload_user()
        # Checks
        self.assertEqual(self.user.email, new_mail)

    def test_successful_password(self):
        # Setting old password
        self.user.set_password(self.password_data['old_password'])
        self.user.save()
        # Re-login
        self.api_login(password=self.password_data['old_password'])

        # Checking current password
        self.assertFalse(self.user.check_password(self.password_data['new_password']))
        print(self.is_authenticated())
        # New password
        response = self.client.put('/api/user/%i/change_password/' % self.user.id,
                                    json.dumps(self.password_data),
                                    content_type="application/json")
        print(response.data)
        self.assertEqual(response.status_code, 201)
        # Update with last db infos
        self.reload_user()
        # Checks
        self.assertTrue(self.user.check_password(self.password_data['new_password']))

    def test_missing_field(self):
        response = self.client.put('/api/user/%i/change_settings/' % self.user.id,
                                    json.dumps({}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Information manquante")
        
    def test_empty_field(self):
        self.settings_data["first_name"] = ""
        response = self.client.put('/api/user/%i/change_settings/' % self.user.id,
                                    json.dumps(self.settings_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Information manquante")

    def test_invalid_email(self):
        new_mail = "blih@bluh"
        response = self.client.put('/api/user/%i/change_login/' % self.user.id,
                                    json.dumps({ "email" : new_mail}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Adresse e-mail invalide")

    def test_duplicate_email(self):
        new_mail = 'kaloo1@free.fr'
        User.objects.create_user(new_mail, 'toto')
        response = self.client.put('/api/user/%i/change_login/' % self.user.id,
                                    json.dumps({"email" : new_mail }),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Compte existant")

    def test_wrong_old_password(self):
        self.assertFalse(self.user.check_password(self.password_data['old_password']))
        response = self.client.put('/api/user/%i/change_password/' % self.user.id,
                                    json.dumps(self.password_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Changement de mot de passe impossible")

    def test_missing_new_password(self):
        # Setting old password
        self.user.set_password(self.password_data['old_password'])
        self.user.save()
        # Re-login
        self.api_login(password=self.password_data['old_password'])
        self.assertTrue(self.user.check_password(self.password_data['old_password']))
        # Empty new
        del self.password_data['new_password']
        response = self.client.put('/api/user/%i/change_password/' % self.user.id,
                                    json.dumps(self.password_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Changement de mot de passe impossible")

    def test_empty_new_password(self):
        # Setting old password
        self.user.set_password(self.password_data['old_password'])
        self.user.save()
        # Re-login
        self.api_login(password=self.password_data['old_password'])
        self.assertTrue(self.user.check_password(self.password_data['old_password']))
        # Empty new
        del self.password_data['new_password']
        response = self.client.put('/api/user/%i/change_password/' % self.user.id,
                                    json.dumps(self.password_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Changement de mot de passe impossible")

    def test_invalid_new_password(self):
        # Setting old password
        self.user.set_password(self.password_data['old_password'])
        self.user.save()
        # Re-login
        self.api_login(password=self.password_data['old_password'])
        self.assertTrue(self.user.check_password(self.password_data['old_password']))
        # Empty new
        self.password_data['new_password'] = "pok"
        response = self.client.put('/api/user/%i/change_password/' % self.user.id,
                                    json.dumps(self.password_data),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Changement de mot de passe impossible")
