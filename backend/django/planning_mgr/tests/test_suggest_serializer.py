from common.test                import TestAPIWithLogin
from planning_mgr.models        import DishRecipe
from planning_mgr.serializers   import DaySuggestionSerializer, DayToFillSerializer
import datetime
import pprint

class TestSuggestionSerializers(TestAPIWithLogin):
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        self.init_default_nutrients()
        super().setUp()
        self.init_db_profile_eater()
        self.create_db_meta_planning()

        self.meal_type = self.create_db_mealtype("mymealtype")
        # AGG = 1 + 2
        self.dish_typeagg, self.dish_type1, self.dish_type2 = self.create_db_dishtype_aggregated()
        self.dish_type3 = self.create_db_dishtype()

        self.day = self.create_db_day()
        self.lunch = self.create_db_mealslot(self.day, time=datetime.time(12, 0), meal_type=self.meal_type)
        self.dish_lunch_1 = self.create_db_dish(self.lunch, self.dish_type1, order=1)
        self.dish_lunch_2 = self.create_db_dish(self.lunch, self.dish_type2, order=2)

        self.breakfast = self.create_db_mealslot(self.day, time=datetime.time(6, 0), meal_type=self.meal_type)
        self.dish_morning = self.create_db_dish(self.breakfast, self.dish_typeagg, order=1)
        self.dish_morning_validated = self.create_db_dish(self.breakfast, self.dish_type3, order=1)

        self.recipe1 = self.create_db_recipe(dish_types=[self.dish_type1])
        self.recipe2 = self.create_db_recipe(dish_types=[self.dish_type2])
        self.recipe3 = self.create_db_recipe(dish_types=[self.dish_typeagg])
        self.recipe4 = self.create_db_recipe(dish_types=[self.dish_type3])
        

    def test_suggest_serializer(self):

        self.create_db_dishrecipe(self.dish_lunch_1, self.recipe1)
        self.create_db_dishrecipe(self.dish_lunch_2, self.recipe2)
        self.create_db_dishrecipe(self.dish_morning_validated, self.recipe4, validated=True)
        self.create_db_dishrecipe(self.dish_morning, self.recipe3)

        res = DaySuggestionSerializer.serialize(self.day)
        print(res)
        self.assertEqual(res, {"suggestions": [{"dish_id": self.dish_morning.id, "meal_id": self.breakfast.id,
                                                "dish_type_id": self.dish_typeagg.id,
                                                "recipe_id": self.recipe3.id, "ratio": 1,
                                                'fully_filtered': True},
                                                {"dish_id": self.dish_lunch_1.id, "meal_id": self.lunch.id,
                                                "dish_type_id": self.dish_type1.id,
                                                "recipe_id": self.recipe1.id, "ratio": 1,
                                                'fully_filtered': True},
                                                {"dish_id": self.dish_lunch_2.id, "meal_id": self.lunch.id,
                                                "dish_type_id": self.dish_type2.id,
                                                "recipe_id": self.recipe2.id, "ratio": 1,
                                                'fully_filtered': True}
                                                ],
                                  'nb_planned_days': 0,
                                  'metaplanning_changed': False,
                                  'shopping_list_id': None,
                                  'skipped': False,
                                  'validated': False
                                                })

    def test_day_to_fill_serializer_empty(self):

        response = self.client.get('/api/user/%i/day_to_fill/%s' % (self.user.id, self.day.date))
        self.assertEqual(response.data['has_forced_recipes'], False)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(response.data)
        self.assertEqual(response.data['content'], [{'meal_slot':
                                    {'eating': [self.eaters[0].id],
                                     'eaten_at_home': True,
                                     'cooked_at_home': True,
                                    'meal_type': {'id': self.meal_type.id, 'name': 'mymealtype'},
                                    'meal_place': {'id': self.places["home"].id, 'key': 'home'},
                                    'speed': 2,
                                    'id': self.breakfast.id},
                                'status': 'suggested',
                                'dishes': [{'id': self.dish_morning.id,                'recipes': [], 'activated': True,
                                            'main_dish_type_id': self.dish_typeagg.id, 'dish_type_ids': [self.dish_type1.id, self.dish_type2.id],
                                            'has_validated_recipes': False},
                                            {'id': self.dish_morning_validated.id,      'recipes': [], 'activated': True,
                                            'main_dish_type_id': self.dish_type3.id,   'dish_type_ids': [self.dish_type3.id],
                                            'has_validated_recipes': False}]},
                         {'meal_slot':
                             {'eating': [self.eaters[0].id],
                              'eaten_at_home': True,
                              'cooked_at_home': True,
                             'meal_type': {'id': self.meal_type.id, 'name': 'mymealtype'},
                             'meal_place': {'id': self.places["home"].id, 'key': 'home'},
                             'speed': 2,
                             'id': self.lunch.id},
                          'status': 'suggested',
                          'dishes': [{'id': self.dish_lunch_1.id,              'recipes': [], 'activated': True,
                                    'main_dish_type_id': self.dish_type1.id, 'dish_type_ids': [self.dish_type1.id],
                                    'has_validated_recipes': False},
                                {'id': self.dish_lunch_2.id,              'recipes': [], 'activated': True,
                                    'main_dish_type_id': self.dish_type2.id, 'dish_type_ids': [self.dish_type2.id],
                                    'has_validated_recipes': False}]}])


    def test_day_to_fill_serializer_fill_with_aggregated(self):
        """
        Test that when setting a recipe to a dish with an aggregated dishtype, it correctly
        returns it
        """
        self.create_db_dishrecipe(self.dish_lunch_1, self.recipe1)
        self.create_db_dishrecipe(self.dish_lunch_2, self.recipe2)
        self.create_db_dishrecipe(self.dish_morning_validated, self.recipe4, validated=True)
        self.create_db_dishrecipe(self.dish_morning, self.recipe3, validated=True)
        response = self.client.get('/api/user/%i/day_to_fill/%s' % (self.user.id, self.day.date))
        res = response.data
        print(res)
        self.assertEqual(res['content'][0]['dishes'][0]['recipes'],
                            [{'id': self.recipe3.id, 'name': self.recipe3.name, 'ratio': 1.0, 'photo': None,
                              'url_key': self.recipe3.url_key, 'validated': True,
                              'avg_rating': None, 'nb_ratings': 0,
                              'calories': 0, 'difficulty': 1, 'in_shopping_list': True,
                              'price': 1}])
        self.assertEqual(res['content'][0]['dishes'][0]['dish_type_ids'],
                            [self.dish_typeagg.id])


    def test_day_to_fill_serializer_fill_with_part_of_aggregated(self):
        """
        Test than when setting a recipe to a dish with a part of an aggregated dishtype, it correctly
        returns it
        """
        self.create_db_dishrecipe(self.dish_lunch_1, self.recipe1)
        self.create_db_dishrecipe(self.dish_lunch_2, self.recipe2)
        self.create_db_dishrecipe(self.dish_morning_validated, self.recipe4, validated=True)
        self.create_db_dishrecipe(self.dish_morning, self.recipe1, validated=True)
        response = self.client.get('/api/user/%i/day_to_fill/%s' % (self.user.id, self.day.date))
        res = response.data
        print(res)
        self.assertEqual(res['content'][0]['dishes'][0]['recipes'],
                            [{'id': self.recipe1.id, 'name': self.recipe1.name, 'ratio': 1.0,
                              'url_key': self.recipe1.url_key, 'photo': None, 'validated': True,
                              'avg_rating': None, 'nb_ratings': 0,
                              'calories': 0, 'difficulty': 1, 'in_shopping_list': True,
                              'price': 1}])
        self.assertEqual(res['content'][0]['dishes'][0]['dish_type_ids'],
                            [self.dish_type1.id, self.dish_type2.id])
