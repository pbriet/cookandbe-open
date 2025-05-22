from common.test                    import TestAPIWithLogin
from common.mock_tools              import fake_redis_cache_decorator

from profile_mgr.models             import Taste

from optalim.main                   import OptalimWebsite
import profile_mgr.views

from mock                           import patch

def fake_max_percentage_decorator(fcn):
    @patch.object(profile_mgr.views, 'MAX_DISLIKE_PERCENTAGE', 0.25)
    def new_fcn(*args, **kargs):
        return fcn(*args, **kargs)
    new_fcn.__name__ = fcn.__name__  # cannot use update_wrapper because... mock is ugly
    return new_fcn


class TestTastes(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.init_db_profile_eater()
        dish_type = self.create_db_dishtype()
        # Creating 4 foods
        self.foods = []
        for i in range(4):
            self.foods.append(self.create_db_food("food%i" % i))

        # Creating 5 food_tags
        # Foodtag0 -> Food0
        # Foodtag1 -> Food1
        # Foodtag4 -> Foodtag2 -> Food2
        # Foodtag4 -> Foodtag3-> Food3

        self.food_tag0 = self.create_db_food_tag('foodtag0', foods=[self.foods[0]])
        self.food_tag1 = self.create_db_food_tag('foodtag1', foods=[self.foods[1]])
        self.food_tag2 = self.create_db_food_tag('foodtag2', foods=[self.foods[2]])
        self.food_tag3 = self.create_db_food_tag('foodtag3', foods=[self.foods[3]])
        self.food_tag4 = self.create_db_food_tag('foodtag4', children=[self.food_tag2, self.food_tag3])

        def get_food(i):
            # Recipe count :
            # [0-4]   : Food0 (foodtag0)
            # [6-14]  : Food1 (foodtag1)
            # [15-16] : Food2 (foodtag2, foodtag4)
            # [17-19] : Food3 (foodtag3, foodtag4)
            if i <= 4:  return self.foods[0]
            if i <= 14: return self.foods[1]
            if i <= 16: return self.foods[2]
            return self.foods[3]

        for i in range(20):
            recipe = self.create_db_recipe("recipe_%i" % i, dish_types=[dish_type])
            food = get_food(i)
            ingredient = self.create_db_ingredient(recipe, food, 100)

        # Final count is :
        # Foodtag0 : 5
        # Foodtag1 : 10
        # Foodtag2 : 2
        # Foodtag3 : 3
        # Foodtag4 : 5


    @fake_redis_cache_decorator
    @fake_max_percentage_decorator
    def _test_dislike(self, food_tag_id, expect_success, expected_nb_tastes):

        # Max is 25%, i.e. 5
        OptalimWebsite.pre_cache()

        res = self.client.post('/api/taste', {'profile': self.profiles[0].id, 'creator': self.user.id,
                                             'food_tag': food_tag_id, 'fondness': -5, 'set_planning_expired': False})

        self.assertTrue(res.status_code in (200, 201))

        self.assertTrue(res.data.get('status', '') == '' or not expect_success)
        self.assertEqual(Taste.objects.count(), expected_nb_tastes)

    def test_dislike_one_25_percent(self):
        self._test_dislike(self.food_tag0.id, True, 1)
        self._test_dislike(self.food_tag2.id, False, 1)

    def test_dislike_two_smalls(self):
        self._test_dislike(self.food_tag2.id, True, 1)
        self._test_dislike(self.food_tag3.id, True, 2)

    def test_dislike_one_big(self):
        self._test_dislike(self.food_tag1.id, False, 0)

    def test_dislike_one_big_parent(self):
        self._test_dislike(self.food_tag4.id, True, 1)
        self._test_dislike(self.food_tag0.id, False, 1)

    def test_dislike_two_food_tags_inherited(self):
        self._test_dislike(self.food_tag4.id, True, 1)
        self._test_dislike(self.food_tag2.id, True, 2)

    def test_dislike_twice_same_food_tag(self):
        self._test_dislike(self.food_tag2.id, True, 1)
        self._test_dislike(self.food_tag2.id, False, 1)
        self._test_dislike(self.food_tag3.id, True, 2)