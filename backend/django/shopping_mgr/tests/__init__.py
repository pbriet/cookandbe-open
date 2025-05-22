from common.test                import TestAPIWithLogin

from shopping_mgr.controller    import fill_shopping_list

import datetime

class TestBaseShoppingListTest(TestAPIWithLogin):
    """
    Test the controller function that generates a shopping list
    """
    WITH_LIST = True
    FILL_LIST = True
    WITH_FOOD_TYPES = True

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.shopping_list = None
    
    def _init_default_conversion(self, food):
        return self.create_db_food_conversion(food, value=1)

    def setUp(self):
        super().setUp()
        self.create_db_profile()
        self.init_default_ingredient_settings()
        dish_type = self.create_db_dishtype()
        
        self.meal_type = self.create_db_mealtype()
        
        self.day1 = self.create_db_day(date="2014-07-08", skipped=False)
        self.day2 = self.create_db_day(date="2014-07-11", skipped=False)
        
        for other_date in ("2014-07-07", "2014-07-09", "2014-07-10"):
            self.create_db_day(date=other_date, skipped=None)
            
        self.meal_slot1 = self.create_db_mealslot(self.day1, meal_type=self.meal_type)
        dish1 = self.create_db_dish(self.meal_slot1, dish_type)
        self.meal_slot2 = self.create_db_mealslot(self.day2, meal_type=self.meal_type)
        dish2 = self.create_db_dish(self.meal_slot2, dish_type)
        
        non_fresh_food_type = self.create_db_foodtype("non-fresh", usually_stored=True)
        if not self.WITH_FOOD_TYPES:
            non_fresh_food_type = None

        self.carrots = self.create_db_food("carrots")
        self.chocolate = self.create_db_food("chocolate", food_type=non_fresh_food_type)
        self.things = self.create_db_food("thing")

        self.default_carrot_conversion = self._init_default_conversion(self.carrots)
        self.default_choco_conversion = self._init_default_conversion(self.chocolate)
        self.default_thing_conversion = self._init_default_conversion(self.things)

        self.chocolate_chunk_cnv = self.create_db_food_conversion(self.chocolate, "chunk", 10, plural="chunks")
        self.small_carrot_cnv = self.create_db_food_conversion(self.carrots, "small", 100)
        self.big_carrot_cnv = self.create_db_food_conversion(self.carrots, "big", 200)
        
        self.thing_cnv = self.create_db_food_conversion(self.things, "thing", 50)

        self.recipe1 = self.create_db_recipe(dish_types=[dish_type])
        self.recipe2 = self.create_db_recipe(dish_types=[dish_type])

        # Recipe 1 is 2 big carrots and 1 chocolate chunk  (RATIO=2)
        self.ing1_1 = self.create_db_ingredient(self.recipe1, self.carrots, 400, default_conversion=self.default_carrot_conversion)
        self.ing1_2 = self.create_db_ingredient(self.recipe1, self.chocolate, 10, default_conversion=self.default_choco_conversion)

        # Recipe 2 is 1 small carrot, 5 chocolate chunks and half a thing (RATIO=1)
        self.ing2_1 = self.create_db_ingredient(self.recipe2, self.carrots, 100, default_conversion=self.default_carrot_conversion)
        self.ing2_2 = self.create_db_ingredient(self.recipe2, self.chocolate, 50, default_conversion=self.default_choco_conversion)
        self.ing2_3 = self.create_db_ingredient(self.recipe2, self.things, 25, default_conversion=self.default_thing_conversion)

        self.dr1 = self.create_db_dishrecipe(dish1, self.recipe1, ratio=2, validated=True)
        self.dr2 = self.create_db_dishrecipe(dish2, self.recipe2, ratio=1, validated=True)
        
        if self.WITH_LIST:
            self._create_shopping_list(self.FILL_LIST)

    def _create_shopping_list(self, fill_list = True):
        if self.shopping_list:
            self.shopping_list.delete()
        self.shopping_list = self.create_db_shopping_list(start_date="2014-07-08", end_date="2014-07-11")
        if fill_list:
            fill_shopping_list(self.shopping_list)

    def check_shopping_list(self, response_data_content):
        
        self.assertEqual(len(response_data_content), 1)
        content = response_data_content[0]
        self.assertEqual(content['food_type'], 'shopping_category_x')
        self.assertEqual(content['missing_items'], 2)
        
        self.assertEqual(len(content['items']), 3)
        items = content['items']
        
        self.assertEqual(items[0]['food']['id'], self.carrots.id)
        self.assertEqual(items[0]['food']['name'], 'carrots')
        self.assertEqual(items[0]['got_it'], False)
        self.assertEqual(items[0]['conversion']['id'], self.small_carrot_cnv.id)
        self.assertEqual(items[0]['conversion']['unit'], 'small')
        self.assertEqual(items[0]['conversion']['value'], 9)
        self.assertEqual(items[0]['conversion']['html_value'], "9")
        self.assertEqual(items[0]['basic_conversion'], {
            'id': self.default_carrot_conversion.id,
            'basic': True,
            'loss': 0.0,
            'score': 0.64,
            'value': 900,
            'unit': 'g',
            'html_value': '900',
            'grams': 900.0,
        })
        self.assertEqual(items[0]['recipes'], [
            {
                'meal': self.meal_type.name,
                'quantity': 800, # 400 * 2.0
                'date': datetime.date(2014, 7, 8),
                'photo': None,
                'name': 'my recipe',
                'id': self.recipe1.id,
            }, {
                'meal': self.meal_type.name,
                'quantity': 100,
                'date': datetime.date(2014, 7, 11),
                'photo': None,
                'name': 'my recipe',
                'id': self.recipe2.id,
            },
        ])
        
        self.assertEqual(items[1]['food']['id'], self.things.id)
        self.assertEqual(items[1]['food']['name'], 'thing')
        self.assertEqual(items[1]['got_it'], False)
        self.assertEqual(items[1]['conversion']['id'], self.thing_cnv.id)
        self.assertEqual(items[1]['conversion']['unit'], 'thing')
        self.assertEqual(items[1]['conversion']['value'], 0.5)
        self.assertEqual(items[1]['conversion']['html_value'], "&frac12;")
        self.assertEqual(items[1]['basic_conversion'], {
            'score': 0.46,
            'value': 25,
            'basic': True,
            'html_value': '25',
            'grams': 25.0,
            'unit': 'g',
            'id': self.default_thing_conversion.id,
            'loss': 0.0,
        })
        self.assertEqual(items[1]['recipes'], [
            {
                'date': datetime.date(2014, 7, 11),
                'meal': self.meal_type.name,
                'photo': None,
                'id': self.recipe2.id,
                'name': 'my recipe',
                'quantity': 25,
            }
        ])
        
        self.assertEqual(items[2]['food']['id'], self.chocolate.id)
        self.assertEqual(items[2]['food']['name'], 'chocolate')
        self.assertEqual(items[2]['got_it'], True)
        self.assertEqual(items[2]['conversion']['id'], self.chocolate_chunk_cnv.id)
        self.assertEqual(items[2]['conversion']['unit'], 'chunks')
        self.assertEqual(items[2]['conversion']['value'], 7)
        self.assertEqual(items[2]['conversion']['html_value'], "7")
        self.assertEqual(items[2]['basic_conversion'], {
            'score': 0.51,
            'value': 70,
            'basic': True,
            'html_value': '70',
            'unit': 'g',
            'grams': 70.0,
            'id': self.default_choco_conversion.id,
            'loss': 0.0,
        })
        self.assertEqual(items[2]['recipes'], [
            {
                'id': self.recipe1.id,
                'meal': self.meal_type.name,
                'date': datetime.date(2014, 7, 8),
                'photo': None,
                'quantity': 20,
                'name': 'my recipe',
            }, {
                'id': self.recipe2.id,
                'meal': self.meal_type.name,
                'date': datetime.date(2014, 7, 11),
                'photo': None,
                'quantity': 50,
                'name': 'my recipe',
            }
        ])

