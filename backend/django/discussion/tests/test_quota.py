
from discussion.models              import Discussion, Publication, Message
from discussion.serializers         import DiscussionSerializer
from discussion.tests               import BaseTestDiscussion

from common.mock_tools              import FakeNow, fake_today_decorator

from mock                           import patch, MagicMock, call

from django.utils                   import timezone

import datetime

DATE_ARGS       = (2015, 2, 10)

FREE_QUOTA      = 0
PREMIUM_QUOTA   = 5

class TestDiscussionQuota(BaseTestDiscussion):

    def get_next_now(cls):
        dt = timezone.now()
        return tuple(list(dt.utctimetuple())[0:6])

    def setUp(self):
        super().setUp()
        self.free       = self.create_db_user(name = "Free subscriber",    subscription_level = 0, auto_create_main_profile = True)
        self.premium    = self.create_db_user(name = "Premium subscriber", subscription_level = 1, auto_create_main_profile = True)
        self.create_db_subscription(user = self.premium, level = 1, enabled = True, start_date = datetime.date(*DATE_ARGS), nb_days = 30, nb_months=0)

    @fake_today_decorator(*DATE_ARGS)
    def test_default_quota(self):
        expected_quota = (
            (self.free,     self.get_quota_args(max_questions = FREE_QUOTA)),
            (self.premium,  self.get_quota_args(max_questions = PREMIUM_QUOTA, start_date = datetime.date(*DATE_ARGS))),
        )
        for user, quota in expected_quota:
            res = self.api_get_quota(user, 200)
            self.assertEqual(res, quota)

    @fake_today_decorator(*DATE_ARGS)
    def test_other_user_quota(self):
        self.target     = self.create_db_user(name = "007", subscription_level = 2)
        self.dietician  = self.create_db_user(name = "Test dukan", roles = ("dietician", ))
        self.admin      = self.create_db_user(name = "42", roles = ("admin", ))
        expected_quota = (
            (None,              401),
            (self.free,         403),
            (self.premium,      403),
            (self.dietician,    403),
            (self.admin,        200),
        )
        for user, expected_code in expected_quota:
            self.change_user(user)
            response = self.client.get('/api/user/%i/question_quota' % self.target.id)
            self.assertEqual(response.status_code, expected_code)
            if response.status_code == 200:
                self.assertEqual(response.data, self.get_quota_args(max_questions = PREMIUM_QUOTA, start_date = datetime.date(*DATE_ARGS)))

    @fake_today_decorator(*DATE_ARGS)
    def test_quota_evolution(self):
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, question_count = 0, start_date = datetime.date(*DATE_ARGS)))
        for i in range(1, PREMIUM_QUOTA):
            self.create_db_discussion(owner = self.premium)
            quota = self.api_get_quota(self.premium)
            self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, question_count = i, start_date = datetime.date(*DATE_ARGS)))
        self.api_create_discussion(self.premium, 201)
        self.api_create_discussion(self.premium, 403)
        for i in range(PREMIUM_QUOTA + 1, PREMIUM_QUOTA + 5):
            self.create_db_discussion(owner = self.premium)
            quota = self.api_get_quota(self.premium)
            self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, question_count = i, start_date = datetime.date(*DATE_ARGS)))
        self.api_create_discussion(self.premium, 403)


class TestDiscussionQuotaOverTime(BaseTestDiscussion):

    def get_next_now(cls):
        dt = timezone.now()
        return tuple(list(dt.utctimetuple())[0:6])

    def setUp(self):
        super().setUp()
        self.start_date = datetime.date(2015, 2, 10)
        self.end_date   = datetime.date(2015, 3, 10)
        self.premium    = self.create_db_user(name = "Premium subscriber", subscription_level = 2, auto_create_main_profile = True)
        self.create_db_subscription(user = self.premium, level = 2, enabled = True, start_date = self.start_date, end_date = self.end_date)

    @fake_today_decorator(2015, 1, 15)
    def test_discussion_anterior(self):
        self.api_create_discussion(self.premium, 403)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = FREE_QUOTA))

    @fake_today_decorator(2015, 3, 15)
    def test_discussion_posterior(self):
        self.api_create_discussion(self.premium, 403)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = FREE_QUOTA))

    @fake_today_decorator(2015, 2, 10)
    def test_discussion_start_limit(self):
        self.api_create_discussion(self.premium, 201)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, start_date = self.start_date, question_count = 1))

    @fake_today_decorator(2015, 2, 9)
    def test_discussion_start_limit_minus(self):
        self.api_create_discussion(self.premium, 403)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = FREE_QUOTA))

    @fake_today_decorator(2015, 3, 10)
    def test_discussion_end_limit(self):
        self.api_create_discussion(self.premium, 201)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, end_date = self.end_date, question_count = 1))

    @fake_today_decorator(2015, 3, 11)
    def test_discussion_end_limit_plus(self):
        self.api_create_discussion(self.premium, 403)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = FREE_QUOTA))

    @fake_today_decorator(2015, 3, 1)
    def test_quota_reset(self):
        for i in range(1, 6):
            self.change_user(self.premium)
            discussion = self.create_db_discussion(owner = self.premium)
            dt = datetime.datetime.combine(self.start_date, datetime.datetime.min.time())
            discussion.creation_date = timezone.make_aware(dt, timezone.get_default_timezone())
            discussion.save()
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, end_date = self.end_date, question_count = 0))
        self.api_create_discussion(self.premium, 201)
        quota = self.api_get_quota(self.premium)
        self.assertEqual(quota, self.get_quota_args(max_questions = PREMIUM_QUOTA, end_date = self.end_date, question_count = 1))
