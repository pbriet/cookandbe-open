from common.test                import OptalimTest, add_permissions, TestAPIWithLogin
from django.utils               import timezone
from user_mgr.models            import User, AutologinToken

from datetime                   import timedelta
import json

class TestLogIn(OptalimTest):
    def test_not_logged_in(self):
        response = self.client.get('/api/current_user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'not logged in')


    def test_login_logout(self):
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()

        values = {"login": self.LOGIN, "password": self.PASSWORD}
        self.api_login(**values)

        response = self.client.get('/api/current_user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['userid'], user.id)
        self.assertEqual(response.data['username'], 'kaloo')

        self.api_logout()

        response = self.client.get('/api/current_user/')
        self.assertEqual(response.data['status'], 'not logged in')

    # def test_login_from_tablet(self):
    #     # With uppercase of the first letter! bloody iPads...
    #    (handled by frontend)
    #     self.assertEqual(User.objects.count(), 1)
    #     user = User.objects.get()

    #     values = {"login": "Test@test.fr", "password": self.PASSWORD}
    #     self.api_login(**values)

    #     response = self.client.get('/api/current_user/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['userid'], user.id)


    def test_autologin_does_not_exist(self):
        """
        Test autologin with invalid tokens
        """
        self.assertEqual(User.objects.count(), 1)

        for wrong_token in ('ABCD', 'e6dd29cd-34e3-4742-98da-a00c5304c523', ''):

            response = self.client.post('/api/autologin/', json.dumps({'token': wrong_token}),
                                        content_type="application/json")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data['status'], 'ko')
            self.assertEqual(response.data['code'], 'INVALID_TOKEN')

    def test_autologin_success(self):
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()

        token_obj = AutologinToken.objects.create(user=user, valid_until=timezone.now() + timedelta(seconds=45))

        response = self.client.post('/api/autologin/', json.dumps({'token': str(token_obj.token)}),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ok')

        self.set_jwt_access_token(response.data['access'])

        response = self.client.get('/api/current_user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['userid'], user.id)


    def test_autologin_expired(self):
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()

        token_obj = AutologinToken.objects.create(user=user, valid_until=timezone.now() - timedelta(seconds=45))

        response = self.client.post('/api/autologin/', json.dumps({'token': str(token_obj.token)}),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ko')
        self.assertEqual(response.data['code'], 'TOKEN_EXPIRED')


    def test_autologin_inactive(self):
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()

        user.access_closed = True
        user.save()

        token_obj = AutologinToken.objects.create(user=user, valid_until=timezone.now() + timedelta(seconds=45))

        response = self.client.post('/api/autologin/', json.dumps({'token': str(token_obj.token)}),
                                    content_type="application/json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ko')
        self.assertEqual(response.data['code'], 'DISABLED_ACCOUNT')

class TestLogInAs(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.assert_is_logged_in(self.user.id)
        self.user2 = self.create_db_user("other_user")

    def assert_is_logged_in(self, user_id):
        response = self.client.get('/api/current_user/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'logged in')
        self.assertEqual(response.data['userid'], user_id)

    @add_permissions("admin")
    def test_login_as(self):
        response = self.client.post('/secure/api/login_as/', {'user_id': self.user2.id })
        self.assertEqual(response.status_code, 200)
        self.set_jwt_access_token(response.data['access'])
        self.assert_is_logged_in(self.user2.id)

    def test_permission(self):
        # No admin permission, it should fail
        response = self.client.post('/secure/api/login_as/', {'user_id': self.user2.id })
        self.assertEqual(response.status_code, 403)
        self.assert_is_logged_in(self.user.id)
