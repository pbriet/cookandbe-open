
from shopping_mgr.controller    import fill_shopping_list

from common.test                import TestAPIWithLogin

from recipe_mgr.models          import RawState

from datetime                   import date, timedelta

import json

class TestForced(TestAPIWithLogin):
    
    LIST_DATE       = date(2015, 2, 12)
    NB_LIST_DAYS    = 7
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.shopping_list = None

    def _fill_shopping_list(self, food_name, quantity=None, forced_quantity=None, forced_name=None):
        # Cleaning list
        if self.shopping_list is not None:
            self.shopping_list.delete()
        start_date = self.LIST_DATE
        end_date = self.LIST_DATE + timedelta(self.NB_LIST_DAYS)
        self.shopping_list = self.create_db_shopping_list(start_date=start_date, end_date=end_date)
        # Filling list
        if forced_name is not None:
            self.create_db_shopping_item(self.shopping_list, forced_quantity=forced_quantity, forced_name=forced_name, custom=True)
        else:
            food        = self.create_db_food(food_name, with_conversion = False)
            food_cnv    = self.create_db_food_conversion(food, value=1, shopping_compatible=True, loss_coeff=0)
            self.create_db_shopping_item(self.shopping_list, food=food, raw_state=self.raw, grams=quantity, forced_quantity=forced_quantity, forced_name=forced_name)
        fill_shopping_list(self.shopping_list)
        self.assertEqual(self.shopping_list.items.count(), 1)

    def _check_list_item(self, food_name, quantity, forced_name=None, forced_quantity=None):
        response = self.client.get('/api/user/%i/shopping_list/%i' % (self.user.id, self.shopping_list.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['content']), 1)
        self.assertEqual(len(response.data['content'][0]['items']), 1)
        item = response.data['content'][0]['items'][0]
        print("item", item)
        if food_name is not None:
            self.assertEqual(item['food']['name'], food_name)
        else:
            self.assertEqual(item['food'], None)
        if quantity is not None and forced_name is None:
            self.assertEqual(item['conversion']['value'], quantity)
        else:
            self.assertEqual(item['conversion'], None)
        self.assertEqual(item['forced_quantity'], forced_quantity)
        self.assertEqual(item['forced_name'], forced_name)

    def test_forced_quantity(self):
        self._fill_shopping_list("meat", quantity=40)
        self._check_list_item("meat", 40)
        self._fill_shopping_list("fish", quantity=40, forced_quantity="67")
        self._check_list_item("fish", 40, forced_quantity="67")

    def test_forced_name(self):
        # Custom item
        self._fill_shopping_list(None, forced_quantity=40, forced_name="meat")
        self._check_list_item("meat", None, forced_quantity="40", forced_name="meat")
        # Standard item
        self._fill_shopping_list("fish", quantity=40, forced_name="salmon")
        self._check_list_item("salmon", 40, forced_name="salmon")
