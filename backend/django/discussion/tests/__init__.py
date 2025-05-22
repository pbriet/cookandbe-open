
from discussion.models              import Discussion, Publication, Message
import discussion.controls

from common.test                    import TestAPIWithLogin
from common.mock_tools              import FakeNow, fake_today_decorator
from common.model                   import reload_object
from common.date                    import make_utc, get_month_range

from mock                           import patch, MagicMock, call

import datetime

class FakeThierry(object):
    def __init__(self, thierry):
        self.patch = patch.object(discussion.controls, '_get_thierry', lambda: thierry)

    def __enter__(self, *args, **kargs):
        self.patch.__enter__(*args, **kargs)

    def __exit__(self, *args, **kargs):
        self.patch.__exit__(*args, **kargs)

class BaseTestDiscussion(TestAPIWithLogin):

    _SECOND = 0

    def setUp(self):
        super().setUp()
        self.thierry = self.create_db_user(name = "Test Thierry", roles = ("dietician", ), auto_create_main_profile = True)

    def get_next_now(cls):
        cls._SECOND += 1
        return (2015, 4, 21, 13, 37, cls._SECOND)

    now = property(lambda x: make_utc(datetime.datetime(*x.get_next_now())))

    def get_dsc_args(self, **kargs):
        default_kargs = {
            "title": "That's a good one ?",
            "owner": self.user.id,
            "dietician": "",
        }
        default_kargs.update(kargs)
        return default_kargs

    def get_msg_args(self, discussion, **kargs):
        default_kargs = {
            "content": "not much",
            "author": self.user,
            "discussion": discussion.id,
        }
        default_kargs.update(kargs)
        return default_kargs

    def api_create_discussion(self, owner = None, expected_code = 201):
        if owner is None:
            owner = self.premium
        self.change_user(user = owner)
        with FakeNow(*self.get_next_now()), FakeThierry(self.thierry):
            response = self.client.post('/api/discussion', self.get_dsc_args(owner=owner.id))
        self.assertEqual(response.status_code, expected_code)
        if expected_code != response.status_code:
            print(response.data)
        if response.status_code != 201:
            return None
        return Discussion.objects.get(id = response.data['id'])

    def api_create_message(self, discussion, author, expected_code = 201):
        self.change_user(user = author)
        with FakeNow(*self.get_next_now()), FakeThierry(self.thierry):
            response = self.client.post('/api/message', self.get_msg_args(discussion, author=author.id))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 201:
            return None
        return Message.objects.get(id = response.data['id'])

    def api_close_discussion(self, discussion, user, expected_code = 200):
        self.change_user(user = user)
        reload_object(discussion)
        response = self.client.post('/api/discussion/%i/status' % discussion.id, self.get_dsc_args(dietician=discussion.dietician.id, close=True))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        return response

    def api_reopen_discussion(self, discussion, user, expected_code = 200):
        self.change_user(user = user)
        reload_object(discussion)
        response = self.client.post('/api/discussion/%i/status' % discussion.id, self.get_dsc_args(dietician=discussion.dietician.id, close=False))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        return response

    def api_read_discussion(self, discussion, user, expected_code = 200):
        self.change_user(user = user)
        reload_object(discussion)
        response = self.client.post('/api/discussion/%i/read' % discussion.id, self.get_dsc_args(dietician=discussion.dietician.id, user_id=user.id))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        return response

    def api_destroy_discussion(self, discussion, user, expected_code = 200):
        self.change_user(user = user)
        response = self.client.delete('/api/discussion/%i' % discussion.id)
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        return response

    def api_list_discussions(self, user, expected_code = 200):
        self.change_user(user = user)
        response = self.client.get('/api/discussion')
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def db_check_unread_messages(self, discussion, user, expected_unread):
        reload_object(discussion)
        print(None if user is None else user.first_name)
        self.assertEqual(discussion.nb_unread_messages(None if user is None else user.id), expected_unread)

    def api_get_quota(self, user, expected_code = 200):
        self.change_user(user)
        response = self.client.get('/api/user/%i/question_quota' % user.id)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def get_quota_args(self, **kargs):
        default_kargs = {
            "start_date": get_month_range()[0],
            "end_date": get_month_range()[1],
            "max_questions": 0,
            "question_count": 0,
        }
        default_kargs.update(kargs)
        return default_kargs

    def api_get_publication(self, publication, user, expected_code = 200):
        self.change_user(user)
        response = self.client.get('/api/publication/%i' % publication.id)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def get_publication_args(self, dietician, **kargs):
        default_kargs = {
            "question": "A",
            "response": "B",
            "user_sex": True,
            "user_date": datetime.date(2015, 1, 1),
        }
        author = dietician and dietician.id,
        if author is not None:
            default_kargs["author"] = author
        default_kargs.update(kargs)
        return default_kargs

    def api_create_publication(self, author, expected_code = 201):
        self.change_user(user = author)
        with FakeNow(*self.get_next_now()):
            response = self.client.post('/api/publication', self.get_publication_args(author))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 201:
            return None
        return Publication.objects.get(id = response.data['id'])

    def api_change_publication(self, publication, user, kargs, expected_code = 200):
        self.change_user(user = user)
        response = self.client.put('/api/publication/%i' % publication.id, kargs)
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        return response

    def api_list_publications(self, user, expected_code = 200):
        self.change_user(user = user)
        response = self.client.get('/api/publication')
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def api_search_publications(self, user, keywords, hidden = True, expected_code = 200):
        self.change_user(user = user)
        response = self.client.get('/api/publication/search', { 'keywords': keywords, 'hidden': hidden} )
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def api_set_discussion_publication(self, user, discussion, publication, expected_code = 200):
        self.change_user(user = user)
        response = self.client.post('/api/discussion/%i/set_publication' % discussion.id, { "publication_id": publication.id })
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data
