from common.test                        import TestAPIWithLogin

from planning_mgr.controller.planning   import build_planning

from planning_mgr.tests                 import TestWithFilledPlanning

import datetime

class TestMealSlotSerializer(TestAPIWithLogin, TestWithFilledPlanning):

    def setUp(self):
        super().setUp()
        self.meta = self.create_db_meta_planning(with_n_days=1)
        self.init_day(self.meta.sorted_days[0])

    def test_meal_slot_serializer(self):

        response = self.client.get('/api/meal_slot/%i' % self.meal_slot1.id)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data,
           {'meal_type': 'Midi', 'dishes': [{'recipes': [{'name': 'recipe1', 'id': self.recipe1.id, 'ratio': 2.0}],
                                             'dish_type_ids': [self.dish_type.id],
                                             'id': self.dish1.id}],
            'id': self.meal_slot1.id})

        response = self.client.get('/api/meal_slot/%i' % self.meal_slot2.id)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data,
           {'meal_type': 'Soir', 'dishes': [{'recipes': [{'name': 'recipe3', 'id': self.recipe3.id, 'ratio': 1.0},
                                                         {'name': 'Canard à l\'orange', 'id': self.recipe2.id, 'ratio': 1.0}],
                                             'dish_type_ids': [self.dish_type.id],
                                             'id': self.dish2_1.id}],
            'id': self.meal_slot2.id})


class TestMealSlotStructure(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        # Default metaplanning
        self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.reload_user()
        
        # Creating a default monday
        self.day = build_planning(self.user, datetime.date(2014, 9, 1), 1)[0]
        
        
    def test_get_meal_slot_structure(self):
        response = self.client.get('/api/user/%i/day/2014-09-01/structure' % self.user.id)
        self.assertEqual(response.status_code, 200)
        
        content = response.data['structure']
        
        self.assertEqual(sorted(content[0].keys()),
                         ['eater_ids', 'meal_place', 'meal_slot_id', 'meal_type', 'speed', 'suggest'])
        
        summary_data = []
        for row in content:
            summary_data.append((row['meal_type']['name'], row['meal_place']['key']))
        
        self.assertEqual(summary_data, [
                            ('Petit déjeuner', 'home'),
                            ('Collation', 'donoteat'),
                            ('Déjeuner', 'home'),
                            ('Goûter', 'donoteat'),
                            ('Dîner', 'home')])
        