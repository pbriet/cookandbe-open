from collections                        import defaultdict

from django.core.cache.backends.locmem  import LocMemCache
from django.utils                       import timezone
from mock                               import patch

from common.date                        import make_utc, is_aware

from functools                          import update_wrapper

from paybox                             import Level

import common.date
import datetime
import diet_mgr.handlers.anc
import diet_mgr.handlers.base
import diet_mgr.tasks
import django.conf
import django.core.cache
import eater_mgr.ratios
import facebook
import hippocrate.models.problem
import hippocrate.views.api
import optalim.mongo
import paybox.models
import paybox.controller
import paybox.prices
import diet_mgr.serializers
import planning_mgr.controller.dish
import planning_mgr.controller.planning
import planning_mgr.serializers
import planning_mgr.tasks
import planning_mgr.views.content
import profile_mgr.models
import user_mgr
import user_mgr.models
import user_mgr.views
import re
import recipe_mgr.seasons
import shopping_mgr.views
import django.db.models.fields

def fake_today(*args):
    def fcn():
        return datetime.date(*args)
    return fcn

def fake_now(*args):
    def fcn():
        dt = make_utc(datetime.datetime(*args))
        assert is_aware(dt)
        return dt
    return fcn

def fake_today_decorator(year=2014, month=3, day=2, hour=0, minute=0, second=0):
    """
    Does some tricks, like setting a fake today, to be able to call suggest from
    the tests
    """
    def decorator(fcn):
        @patch.object(common.date, 'today', fake_today(year, month, day))
        @patch.object(common.date, 'today_aware', fake_now(year, month, day, 0, 0, 0))
        @patch.object(paybox.controller, 'today', fake_today(year, month, day))
        @patch.object(paybox.models, 'today', fake_today(year, month, day))
        @patch.object(paybox.prices, 'today_aware', fake_now(year, month, day, 0, 0, 0))
        @patch.object(planning_mgr.controller.planning, 'today', fake_today(year, month, day))
        @patch.object(planning_mgr.serializers, 'today', fake_today(year, month, day))
        @patch.object(planning_mgr.tasks, 'today', fake_today(year, month, day))
        @patch.object(planning_mgr.views.content, 'today', fake_today(year, month, day))
        @patch.object(profile_mgr.models, 'today', fake_today(year, month, day))
        @patch.object(recipe_mgr.seasons, 'today', fake_today(year, month, day))
        @patch.object(diet_mgr.handlers.base, 'today', fake_today(year, month, day))
        @patch.object(diet_mgr.tasks, 'today', fake_today(year, month, day))
        @patch.object(hippocrate.views.api, 'today', fake_today(year, month, day))
        @patch.object(shopping_mgr.views, 'today', fake_today(year, month, day))
        @patch.object(profile_mgr.history, 'today_aware', fake_now(year, month, day, 0, 0, 0))
        @patch.object(timezone, 'now', fake_now(year, month, day, hour, minute, second))
        @patch.object(user_mgr.models, 'today', fake_today(year, month, day))
        @patch.object(user_mgr.views, 'today', fake_today(year, month, day))
        @patch.object(django.db.models.fields.timezone, 'now', fake_now(year, month, day, hour, minute, second)) # Mocks the auto_now_add
        def new_fcn(*args, **kargs):
            return fcn(*args, **kargs)
        new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
        return new_fcn
    return decorator

def fake_ratios_decorator(ratio=1):
    """
    Make a default ratio of <ratio> for every meal/profile
    """
    def mock_profile_ratio(*x, **y): return defaultdict(lambda: ratio)
    def decorator(fcn):
        @patch.object(eater_mgr.ratios.RatiosCalculator, 'get_initial_ratios', mock_profile_ratio)
        def new_fcn(*args, **kargs):
            return fcn(*args, **kargs)
        new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
        return new_fcn
    return decorator

def fake_ratio_variable(name, value):
    """
    Use a fake calories reference in the ratio calculation
    """
    def decorator(fcn):
        @patch.object(eater_mgr.ratios, name, value)
        def new_fcn(*args, **kargs):
            return fcn(*args, **kargs)
        new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
        return new_fcn
    return decorator

