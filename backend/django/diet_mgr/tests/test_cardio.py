from common.test                import TestAPIWithLogin
from common.mock_tools          import fake_today_decorator, FakeNow

from mock                       import patch, call

from diet_mgr.models                import Diet

from hippocrate.models.constraints  import NutrientBalanceConstraint, NutrientMealTypeConstraint
from hippocrate.models.recipestorage import MainRecipeStorage

from planning_mgr.models            import MealType

import optalim.config
import datetime
import json

class TestSubscribeToCardio(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.create_db_meta_planning()
        self.cardio = self.create_db_diet("cardiovascular")
        self.profile = self.create_db_profile(height=165, weight=60)

    def _subscribe_to(self, **parameters):
        post_kargs = {'parameters': json.dumps(parameters)}
        return self.client.post('/api/user/%i/subscribe_to_diet/%i' % (self.user.id, self.cardio.id), post_kargs)

    def test_success_subscription(self):
        for i in range(4):
            res = self._subscribe_to(normolipidic = (i == 0), hyposodic = (i == 1), low_trigly = (i == 2), controlled_k = (i == 3))
            self.assertEqual(res.data['status'], 'success')

class TestCardioDiet(TestAPIWithLogin):
    SEX = "male"
    SCORE = 6
    WEIGHT = 65
    HEIGHT = 165
    METABOLISM = 1.2
    BIRTHDATE = datetime.datetime(1985, 1, 13)
    NORMOLIPIDIC = 0
    HYPOSODIC = 0
    LOW_TRIGLY = 0
    CONTROLLED_K = 0
    FAKE_ANC = dict()
    REQUIRED_NUTRIENTS = tuple()

    def setUp(self):
        super().setUp()
        self.planning = self.create_db_planning()
        for nutrient in self.REQUIRED_NUTRIENTS:
            self.create_db_nutrient(name=nutrient, key=nutrient)
        MainRecipeStorage.init_indexer()
        self.cardio = self.create_db_diet("cardiovascular")
        with FakeNow(2010, 1, 1):
            self.assign_diet_user(
                self.user,
                self.cardio,
                normolipidic = self.NORMOLIPIDIC,
                hyposodic = self.HYPOSODIC,
                low_trigly = self.LOW_TRIGLY,
                controlled_k = self.CONTROLLED_K,
            )

        self.profile = self.create_db_profile(
            weight = self.WEIGHT,
            height = self.HEIGHT,
            birth_date = self.BIRTHDATE,
            sex = self.SEX,
            work_score = self.SCORE,
            metabolism = self.METABOLISM,
        )

    @patch('diet_mgr.handlers.anc.AncStandardDiet._load_nutrient_constraint')
    @fake_today_decorator(2010, 3, 1)
    def _test_diet(self, mock_load_constraint):
        with patch.object(optalim.config.Config, 'anc', {
            'profile1': {
                'min_age': 23,
                'max_age': 30,
                'sex': 'male',
                'nutrients': self.FAKE_ANC,
            }
        }):
            ctrs = self.cardio.handler(self.profile).build_nutrient_constraints(self.planning)
            for i, result in enumerate(mock_load_constraint.mock_calls):
                print("result  ", result.call_list())
                print("expected", self.EXPECTED[i].call_list())
                self.assertEqual(result, self.EXPECTED[i])
        return ctrs

class TestNormolipidicCardioDiet(TestCardioDiet):
    NORMOLIPIDIC = 1
    WEIGHT = 65
    EXPECTED_CALORIES = 3102
    REQUIRED_NUTRIENTS = "omega3", "omega6"
    FAKE_ANC = {
        # 'proteins_per_kg':          {'key': 'proteins_per_kg',          'min': 0.8},
        'lipids_saturated':         {'key': 'lipids_saturated',                     'max': 12,  'daily_tolerance': 20},
        'lipids_monoinsaturated':   {'key': 'lipids_monoinsaturated',   'min': 15,  'max': 20,  'daily_tolerance': 50},
        'omega6':                   {'key': 'omega6',                   'min': 4,               'daily_tolerance': 20},
    }
    EXPECTED = [
        call({'key': 'cholesterol', 'name': 'cholesterol', 'unit': 'mg', 'max': 300, 'daily_tolerance': 0, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'lipids_monoinsaturated', 'min': 17,'max': 20, 'daily_tolerance': 50, 'mode': 'percentage_energy', 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'lipids_saturated', 'min': 8,'max': 10, 'daily_tolerance': 20, 'mode': 'percentage_energy', 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        # call({'key': 'omega3', 'unit': 'g', 'name': 'omega3', 'min': 1.75, 'max': 2, 'daily_tolerance': 20, 'mode': 'percentage_energy', 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        # call({'key': 'omega6', 'min': 6,'max': 8, 'daily_tolerance': 20, 'cost': 50, 'name': 'acides gras polyinsaturés, 18:2 c,c n-6, linoléique, octadécadiénoïque', 'mode': 'percentage_energy', 'unit': 'g'}, EXPECTED_CALORIES, WEIGHT),
        # call({'key': 'proteins_per_kg', 'min': 1.2, 'max': 1.4, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
    ]

    def test_diet(self):
        ctrs = self._test_diet()
        self.assertEqual(len(ctrs), 4)

class TestCoagulationCardioDiet(TestCardioDiet):
    CONTROLLED_K = 1
    WEIGHT = 65
    EXPECTED_CALORIES = 3102
    FAKE_ANC = {
        # 'proteins_per_kg':  {'key': 'proteins_per_kg', 'min': 0.8},
        'vitamin_k':  {'key': 'vitamin_k', 'min': 45},
    }
    EXPECTED = [
        # call({'key': 'proteins_per_kg', 'min': 1.2, 'max': 1.4, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'vitamin_k', 'unit': 'µg', 'min': 45, 'max': 50, 'name': 'K1+K2','daily_tolerance': 10, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
    ]

    def test_diet(self):
        ctrs = self._test_diet()
        self.assertEqual(len(ctrs), 1)

class TestLowTrilyceridesCardioDiet(TestCardioDiet):
    LOW_TRIGLY = 1
    WEIGHT = 65
    EXPECTED_CALORIES = 3102
    REQUIRED_NUTRIENTS = "glucides", "energiekilocalories"
    FAKE_ANC = {
        'fibres':  {'key': 'fibres', 'min': 20, 'max': 35, 'unit': 'g'},
        'lipids':  {'key': 'lipids', 'min': 35, 'max': 40, 'unit': 'g'},
    }

    EXPECTED = [
        call({'key': 'added_sugar', 'name': 'sucres ajoutés', 'unit': 'g',
              'max': 7, 'daily_tolerance': 0, 'mode': 'percentage_energy', 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'alcool', 'name': 'alcool', 'unit': 'g',
              'max': 24, 'daily_tolerance': 0, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'fibres', 'unit': 'g', 'name': 'fibres alimentaires totales',
              'min': 30, 'daily_tolerance': 0, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'fibres_per_kg', 'mode': 'per_1000kcal', 'name': 'fibres alimentaires totales',
              'cost': 50, 'min': 15, 'daily_tolerance': 0, 'unit': 'g'}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'glucides', 'unit': 'g', 'name': 'glucides totaux (par différence)',
              'min': 50, 'mode': 'percentage_energy', 'daily_tolerance': 5, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
    ]

    def setUp(self):
        super().setUp()

        self.day = self.create_db_day(planning=self.planning)
        self.init_default_meal_type_settings()
        meal_slot = self.create_db_mealslot(self.day, meal_type=MealType.objects.get(key="lunch"))
        meal_slot = self.create_db_mealslot(self.day, meal_type=MealType.objects.get(key="dinner"))

    def test_diet(self):
        ctrs = self._test_diet()
        self.assertEqual(len(ctrs), 8)
        self.assertTrue(isinstance(ctrs[-3], NutrientBalanceConstraint))
        self.assertTrue(isinstance(ctrs[-2], NutrientMealTypeConstraint))
        self.assertTrue(isinstance(ctrs[-1], NutrientMealTypeConstraint))

class TestHyposodicCardioDiet(TestCardioDiet):
    HYPOSODIC = 1
    WEIGHT = 65
    EXPECTED_CALORIES = 3102
    FAKE_ANC = {
        # 'proteins_per_kg':  {'key': 'proteins_per_kg',  'min': 0.8},
        'sodium':           {'key': 'sodium',           'max': 3200, 'daily_tolerance': 0},
    }
    EXPECTED = [
        # call({'key': 'proteins_per_kg', 'min': 1.2, 'max': 1.4, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
        call({'key': 'sodium', 'max': 2400, 'daily_tolerance': 0, 'cost': 50}, EXPECTED_CALORIES, WEIGHT),
    ]

    def setUp(self):
        super().setUp()

    def test_diet(self):
        ctrs = self._test_diet()
        self.assertEqual(len(ctrs), 1)

class TestHyposodicSlimCardioDiet(TestCardioDiet):
    HYPOSODIC = 1
    WEIGHT = 95
    OBJECTIVE = 68
    EXPECTED_CALORIES = 3133
    FAKE_ANC = {
        # 'proteins_per_kg':  {'key': 'proteins_per_kg',  'min': 0.8},
        'sodium':           {'key': 'sodium',           'max': 3200, 'daily_tolerance': 0},
    }
    EXPECTED = [
        # call({'key': 'proteins_per_kg', 'min': 1.2, 'max': 1.4, 'cost': 50}, EXPECTED_CALORIES, OBJECTIVE),
        call({'key': 'sodium', 'max': 2400, 'daily_tolerance': 0, 'cost': 50}, EXPECTED_CALORIES, OBJECTIVE),
    ]

    def setUp(self):
        super().setUp()

    def test_diet(self):
        self._test_diet()
        ctrs = self._test_diet()
        self.assertEqual(len(ctrs), 1)
