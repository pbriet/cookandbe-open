
from user_mgr.models                import User

from django.utils                   import timezone

from discussion.models              import Discussion, Publication, Message
from discussion.serializers         import DiscussionSerializer
from discussion.tests               import BaseTestDiscussion

from common.model                   import reload_object

from mock                           import patch

class TestMessage(BaseTestDiscussion):

    def setUp(self):
        super().setUp()
        self.unwanted_dietician     = self.create_db_user(name = "Dukan", roles = ("dietician", ))
        self.spy                    = self.create_db_user(name = "007")
        self.god                    = self.create_db_user(name = "42", roles = ("admin", ))
        self.discussion             = self.create_db_discussion()

    @patch('discussion.controls.sendmail_template')
    def test_create_message(self, mock_sendmail_template):
        self.assertEqual(self.user.messages.count(), 0)

        # The user
        self.api_create_message(self.discussion, self.user, 201)
        self.assertEqual(self.user.messages.count(), 1)
        self.api_create_message(self.discussion, self.user, 201)
        self.assertEqual(self.user.messages.count(), 2)

        # The first dietician to respond takes the discussion
        reload_object(self.discussion)
        self.assertEqual(self.discussion.dietician, None)
        self.api_create_message(self.discussion, self.thierry, 201)
        reload_object(self.discussion)
        self.assertEqual(self.discussion.dietician, self.thierry)

        # Not your conversation !
        self.api_create_message(self.discussion, self.spy, 403)

        # Not your patient !
        self.api_create_message(self.discussion, self.unwanted_dietician, 403)
        reload_object(self.discussion)
        self.assertEqual(self.discussion.dietician, self.thierry)

        # Not your concern my lord !
        self.api_create_message(self.discussion, self.god, 403)

    def test_create_message_pretending_being_someone_else(self):
        user_message                = self.create_db_message(self.discussion)
        self.discussion.dietician   = self.thierry
        self.discussion.closed      = timezone.now()
        self.discussion.save()

        expected = (
            (None,                      401), # anonymous
            (self.thierry,              403), # dietician
            (self.unwanted_dietician,   403), # other dietician
            (self.spy,                  403), # other user
            (self.god,                  403), # admin
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            response = self.client.post('/api/message', self.get_msg_args(self.discussion, author=self.discussion.owner.id))
            self.assertEqual(response.status_code, expected_code)

    def test_create_message_when_discussion_closed(self):
        user_message                = self.create_db_message(self.discussion)
        self.discussion.dietician   = self.thierry
        self.discussion.close_date  = timezone.now()
        self.discussion.save()

        expected = (
            (None,                      401), # anonymous
            (self.user,                 403), # user
            (self.thierry,              403), # dietician
            (self.unwanted_dietician,   403), # other dietician
            (self.spy,                  403), # other user
            (self.god,                  403), # admin
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            if user is None:
                # Special anonymous user
                user = self.user
            response = self.client.post('/api/message', self.get_msg_args(self.discussion, author=user.id))
            self.assertEqual(response.status_code, expected_code)

    def test_read_message(self):
        self.discussion.dietician = self.thierry
        self.discussion.save()
        user_message = self.create_db_message(self.discussion)

        expected = (
            (None,                      401), # anonymous
            (self.user,                 200), # user
            (self.thierry,              200), # dietician
            (self.unwanted_dietician,   200), # other dietician
            (self.spy,                  403), # other user
            (self.god,                  200), # admin
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            response = self.client.get('/api/message/%i' % user_message.id)
            self.assertEqual(response.status_code, expected_code)

    def test_destroy_message(self):
        self.discussion.dietician = self.thierry
        self.discussion.save()
        user_message = self.create_db_message(self.discussion)

        expected = (
            (None,                      401), # anonymous
            (self.user,                 403), # user
            (self.thierry,              403), # dietician
            (self.unwanted_dietician,   403), # other dietician
            (self.spy,                  403), # other user
            (self.god,                  204), # admin
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            response = self.client.delete('/api/message/%i' % user_message.id)
            self.assertEqual(response.status_code, expected_code)
