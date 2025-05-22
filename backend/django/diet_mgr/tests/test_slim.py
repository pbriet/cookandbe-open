from common.test                import TestAPIWithLogin
from common.mock_tools          import fake_today_decorator, FakeNow
from mock                       import patch, call

import optalim.config

import datetime
import json

class TestSubscribeToSlim(TestAPIWithLogin):
    def setUp(self):
        super().setUp()
        self.create_db_meta_planning()
        self.slim = self.create_db_diet("slim")
        self.profile = self.create_db_profile(height=165, weight=60)

    def _subscribe_to(self, **parameters):
        post_kargs = {'parameters': json.dumps(parameters)}
        return self.client.post('/api/user/%i/subscribe_to_diet/%i' % (self.user.id, self.slim.id),
                                post_kargs)

    def test_success_subscription(self):
        res = self._subscribe_to(objective = 52, mode='eat_different')
        self.assertEqual(res.data['status'], 'success')


    def test_not_really_slim(self):
        res = self._subscribe_to(objective = 65, mode='eat_different')
        self.assertEqual(res.data['status'], 'error')


class TestSlimDiet(TestAPIWithLogin):
    HEIGHT = 165
    FORCED_BASE_CALORIES = None

    def setUp(self):
        super().setUp()
        self.planning = self.create_db_planning()
        self.slim = self.create_db_diet("slim")
        self.profile = self.create_db_profile(weight=self.WEIGHT, height=self.HEIGHT, birth_date=datetime.datetime(1985, 1, 13),
                                              sex="male", work_score=6, metabolism=1.2,
                                              forced_base_calories=self.FORCED_BASE_CALORIES)
        with FakeNow(2010, 1, 1):
            self.assign_diet_user(self.user, self.slim, objective=self.OBJECTIVE, mode='eat_different')

    @patch('diet_mgr.handlers.anc.AncStandardDiet._load_nutrient_constraint')
    @fake_today_decorator(2010, 3, 1)
    def _test_diet(self, mock_load_constraint):
        with patch.object(optalim.config.Config, 'anc',
            {'profile1':
                {'min_age': 23, 'max_age': 30, 'sex': 'male',
                'nutrients':
                    {#'proteins_per_kg':  {'key': 'proteins_per_kg', 'min' : 0.8},
                     'lipids': {'key': 'lipids', 'max': 50},
                     'proteins': {'key': 'proteins', 'min': 10, 'max': 20},
                     'calories': {'key': 'calories', 'max': 3000}
                    }
                 }
             }):
            ctrs = self.slim.handler(self.profile).build_nutrient_constraints(self.planning)
            # expected : different value for proteins, and level of calories based on HIDDEN_OBJECTIVE
            expected = [call({'key': 'calories',        'max': 3000,            'cost': 100}, self.EXPECTED_CALORIES, self.HIDDEN_OBJECTIVE),
                        call({'key': 'lipids',          'max': 50,              'cost': 100}, self.EXPECTED_CALORIES, self.HIDDEN_OBJECTIVE),
                        call({'key': 'proteins',        'min': 15, 'max': 25, 'cost': 100},  self.EXPECTED_CALORIES, self.HIDDEN_OBJECTIVE)]
            self.assertEqual(mock_load_constraint.mock_calls, expected)

class TestSlimDietWithReasonableObjective(TestSlimDiet):
    """
    Reasonable objective : calories should be Black&co for objective, - some percentage
    """
    WEIGHT = 70
    OBJECTIVE = 64
    HIDDEN_OBJECTIVE = OBJECTIVE
    EXPECTED_CALORIES = 2968  # Black&co for 64kg (3092.03) - 4%

    def test_diet(self):
        self._test_diet()


class TestSlimDietWithExternalSource(TestSlimDietWithReasonableObjective):
    """
    Same as before, byt with theorical calories in "standard diet" provided by external source
    """
    FORCED_BASE_CALORIES = 2200

    # Theorical calories "standard" : 3133 Kcal
    # Theorical calories "objective" : 3092 Kcal
    # ------------> Ratio = 98.69%
    # Forced base calories with NAP : 2200*1.7 = 3740 Kcal
    # Applying diminution ratio : 3740*0.9869 = 3691 Kcal
    # Correction (reasonable objective) :  -4%
    EXPECTED_CALORIES = 3543

    def test_diet(self):
        self._test_diet()



