from django.conf                    import settings

from discussion.models              import Discussion, Publication, Message
from discussion.serializers         import DiscussionSerializer
from discussion.tests               import BaseTestDiscussion

from common.model                   import reload_object
from common.mock_tools              import FakeNow, fake_today_decorator

from mock                           import patch, MagicMock, call
from freezegun                      import freeze_time

import datetime


class TestDiscussion(BaseTestDiscussion):

    @freeze_time("2015-04-01")
    def setUp(self):
        super().setUp()
        self.dietician  = self.create_db_user(name = "Test dietician", roles = ("dietician", ), auto_create_main_profile = True)
        self.premium    = self.create_db_user(name = "Premium subscriber", subscription_level = 1, auto_create_main_profile = True)
        self.god        = self.create_db_user(name = "42", roles = ("admin", ))

    @freeze_time("2015-08-21")
    def test_new_discussion(self):
        self.assertEqual(Discussion.objects.count(), 0)
        self.assertEqual(self.user.subscription_level, 0)
        expected = (
            (self.thierry,  403), # dietician
            (self.user,     403), # free user
            (self.premium,  201), # premium user
        )
        for user, expected_code in expected:
            self.api_create_discussion(owner = user, expected_code = expected_code)
        self.assertEqual(Discussion.objects.count(), 1)

    def test_new_discussion_pretending_being_someone_else(self):
        self.assertEqual(self.user.subscription_level, 0)
        expected = (
            (None,          401), # anonymous
            (self.thierry,  403), # dietician
            (self.user,     403), # free user
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            response = self.client.post('/api/discussion', self.get_dsc_args(owner=self.premium.id))
            self.assertEqual(response.status_code, expected_code)
        self.assertEqual(Discussion.objects.count(), 0)

    @freeze_time("2015-08-21")
    def test_discussion_dietician(self):
        discussion = self.api_create_discussion()
        self.assertEqual(discussion.dietician, None)
        self.api_create_message(discussion, self.thierry)
        reload_object(discussion)
        self.assertEqual(discussion.dietician, self.thierry)
        self.api_create_message(discussion, self.dietician, 403)
        reload_object(discussion)
        self.assertEqual(discussion.dietician, self.thierry)

    @patch('discussion.controls.sendmail_template')
    @freeze_time("2015-04-21")
    def test_mail_new_question(self, mock_sendmail_template):
        self.assertEqual(Discussion.objects.count(), 0)
        discussion = self.api_create_discussion(self.premium, 201)
        expected_calls = [call(
            0,
            'discussion/templates/new_question.html',
            {'discussion_id': discussion.id, 'discussion_title': "That's a good one ?"},
            '[%s] Nouvelle question utilisateur' % settings.APP_BRAND_NAME,
            users=[self.thierry],
            tags=['new_question'],
        )]
        self.assertEqual(mock_sendmail_template.mock_calls, expected_calls)
        self.assertEqual(Discussion.objects.count(), 1)
        discussion = Discussion.objects.get()
        # No new email, even if we add a message, until the conversation is marked as read
        self.api_create_message(discussion, self.premium, 201)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 1)

    @patch('discussion.controls.sendmail_template')
    @freeze_time("2015-04-21")
    def test_mail_new_response(self, mock_sendmail_template):
        discussion = self.create_db_discussion(owner = self.premium)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 0)
        # New reponse (send mail)
        self.api_create_message(discussion, self.thierry)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 1)
        expected_call = call(
            0,
            'discussion/templates/new_response.html',
            {'end_of_month': datetime.date(2015, 4, 30), 'nb_month_questions': 1, 'dietician_name': 'Test Thierry', 'remaining_questions': 4, 'discussion_title': 'Good question !', 'discussion_id': discussion.id},
            '[%s] Good question !' % settings.APP_BRAND_NAME,
            tags=['new_response'],
            users=[self.premium]
        )
        self.assertEqual(mock_sendmail_template.mock_calls[0], expected_call)
        # Second reponse (no mail)
        self.api_create_message(discussion, self.thierry)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 1)
        # User read + third reponse (send mail)
        discussion.owner_read_date = self.now
        discussion.save()
        reload_object(discussion)
        self.api_create_message(discussion, self.thierry)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 2)
        self.assertEqual(mock_sendmail_template.mock_calls[1], expected_call)

    @patch('discussion.controls.sendmail_template')
    @freeze_time("2015-04-21")
    def test_mail_new_message(self, mock_sendmail_template):
        with FakeNow(*self.get_next_now()):
            discussion = self.create_db_discussion(owner = self.premium)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 0)
        with FakeNow(*self.get_next_now()):
            self.create_db_message(discussion, author = self.thierry)
        reload_object(discussion)
        discussion.dietician = self.thierry
        discussion.save()
        # New user message (send mail)
        self.api_create_message(discussion, self.premium)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 1)
        expected_call = call(
            0,
            'discussion/templates/new_message.html',
            {'discussion_id': discussion.id, 'discussion_title': 'Good question !'},
            '[%s] Nouveau message utilisateur' % settings.APP_BRAND_NAME,
            users=[self.thierry],
            tags=['new_message'],
        )
        self.assertEqual(mock_sendmail_template.mock_calls[0], expected_call)
        # Second reponse (no mail)
        self.api_create_message(discussion, self.premium)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 1)
        # Dietician response (send mail)
        self.api_create_message(discussion, self.thierry)
        self.assertEqual(len(mock_sendmail_template.mock_calls), 2)
        expected_call = call(
            0, 'discussion/templates/new_response.html',
            {'remaining_questions': 4, 'dietician_name': 'Test Thierry', 'discussion_title': 'Good question !', 'end_of_month': datetime.date(2015, 4, 30), 'nb_month_questions': 1, 'discussion_id': discussion.id},
            '[%s] Good question !' % settings.APP_BRAND_NAME,
            users=[self.premium],
            tags=['new_response']
        )
        self.assertEqual(mock_sendmail_template.mock_calls[1], expected_call)

    @freeze_time("2015-08-21")
    def test_read_discussion(self):
        discussion = self.api_create_discussion(self.premium)

        expected = (
            (None,              401), # anonymous
            (self.premium,      200), # user
            (self.user,         404), # other user (404 because the queryset is filtered)
            (self.thierry,      200), # dietician
            (self.dietician,    200), # other dietician
            (self.god,          200), # admin
        )
        for user, expected_code in expected:
            self.change_user(user = user)
            response = self.client.get('/api/discussion/%i' % discussion.id)
            self.assertEqual(response.status_code, expected_code)

    @freeze_time("2015-08-21")
    def test_write_discussion(self):
        discussion = self.api_create_discussion(self.premium)
        self.api_create_message(discussion, self.thierry)

        expected = (
            (None,              401), # anonymous
            (self.premium,      403), # user
            (self.user,         403), # other user
            (self.thierry,      403), # dietician
            (self.dietician,    403), # other dietician
            (self.god,          403), # admin
        )
        for user, expected_code in expected:
            self.change_user(user)
            print(None if user is None else user.first_name)
            response = self.client.put('/api/discussion/%i' % discussion.id, self.get_dsc_args(dietician = self.thierry.id, title = "New title"))
            self.assertEqual(response.status_code, expected_code)

    @freeze_time("2015-08-21")
    def test_set_discussion_publication(self):
        discussion  = self.api_create_discussion(self.premium)
        publication = self.api_create_publication(self.thierry)

        expected = (
            (None,              401), # anonymous
            (self.premium,      403), # user
            (self.user,         403), # other user
            (self.thierry,      200), # dietician
            (self.dietician,    403), # other dietician
            (self.god,          200), # admin
        )
        for user, expected_code in expected:
            print(None if user is None else user.first_name)
            self.api_set_discussion_publication(user, discussion, publication, expected_code)

    @freeze_time("2015-08-21")
    def test_destroy_discussion(self):
        discussion = self.api_create_discussion(self.premium)
        self.api_create_message(discussion, self.thierry)

        expected = (
            (None,          401), # anonymous
            (self.premium,  403), # user
            (self.user,     403), # other user
            (self.thierry,  403), # dietician
            (self.dietician,    403), # other dietician
            (self.god,      403), # admin
        )
        for user, expected_code in expected:
            print(None if user is None else user.first_name)
            self.api_destroy_discussion(discussion, user, expected_code)

    @freeze_time("2015-08-21")
    def test_close_discussion(self):
        discussion = self.api_create_discussion(self.premium)
        self.api_create_message(discussion, self.thierry)
        response = self.client.get('/api/discussion/%i' % discussion.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['close_date'] is None)

        # Closing discussion
        self.api_close_discussion(discussion, self.thierry)
        response = self.client.get('/api/discussion/%i' % discussion.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['close_date'] is not None)

        # Checking rights
        expected = (
            (None,              401), # anonymous
            (self.premium,      403), # user
            (self.thierry,      200), # dietician
            (self.user,         403), # other user
            (self.dietician,    403), # other dietician
            (self.god,          200), # admin
        )
        for user, expected_code in expected:
            # New message
            if user is not None:
                print(user.first_name, user.email, user.id)
                self.api_create_message(discussion, user, expected_code = 403)
            # Reopen discussion
            print(None if user is None else user.first_name)
            self.api_reopen_discussion(discussion, user, expected_code = expected_code)
            if expected_code == 200:
                # Restoring
                self.api_close_discussion(discussion, self.thierry)

    @freeze_time("2015-08-21")
    def test_nb_unread_messages(self):
        print(">>> New discussion")
        with FakeNow(*self.get_next_now()):
            discussion = self.api_create_discussion(self.premium)
        expected = ( (None, 0), (self.premium, 0), (self.thierry, 0), (self.user, 0), (self.dietician, 0), (self.god, 0), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> New dietician message")
        with FakeNow(*self.get_next_now()):
            self.api_create_message(discussion, self.thierry)
        expected = ( (None, 1), (self.premium, 1), (self.thierry, 0), (self.user, 1), (self.dietician, 1), (self.god, 1), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> Second dietician message")
        with FakeNow(*self.get_next_now()):
            self.api_create_message(discussion, self.thierry)
        expected = ( (None, 2), (self.premium, 2), (self.thierry, 0), (self.user, 2), (self.dietician, 2), (self.god, 2), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> User message")
        with FakeNow(*self.get_next_now()):
            self.api_create_message(discussion, self.premium)
        expected = ( (None, 1), (self.premium, 0), (self.thierry, 1), (self.user, 1), (self.dietician, 1), (self.god, 1), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> Dietician read")
        self.api_read_discussion(discussion, self.thierry)
        expected = ( (None, 0), (self.premium, 0), (self.thierry, 0), (self.user, 0), (self.dietician, 0), (self.god, 0), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> New dietician message")
        with FakeNow(*self.get_next_now()):
            self.api_create_message(discussion, self.thierry)
        expected = ( (None, 1), (self.premium, 1), (self.thierry, 0), (self.user, 1), (self.dietician, 1), (self.god, 1), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> Discussion closed")
        self.api_close_discussion(discussion, self.thierry)
        expected = ( (None, 1), (self.premium, 1), (self.thierry, 0), (self.user, 1), (self.dietician, 1), (self.god, 1), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)
        print(">>> User read")
        with FakeNow(*self.get_next_now()):
            self.api_read_discussion(discussion, self.premium)
        expected = ( (None, 0), (self.premium, 0), (self.thierry, 0), (self.user, 0), (self.dietician, 0), (self.god, 0), )
        for user, expected_unread in expected:
            self.db_check_unread_messages(discussion, user, expected_unread)

    def test_list(self):
        with FakeNow(*self.get_next_now()):
            d1 = self.create_db_discussion(owner = self.premium)
        with FakeNow(*self.get_next_now()):
            d2 = self.create_db_discussion(owner = self.user)
        expected = (
            (None,          401, None),  # anonymous
            (self.thierry,  200, (d1, d2)), # dietician
            (self.dietician,200, (d1, d2)), # other dietician
            (self.user,     200, (d2, )),   # free user
            (self.premium,  200, (d1, )),   # premium user
            (self.god,      200, (d1, d2)), # admin
        )
        for user, expected_code, expected_items in expected:
            publications = self.api_list_discussions(user, expected_code = expected_code)
            if expected_code != 200:
                continue
            self.assertEqual(len(publications), len(expected_items))
            for publication, item in zip(publications, DiscussionSerializer(expected_items, many = True).data):
                for key, value in publication.items():
                    self.assertEqual(item[key], value)