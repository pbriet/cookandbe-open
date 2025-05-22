
from shopping_mgr.models        import ShoppingItem

from common.test                import TestAPIWithLogin

import json, datetime

class TestShoppingItem(TestAPIWithLogin):
    LIST_DATE       = datetime.date(2015, 2, 12)
    NB_LIST_DAYS    = 7

    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        # Users
        self.other  = self.create_db_user(name = "007")
        self.admin  = self.create_db_user(name = "42", roles = ("admin", ))
        # List
        start_date = self.LIST_DATE
        end_date = self.LIST_DATE + datetime.timedelta(self.NB_LIST_DAYS)
        self.shopping_list = self.create_db_shopping_list(start_date=start_date, end_date=end_date)

    def get_item_args(self, **kargs):
        res = {
            "shopping_list": self.shopping_list.id,
            "forced_name": "Rutabagas",
            "forced_quantity": "42",
        }
        res.update(kargs)
        for k in list(res.keys()):
            if res[k] is None:
                del res[k]
        return res

    def api_create_item(self, actor, expected_code = 201, **kargs):
        self.change_user(user = actor)
        response = self.client.post('/api/shopping_item', self.get_item_args(**kargs))
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 201:
            return None
        return ShoppingItem.objects.get(id = response.data['id'])

    def api_get_item(self, actor, item_id, expected_code = 200):
        self.change_user(user = actor)
        response = self.client.get('/api/shopping_item/%i' % item_id)
        self.assertEqual(response.status_code, expected_code)
        if expected_code != response.status_code:
            print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return None
        return response.data

    def test_create_item(self):
        self.assertEqual(ShoppingItem.objects.count(), 0)
        # All ok
        kargs = {
            "shopping_list": self.shopping_list.id,
            "forced_name": "Topinambour",
            "forced_quantity": "13",
            "got_it": True,
        }
        item = self.api_create_item(self.user, 201, **kargs)
        self.assertEqual(ShoppingItem.objects.count(), 1)
        expected = {
            'shopping_list_id': self.shopping_list.id,
            'got_it': True,
            'forced_quantity': '13',
            'grams': None,
            'food_id': None,
            'forced_name': 'Topinambour',
            'raw_state_id': None,
            'is_custom': True,
        }
        for key, value in expected.items():
            self.assertEqual(getattr(item, key), value)
        # No forced_quantity
        self.api_create_item(self.user, 403, forced_quantity=None)
        self.assertEqual(ShoppingItem.objects.count(), 1)
        # No forced_name
        self.api_create_item(self.user, 403, forced_name=None)
        self.assertEqual(ShoppingItem.objects.count(), 1)

    def test_create_item_rights(self):
        expected = (
            (None,          401), # anonymous
            (self.other,    403), # pirate user
            (self.admin,    201), # admin
        )
        for user, expected_code in expected:
            print(user and user.get_full_name())
            self.api_create_item(user, expected_code)

    def test_read_item(self):
        # Creating item
        self.assertEqual(ShoppingItem.objects.count(), 0)
        food = self.create_db_food("meat", with_conversion=False)
        conv = self.create_db_food_conversion(food, value = 1, loss_coeff=0, shopping_compatible=True)
        item = self.create_db_shopping_item(self.shopping_list, food=food, raw_state=self.raw, grams=12, forced_quantity="22")
        # Reading
        data = self.api_get_item(self.user, item.id)
        self.assertEqual(ShoppingItem.objects.count(), 1)
        # Comparing
        expected = {
            'id': item.id,
            'shopping_list': self.shopping_list.id,
            'got_it': False,
            'forced_quantity': '22',
            'grams': 12,
            'food': food.id,
            'forced_name': None,
            'raw_state': self.raw.id,
        }
        self.assertEqual(data, expected)

    def test_read_item_rights(self):
        item = self.api_create_item(self.user)
        self.assertEqual(ShoppingItem.objects.count(), 1)

        expected = (
            (None,          401), # anonymous
            (self.other,    403), # pirate user
            (self.admin,    200), # admin
        )
        for user, expected_code in expected:
            print(user and user.get_full_name())
            self.api_get_item(user, item.id, expected_code)

    def test_destroy_item(self):
        item = self.api_create_item(self.user, 201)
        self.assertEqual(ShoppingItem.objects.count(), 1)

        expected = (
            (None,          401), # anonymous
            (self.other,    403), # pirate user
            (self.admin,    204), # admin
            (self.user,     204), # himself
        )
        for user, expected_code in expected:
            print(user and user.get_full_name())
            self.change_user(user = user)
            response = self.client.delete('/api/shopping_item/%i' % item.id)
            self.assertEqual(response.status_code, expected_code)
            if expected_code == 204:
                self.assertEqual(ShoppingItem.objects.count(), 0)
                item = self.api_create_item(self.user)
            else:
                self.assertEqual(ShoppingItem.objects.count(), 1)

    def test_force_item(self):
        item = self.api_create_item(self.user, 201)

        expected = (
            (None,          401), # anonymous
            (self.other,    403), # pirate user
            (self.admin,    200), # admin
            (self.user,     200), # himself
        )
        for user, expected_code in expected:
            print(user and user.get_full_name())
            self.change_user(user = user)
            response = self.client.put('/api/shopping_item/%i/force' % item.id, { "quantity": 10, "name": "plop"})
            self.assertEqual(response.status_code, expected_code)