class TestSlimDietWithAmbitiousObjective(TestSlimDiet):
    """
    Reasonable objective : calories should be Black&co for objective, - some percentage
    """
    WEIGHT = 70
    OBJECTIVE = 58
    HIDDEN_OBJECTIVE = OBJECTIVE
    EXPECTED_CALORIES = 3025  # Black&co for 58kg

    def test_diet(self):
        self._test_diet()

class TestSlimDietOverweightObjective(TestSlimDiet):
    """
    Overweight person
    """
    WEIGHT = 120
    OBJECTIVE = 100
    HIDDEN_OBJECTIVE = 68
    EXPECTED_CALORIES = 3133  # Black&co for IMC == 25

    def test_diet(self):
        self._test_diet()



class TestSlimDiagnosis(TestAPIWithLogin):
    """
    Test the diagnosis step
    """

    def setUp(self):
        super().setUp()
        self.slim = self.create_db_diet("slim")
        self.profile = self.create_db_profile(height=165, weight=60)
        self.create_db_meta_planning()

    @fake_today_decorator(2010, 3, 1)
    def _test_diagnostic(self, questions, expected=None, initial_weight=None):
        """
        Test sending questions to slim diagnostic
        """
        if initial_weight is not None:
            self.profile.weight = initial_weight
            self.profile.save()

        response = self.client.post('/api/user/%i/diagnose/%i' % (self.user.id, self.slim.id),
                                    {'arguments': json.dumps(questions), 'auto_select': True})

        if expected is None:
            return response

        expected['questions'] = questions

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], expected)

    @fake_today_decorator(2010, 3, 1)
    def test_too_much_loss(self):
        """
        Too much weight loss
        Metabolism reduction
        """
        questions = {'objective': 100, 'snacking': 1,
                     'diet_past': 5,   'genetic': 1}

        expected = {'params':  {'mode': 'eat_different', 'objective': 119},
                    'profile': {'metabolism': 0.72},
                     'other':  {'objective_non_reasonable': True, 'original_objective': 100,
                                'estimated_date': datetime.date(2010, 12, 26)}
                    }

        self._test_diagnostic(questions, expected, initial_weight=140)

    @fake_today_decorator(2010, 3, 1)
    def test_objective_under_imc(self):
        """
        Objective under IMC
        """

        questions = {'objective': 10, 'snacking': 0,
                     'diet_past': 0,   'genetic': 1}

        expected = {'params':  {'mode': 'eat_less', 'objective': 51},
                    'profile': {'metabolism': 0.9},
                     'other':  {'objective_non_reasonable': True, 'original_objective': 10,
                                'estimated_date': datetime.date(2010, 7, 8)}
                   }

        self._test_diagnostic(questions, expected)


    @fake_today_decorator(2010, 3, 1)
    def test_ok(self):
        """
        Just a normal one !
        """

        questions = {'objective': 55, 'snacking': 0,
                     'diet_past': 0,  'genetic': 0}

        expected = {'params':  {'mode': 'eat_less', 'objective': 55},
                    'profile': {'metabolism': 1},
                    'other':   {'estimated_date': datetime.date(2010, 5, 12)}
                    }

        self._test_diagnostic(questions, expected)



    @fake_today_decorator(2010, 3, 1)
    def test_profile_below_imc(self):
        """
        With already low IMC
        """

        self.profile.weight = 45
        self.profile.save()

        questions = {'objective': 40, 'snacking': 0,
                     'diet_past': 0,  'genetic': 0}

        expected = {'params':  {'mode': 'eat_less', 'objective': 55},
                    'profile': {'metabolism': 1},
                    'other':   {'estimated_date': datetime.date(2010, 5, 12)}
                    }

        res = self._test_diagnostic(questions)
        self.assertEqual(res.data['status'], 'error')
        self.assertTrue(res.data['error'].startswith('Votre IMC actuel est inférieur à 18.5'))
