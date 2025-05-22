
from common.test                import TestAPIWithLogin
from common.date                import get_tomorrow, get_yesterday, add_days, today

import datetime

class TestShoppingListHistory(TestAPIWithLogin):

    def _check_history(self, expected_data):
        
        response = self.client.get('/api/user/%i/shopping_list/history' % self.user.id)
        self.assertEqual(response.status_code, 200)
        
        shopping_lists = response.data['lists']
        self.assertEqual(len(shopping_lists), len(expected_data))
        
        for shopping_list, data in zip(shopping_lists, expected_data):
            self.assertEqual(shopping_list['start_date'], data[0])
            self.assertEqual(shopping_list['end_date'], data[1])
            self.assertEqual(shopping_list['nb_items'], data[2])

    def test_shopping_history(self):
        bar = self.create_db_raw_state("bar")
        black_chocolate = self.create_db_food("black chocolate")
        white_chocolate = self.create_db_food("white chocolate")
        
        # No history
        self._check_history([])

        # History with one list
        self.create_db_shopping_list(datetime.date(2012, 5, 4), datetime.date(2012, 5, 10))
        
        self._check_history([("2012-05-04", "2012-05-10", 0)])
        
        # History with 3 lists
        # A most recent one
        self.create_db_shopping_list(datetime.date(2012, 8, 10), datetime.date(2012, 9, 2))
        # And one older with items
        last_list = self.create_db_shopping_list(datetime.date(2011, 12, 1), datetime.date(2011, 12, 8))
        self.create_db_shopping_item(last_list, black_chocolate, raw_state = bar, grams = 100)
        self.create_db_shopping_item(last_list, black_chocolate, raw_state = bar, grams = 200)
        self.create_db_shopping_item(last_list, white_chocolate, raw_state = bar, grams = 10)
        
        self._check_history([
                ("2012-08-10", "2012-09-02", 0),
                ("2012-05-04", "2012-05-10", 0),
                ("2011-12-01", "2011-12-08", 3),
            ],
        )
