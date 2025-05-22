
from shopping_mgr.controller    import fill_shopping_list

from common.test                import TestAPIWithLogin

from recipe_mgr.models          import RawState

from datetime                   import date, timedelta

import json

class TestOrder(TestAPIWithLogin):
    
    LIST_DATE       = date(2015, 2, 12)
    NB_LIST_DAYS    = 7
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        
        # Init raw states
        self.assertEqual(RawState.objects.count(), 1)
        self.raw_state = { "frais": RawState.objects.get(name="frais") }
        for s in ("en conserve", "surgelé"):
            self.raw_state[s] = RawState.objects.create(name=s)
        
        # Init shopping categories
        self.categories = dict()
        for name, order in [ ("Fruits", 4), ("Légumes", 2), ("Autre", 1), ("Conserves", 6), ("Surgelés", 5), ("Herbes", 7), ("Sauces", 8) ]:
            self.categories[name] = self.create_db_shopping_category(name, order)
        
        # Creating list
        start_date = self.LIST_DATE
        end_date = self.LIST_DATE + timedelta(self.NB_LIST_DAYS)
        self.shopping_list = self.create_db_shopping_list(start_date=start_date, end_date=end_date)

    def _fill_shopping_list(self, nb_items_expected):
        fill_shopping_list(self.shopping_list)
        self.assertEqual(self.shopping_list.items.count(), nb_items_expected)

    def _check_list_order(self, itemCategories):
        response = self.client.get('/api/user/%i/shopping_list/%i' % (self.user.id, self.shopping_list.id))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(c['food_type'] for c in response.data['content']), list(c[0] for c in itemCategories))
        for category, expected in zip(response.data['content'], itemCategories):
            print("expected", expected)
            print("category", category)
            expected_name, missings, expected_items = expected
            self.assertEqual(category['food_type'], expected_name)
            self.assertEqual(category['missing_items'], missings)
            self.assertEqual(list(item['food']['name'] for item in category['items']), expected_items)

    def _create_item(self, name, raw_state_str, shopping_category_str, got_it = False, custom = False):
        if custom:
            food = None
            forced_name = name
        else:
            forced_name = None
            food = self.create_db_food(name, shopping_category=self.categories[shopping_category_str], with_conversion = True)
        self.create_db_shopping_item(self.shopping_list, food=food, raw_state=self.raw_state[raw_state_str], grams=42, got_it=got_it, custom=custom, forced_name=forced_name)

    def test_category(self):
        # Frais
        self._create_item("tomate",         "frais",        "Fruits")
        self._create_item("banane",         "frais",        "Fruits")
        # Non frais
        self._create_item("tomate",         "en conserve",  "Fruits")
        self._create_item("banane",         "surgelé",      "Fruits")
        self._create_item("frites",         "surgelé",      "Légumes")
        self._create_item("haricots",       "en conserve",  "Légumes")
        # Customs
        self._create_item("salade verte",   "frais",        "Fruits",   custom=True)
        self._create_item("salade jaune",   "frais",        "Fruits",   custom=True)
        self._create_item("salade blanche", "frais",        "Fruits",   custom=True)
        # Got_it
        self._create_item("ananas",         "frais",        "Fruits",   got_it=True)
        self._create_item("betterave",      "en conserve",  "Légumes",  got_it=True)
        self._create_item("annette",        "surgelé",      "Herbes",   got_it=True)
        self._create_item("tartare",        "frais",        "Sauces",   got_it=True)
        self._create_item("bolognese",      "frais",        "Sauces",   got_it=True)
        # Got_it + custom
        self._create_item("salade violette","frais",        "Fruits",   got_it=True, custom=True)
        self._create_item("salade mauve",   "frais",        "Fruits",   got_it=True, custom=True)
        # Results
        self._fill_shopping_list(16)
        """
        Expected categories order:
        - According to their list_order
        - Automatic categories added: Autre, Conserves, Surgelés
        - Only if not empty
        
        Expected item order:
        - First the missing items (!got_it), then the missing ones
        - In each case, alphabetically ordered
        """
        self._check_list_order([
            # category_name, missings, items
            ("Autre", 3, ["salade blanche", "salade jaune", "salade verte", "salade mauve", "salade violette"]),
            ("Fruits", 2, ["banane", "tomate", "ananas"]),
            ("Surgelés", 2, ["banane", "frites", "annette"]),
            ("Conserves", 2, ["haricots", "tomate", "betterave"]),
            # "Herbes" not present because empty !
            ("Sauces", 0, ["bolognese", "tartare"]),
        ])
