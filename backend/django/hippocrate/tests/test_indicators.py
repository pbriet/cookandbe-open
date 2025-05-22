
from common.mock_tools                  import fake_ratios_decorator, fake_today_decorator
from common.test                        import TestAPIWithLogin

from diet_mgr.models                    import Diet

from hippocrate.models.recipe           import RecipeNutrientCalculator
from hippocrate.models.constraints      import NutrientConstraint

from mock                               import patch

from nutrient.models                    import Nutrient

from optalim.config                     import Config
import optalim.mongo

import datetime

def fake_compute_nutrients(obj, *args, **kargs):
    obj.aggregated_nutrients = { 10 : 15 }
    obj.nutrients_data_availability = { 10 : 1. }
    return obj

class FakeMongoHpTable(object):

    def __init__(self):
        self.values = []

        self.update_args = []
        self.find_args = []

        self.MONGO_ID = 1


    def update_one(self, where, set_query, **kargs):
        value = set_query["$set"]
        # Adding the '_id' attribute
        value['_id'] = self.MONGO_ID
        self.MONGO_ID += 1
        self.values.append(value)
        print("--->", self.values)
        self.update_args.append((where, value))

    def find_one(self, query):
        self.find_args.append((query,))

        assert 'planning_id' in query
        for value in self.values:
            if value['planning_id'] == query['planning_id']:
                return value
        return None

class TestPlanningIndicators(TestAPIWithLogin):
    def fake_diet_handler(self, *args, **kargs):
        class FakeDietHandler(object):
            def filters(*args):             return []
            def validate_constraint(cst):   return cst
            def build_nutrient_constraints(*args):
                return [NutrientConstraint(Nutrient.objects.get(pk=10), 20, 40,
                                            cost_per_percent_out=110, daily_tolerance_min=0.1,  daily_tolerance_max=0)]
        return FakeDietHandler

    @patch.object(RecipeNutrientCalculator, 'compute', fake_compute_nutrients)
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.init_default_nutrients()
        # We create a planning with one dish,
        # And store one recipe into it
        dish_type = self.create_db_dishtype("Plat complet") # Unicity will be applied
        self.init_db_profile_eater()

        # Theses future days should not disturb (but were, in the past!)
        planning = self.create_db_planning(start_date=datetime.date(2014, 4, 10))
        future_days = planning.sorted_days
        planning = self.create_db_planning(start_date = datetime.date(2014, 3, 3))
        self.days = planning.sorted_days

        dishes = []
        for i in range(7):
            meal_slot = self.create_db_mealslot(self.days[i])
            dishes.append(self.create_db_dish(meal_slot, dish_type))

        self.vitamineb1 = self.create_db_nutrient("vitamineb1", short_name="vitamineb1", id=10)

        recipe = self.create_db_recipe(dish_types=[dish_type])

        for i, dish in enumerate(dishes):
            # We set the same recipe every day  (one dish per day)
            self.create_db_dishrecipe(dish, recipe, validated=i < 3) # The 3 first days are completed

        self.init_recipe_index([self.vitamineb1.id])

    @fake_ratios_decorator(1)
    def _get_indicators(self, date, nutrient_id=None, day_week_indicators=False):
        with patch.object(Diet, '_handlers', {'balanced': self.fake_diet_handler}):
            if day_week_indicators:
                response = self.client.get('/api/user/%s/day/%s/indicators' % (self.user.id, date))
            elif nutrient_id is not None:
                response = self.client.get('/api/user/%s/indicators/%s/%i' % (self.user.id, date, nutrient_id))
            else:
                response = self.client.get('/api/user/%s/indicators/%s' % (self.user.id, date))
            self.assertEqual(response.status_code, 200)
        return response

    def test_indicators(self):
        response = self._get_indicators(self.days[0].date)
        print(response.data)
        self.assertEqual(response.data['total_cost'], 254260) # 248260 + 6000
        self.assertEqual(len(response.data['constraints']), 8)
        elts = sorted(response.data['constraints'], key=lambda x: (x['cost'], x['key']))

        self.assertEqual(elts[0]['cost'], 0)
        self.assertEqual(elts[0]['key'], 'budget')

        self.assertEqual(elts[1]['cost'], 0)
        self.assertEqual(elts[1]['key'], 'food_tag_unicity')

        self.assertEqual(elts[2]['cost'], 0)
        self.assertEqual(elts[2]['key'], 'meal_balance')

        self.assertEqual(elts[4]['cost'], 0)
        self.assertEqual(elts[4]['key'], 'shopping')

        self.assertEqual(elts[5]['cost'], 0)
        self.assertEqual(elts[5]['key'], 'time')

        self.assertEqual(elts[6]['cost'], 6000)
        self.assertEqual(elts[6]['key'], 'unicity')
        # 15g per day vs 20g min (weekly -- ie 25% out) //  vs 18g min (daily  -- ie 16.6% out)
        # 25% off * 25 (square) * 55 penalty * 1 week   +  16.6% off * 16.6 * 110 penalty * 7 days
        # 25 * 25 * 55 + 16.6666 * 16.6666 * 110 * 7  ~= 248260
        self.assertEqual(elts[7]['cost'], 248260)
        self.assertEqual(elts[7]['key'], 'vitamineb1')

        # Getting details on vitamineb1
        response = self._get_indicators(self.days[0].date, elts[7]['id'])
        self.assertEqual(response.data['other_infos']['min'], 20.0)
        self.assertEqual(response.data['other_infos']['unit'], 'mg')


    def _test_day_week_indicators(self, date):
        fake_hp_table = FakeMongoHpTable()
        with patch.object(optalim.mongo.Mongo, 'hp_table', lambda x: fake_hp_table):
            response = self._get_indicators(date, day_week_indicators=True)
            self.assertEqual(response.status_code, 200)
        return response.data['content']


    @fake_today_decorator(2014, 3, 5) # 3rd day
    def test_day_week_indicators(self):
        data = self._test_day_week_indicators(self.days[2].date)
        self.assertEqual(sorted(data['nutrients'].keys()), ['disabled_ko', 'disabled_ok', 'ko', 'ok'])

        self.assertEqual(data['nutrients']['ko']['vitamineb1']['daily'],
                            {'percent_min': 83,
                            'flag': 'ko',
                            'name': 'vitamineb1',
                            'nutrient_key': 'vitamineb1',
                            'min': 18.0,
                            'middle_value': 29.0,
                            'max': 40.0,
                            'unit': 'mg',
                            'percent_max': 38,
                            'percent_diff': 17,
                            'str_value': 15,
                            'cost': 30555,
                            'value': 15.0})

        self.assertEqual(data['nutrients']['ko']['vitamineb1']['weekly'],
                            {'percent_min': 75,
                            'flag': 'ko',
                            'name': 'vitamineb1',
                            'nutrient_key': 'vitamineb1',
                            'min': 20.0,
                            'middle_value': 30.0,
                            'max': 40.0,
                            'unit': 'mg',
                            'percent_max': 38,
                            'percent_diff': 25,
                            'str_value': 15,
                            'cost': 34375,
                            'value': 15.0})

        self.assertEqual(data['nutrients']['ko']['vitamineb1']['cost'], 248260)


    @fake_today_decorator(2014, 3, 5) # 3rd day
    def test_should_work_with_default_weight_height(self):
        """
        Simply test that it doesn't crash with empty height/weight
        """
        self.profiles[0].weight = self.profiles[0].height = None
        self.profiles[0].save()

        data = self._test_day_week_indicators(self.days[2].date)
