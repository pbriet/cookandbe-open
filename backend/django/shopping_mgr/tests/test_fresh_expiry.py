
from shopping_mgr.controller    import fill_shopping_list

from common.test                import TestAPIWithLogin

from recipe_mgr.models          import RawState

from datetime                   import date, timedelta

import json

class TestFreshExpiry(TestAPIWithLogin):
    
    DAY_DATE = date(2015, 5, 22)
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.dish_type      = self.create_db_dishtype()
        self.day            = self.create_db_day(date=self.DAY_DATE.strftime("%Y-%m-%d"), skipped=False)
        self.meal_slot      = self.create_db_mealslot(self.day)
        self.dish           = self.create_db_dish(self.meal_slot, self.dish_type)
        self.dish_recipe    = None
        self.shopping_list  = None
        self.raw_state      = RawState.objects.get(name="frais")

    def _add_food(self, name, type_fresh_expiry, food_fresh_expiry, usually_stored, ):
        food_type   = self.create_db_foodtype(name + " foodtype", usually_stored=usually_stored, fresh_expiry=type_fresh_expiry)
        food        = self.create_db_food(name, food_type=food_type, fresh_expiry=food_fresh_expiry)
        food_cnv    = self.create_db_food_conversion(food, value=1)
        recipe      = self.create_db_recipe(dish_types=[self.dish_type])
        ingredient  = self.create_db_ingredient(recipe, food, 42, default_conversion=food_cnv, raw_state=self.raw_state)
        if not self.dish_recipe:
            self.dish_recipe = self.create_db_dishrecipe(self.dish, recipe, ratio=1, validated=True)
        else:
            self.dish_recipe.recipe = recipe
            self.dish_recipe.save()

    def _create_shopping_list(self, delay, nb_list_days = 7):
        start_date = self.DAY_DATE - timedelta(delay)
        end_date = start_date + timedelta(nb_list_days)
        if self.shopping_list:
            self.shopping_list.delete()
        self.shopping_list = self.create_db_shopping_list(start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"))
        fill_shopping_list(self.shopping_list)
        self.assertEqual(self.shopping_list.items.count(), 1)
        item = self.shopping_list.items.all()[0]

    def _check_item_expiry(self, food_expiry, freeze_warning, freeze_date):
        response = self.client.get('/api/user/%i/shopping_list/%i' % (self.user.id, self.shopping_list.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['content']), 1)
        category = response.data['content'][0]
        self.assertEqual(len(category['items']), 1)
        item = category['items'][0]
        print("_check_item_expiry", item)
        self.assertEqual(item['food']['fresh_expiry'], food_expiry)
        self.assertEqual(item['freeze_warning'], freeze_warning)
        self.assertEqual(item['freeze_date'], freeze_date)

    def test_no_expiry(self):
        data = [
            # Name, delay, warning
            ("farine", 0, False), # First day
            ("pates",  7, False), # Last day
        ]
        for name, delay, warning in data:
            self._add_food(name, None, None, False)
            self._create_shopping_list(delay)
            self._check_item_expiry(None, warning, None)

    def test_type_expiry(self):
        data = [
            # Name, type_expiry, delay, warning
            ("saumon", 2, 0, True),  # In time
            ("truite", 2, 6, True),  # Last minute
            # Old behavior (based on expiry < delay)
            ("crabe",  1, 1, True),  # Tomorrow
            ("huitre", 1, 4, True),  # Long after
            # New behavior (based on start_date + expiry < shopping_list.end_date)
            ("carrot", 7, 0, True),
            ("tomato", 7, 6, True),
            ("potato", 8, 0, False),
            ("rice",   8, 6, False),
        ]
        for name, type_expiry, delay, warning in data:
            self._add_food(name, type_expiry, None, False)
            self._create_shopping_list(delay)
            self._check_item_expiry(type_expiry, warning, self.DAY_DATE + timedelta(type_expiry - delay))

    def test_food_expiry(self):
        data = [
            # Name, food_expiry, delay, warning
            ("saumon", 2, 0, True),  # In time
            ("truite", 2, 6, True),  # Last minute
            # Old behavior (based on expiry < delay)
            ("crabe",  1, 1, True),  # Tomorrow
            ("huitre", 1, 4, True),  # Long after
            # New behavior (based on start_date + expiry < shopping_list.end_date)
            ("carrot", 7, 0, True),
            ("tomato", 7, 6, True),
            ("potato", 8, 0, False),
            ("rice",   8, 6, False),
        ]
        for name, food_expiry, delay, warning in data:
            self._add_food(name, None, food_expiry, False)
            self._create_shopping_list(delay)
            self._check_item_expiry(food_expiry, warning, self.DAY_DATE + timedelta(food_expiry - delay))

    def test_override_expiry(self):
        data = [
            # Name, type_expiry, food_expiry, delay, warning
            ("saumon", 4, 5, 0, True),  # Food > type
            ("truite", 6, 3, 0, True),  # Type > Food
            # Old behavior (based on expiry < delay)
            ("crabe",  1, 5, 2, True),  # Type expired, Food OK
            ("huitre", 5, 1, 2, True),  # Type OK, Food expired
            # New behavior (based on start_date + expiry < shopping_list.end_date)
            ("potato", 1, 8, 2, False), # Type expired, Food OK
            ("tomato", 8, 1, 2, True),  # Type OK, Food expired
        ]
        for name, type_expiry, food_expiry, delay, warning in data:
            # Dans les temps
            self._add_food(name, type_expiry, food_expiry, False)
            self._create_shopping_list(delay)
            self._check_item_expiry(food_expiry, warning, self.DAY_DATE + timedelta(food_expiry - delay))

    def test_non_fresh_raw_states(self):
        self.raw_state = self.create_db_raw_state("pas frais !")
        data = [
            # Name, type_expiry, food_expiry, delay, warning
            ("saumon d'Ordralfabétix", 4, 4, 0, False), # In time
            ("truite d'Ordralfabétix", 4, 4, 3, False), # Last minute
            ("crabe d'Ordralfabétix",  4, 4, 4, False), # Tomorrow
            ("huitre d'Ordralfabétix", 4, 4, 7, False), # At end_date
        ]
        for name, type_expiry, food_expiry, delay, warning in data:
            self._add_food(name, type_expiry, food_expiry, False)
            self._create_shopping_list(delay)
            self._check_item_expiry(None, warning, None)

    def test_usually_stored(self):
        data = [
            # Name, type_expiry, food_expiry, delay, warning
            ("potion de Panoramix",  4, 4, 0, False), # In time
            ("marmite de Panoramix", 4, 4, 3, False), # Last minute
            ("cerpe de Panoramix",   4, 4, 4, False), # Tomorrow
            ("louche de Panoramix",  4, 4, 7, False), # At end_date
        ]
        for name, type_expiry, food_expiry, delay, warning in data:
            self._add_food(name, type_expiry, food_expiry, True)
            self._create_shopping_list(delay)
            self._check_item_expiry(None, warning, None)