class FakeNow(object):
    """
    Patches timezone.now()
    Use this way:
    with FakeNow(2014, 3, 2):
        do_stuff(...)
        self.assertEqual(...)
    """
    def __init__(self, *date):
        self.date_patch = patch.object(timezone, 'now', fake_now(*date))

    def __enter__(self, *args, **kargs):
        self.date_patch.__enter__(*args, **kargs)

    def __exit__(self, *args, **kargs):
        self.date_patch.__exit__(*args, **kargs)


def empty_diet_decorator(fcn):
    @patch.object(diet_mgr.handlers.anc.AncStandardDiet, 'build_nutrient_constraints', lambda x, *a: [])
    def new_fcn(*args, **kargs):
        return fcn(*args, **kargs)
    new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
    return new_fcn


class FakeCache(LocMemCache):
    """
    Local memory cache with additional keys method, like Redis
    """
    def __init__(self):
        super().__init__('temporary_fake_cache', {})
        self.all_keys = set()

    def set(self, key, value, *args, **kargs):
        self.all_keys.add(key)
        return super().set(key, value, *args, **kargs)

    def set_many(self, d, *args, **kargs):
        self.all_keys = self.all_keys.union(d.keys)
        return super().set_many(d, *args, **kargs)

    def delete(self, key):
        self.all_keys.remove(key)
        return super().delete(key)

    def delete_many(self, keys):
        self.all_keys = self.all_keys.difference(keys)
        return super().delete_many(keys)

    def keys(self, pattern):
        res = []
        for key in self.all_keys:
            if re.compile(pattern).match(key):
                res.append(key)
        return res

def fake_redis_cache_decorator(fcn):
    fake_cache = FakeCache()
    @patch.object(django.core.cache, 'cache', fake_cache)
    @patch.object(recipe_mgr.seasons, 'cache', fake_cache)
    @patch.object(recipe_mgr.models, 'cache', fake_cache)
    def new_fcn(*args, **kargs):
        return fcn(*args, **kargs)
    new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
    return new_fcn

class FakeGraphAPI(object):
    GOOD_TOKEN = 'MY_TOKEN'

    def __init__(self, token=None, version=None):
        if token is not None:
            assert token == self.GOOD_TOKEN, "Unexpected token"

    def request(self, request_name, data):

        return {'data': {'is_valid': data['input_token'] == self.GOOD_TOKEN}}

    def get_object(self, *args, **kargs):
        assert args == ('me',), "Expected 'me' in get_object"

        return {'email': 'toto@titi.fr',
                'birthday': '1/30/2004',
                'first_name': 'Plops',
                'id':  '103',
                'last_name':  'Zoo',
                'gender':    'female'}


class MockMongoTable(object):
    def __init__(self):
        # Table name -> list of entries
        self.written_data = []

    def find(*args, **kargs):
        raise NotImplementedError("find not implemented in when mongo is mocked")
    find_one = find

    def insert_one(self, entry):
        self.written_data.append(entry)

def fake_django_login(fcn):
    @patch.object(user_mgr.auth, 'django_login', lambda *args: True)
    def new_fcn(*args, **kargs):
        return fcn(*args, **kargs)
    update_wrapper(new_fcn, fcn)
    return new_fcn

def fake_mongo_decorator(fcn):
    mock_tables = {}
    def fake_log_table(name):
        if name not in mock_tables:
            mock_tables[name] = MockMongoTable()
        return mock_tables[name]

    @patch.object(optalim.mongo.Mongo, 'log_table', fake_log_table)
    def new_fcn(_self, *args, **kargs):
        return fcn(_self, mock_tables, *args, **kargs)
    new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
    return new_fcn


MOCK_PRICES = {
    Level.PREMIUM : {
        1:  500,
        3:  400,
        12: 300
    },
    # Level.PREMIUM    : {
    #     1:  2000,
    #     3:  1500,
    #     12: 1000
    # }
}

def fake_prices_decorator(fcn):
    @patch.object(paybox.prices, 'BASE_PRICES', MOCK_PRICES)
    def new_fcn(*args, **kargs):
        return fcn(*args, **kargs)
    new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
    return new_fcn

