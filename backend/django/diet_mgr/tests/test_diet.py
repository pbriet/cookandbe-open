
from diet_mgr.handlers.base         import DietHandlerBase
from diet_mgr.handlers.anc          import AncStandardDiet
from diet_mgr.handlers.easy_digest  import EasyDigestDiet
from diet_mgr.serializers           import DietSerializer

from common.mock_tools              import fake_prices_decorator
from common.test                    import TestAPIWithLogin, OptalimTest, add_permissions

from mock                           import patch, MagicMock, call

from nutrient.models                import NutrientPack

import optalim
import numpy

class TestDietViewSet(TestAPIWithLogin):
    def setUp(self):
        self.enabled_diet = self.create_db_diet("enabled", enabled = True)
        self.disabled_diet = self.create_db_diet("disabled", enabled = False)
        super().setUp()

    def _get_diet_kargs(self, **modifications):
        default_kargs = { "enabled": False, "title": "Jabba", "description": "Eat more to get bigger", "key": "jabba" }
        default_kargs.update(modifications)
        return default_kargs

    def test_user_diet_list(self):
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 2)
        for diet_data in response.data:
            self.assertTrue(diet_data["enabled"])
        self.assertEqual({"balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

    @add_permissions("admin")
    def test_admin_diet_list(self):
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 3)
        self.assertEqual({"disabled": False, "balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

    @add_permissions("operator")
    def test_operator_diet_list(self):
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 3)
        self.assertEqual({"disabled": False, "balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

    def test_user_diet_update(self):
        response = self.client.put('/secure/api/diet/%i' % self.disabled_diet.id, self._get_diet_kargs(enabled = True))
        self.assertEqual(response.status_code, 403)
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 2)
        self.assertEqual({"balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

    @add_permissions("admin")
    def test_admin_diet_update(self):
        response = self.client.put('/secure/api/diet/%i' % self.disabled_diet.id, self._get_diet_kargs(enabled = True))
        self.assertEqual(response.status_code, 403)
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 3)
        self.assertEqual({"disabled": False, "balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

    @add_permissions("operator")
    def test_operator_diet_update(self):
        response = self.client.put('/secure/api/diet/%i' % self.disabled_diet.id, self._get_diet_kargs(enabled = True))
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/secure/api/diet')
        self.assertEqual(len(response.data), 3)
        self.assertEqual({"jabba": True, "balanced": True, "enabled": True}, dict((d['key'], d['enabled']) for d in response.data))

class TestDietSerializer(OptalimTest):

    @fake_prices_decorator
    def test_serialization_paying(self):
        self.diet = self.create_db_diet(min_subscription_level=1)
        res = DietSerializer(self.diet).data
        self.assertEqual(res['cost_1'], 5)
        self.assertEqual(res['cost_3'], 4)
        self.assertEqual(res['cost_12'], 3)

    @fake_prices_decorator
    def test_serialization_free(self):
        self.diet = self.create_db_diet(min_subscription_level=0)
        res = DietSerializer(self.diet).data
        self.assertTrue('cost_1' not in res)

class DietHandlerTest(OptalimTest):
    """
    Test that a handler is correctly registered in a Diet
    """
    @patch('diet_mgr.handlers.base.Diet.register_diet_handler')
    def test_handler_registering(self, mck_register):
        class DummyDietHandler(DietHandlerBase):
            KEY="dummy"

        mck_register.assert_called_once_with("dummy", DummyDietHandler)

class TestAncDiet(OptalimTest):

    PROFILE_AGE = 25

    def setUp(self):
        super().setUp()
        self.diet = self.create_db_diet()
        self.planning = self.create_db_planning()
        self.nutrient = self.create_db_nutrient('Midichlorien', id=10, unit='mg')
        nutrient_pack = self.create_db_nutrient_pack()
        self.user.nutrient_packs.add(nutrient_pack)
        nutrient_pack.nutrients.add(self.nutrient)
        self.profile = MagicMock(age=self.PROFILE_AGE, sex="male", weight_or_default=70,
                                 height_or_default=175, caloric_need=lambda:3000,
                                 creator=self.user)
        self.diet_handler = AncStandardDiet(self.diet, self.profile)

    @patch('diet_mgr.handlers.anc.NutrientConstraint')
    def test_basic_diet(self, mck_nutrient_ctr):
        """
        Test a simple diet with one min-max on one nutrient
        """
        with patch.object(optalim.config.Config, 'anc',
            {'profile1':
                {'min_age': 20, 'max_age': 60, 'sex': 'male',
                'nutrients':
                    {'midi':
                        {'name': 'Midichlorien',
                        'min': 30,
                        'max': 50,
                        'cost': 9999,
                        'unit': 'mg',
                        'daily_tolerance': 25
                        }
                    }
                 }
             }):
            ctrs = self.diet_handler.build_nutrient_constraints(self.planning)

            self.assertEqual(len(ctrs), 1)
            mck_nutrient_ctr.assert_called_once_with(self.nutrient, 30, 50,
                                                     daily_tolerance_min=0.25,
                                                     daily_tolerance_max=0.25,
                                                     cost_per_percent_out=9999)

class TestYoungAncDiet(TestAncDiet):

    PROFILE_AGE = 18

class TestEasyDigestDiet(OptalimTest):

    def setUp(self):
        super().setUp()
        self.planning = self.create_db_planning()
        self.diet = self.create_db_diet("easy_digest")
        self.profile = MagicMock(age=25, sex="male", weight_or_default=70,
                                 height_or_default=175, caloric_need=lambda:3000,
                                 creator_id=self.user.id)

    @patch('diet_mgr.handlers.anc.AncStandardDiet._load_nutrient_constraint')
    def test_easy_digest_diet(self, mock_load_constraint):
        with patch.object(optalim.config.Config, 'anc',
            {'profile1':
                {'min_age': 23, 'max_age': 30, 'sex': 'male',
                'nutrients':
                    {'lipids':  {'key': 'lipids', 'min' : 60, 'max': 75},
                     'plop': {'key': 'plop', 'min': 99}
                    }
                 }
             }):
            ctrs = self.diet.handler(self.profile).build_nutrient_constraints(self.planning)
            expected = [call({'key': 'lipids',  'min': 30, 'max': 35, 'cost': 100}, 3000, 70),
                        call({'key': 'plop',    'min': 99}, 3000, 70)]
            self.assertEqual(mock_load_constraint.mock_calls, expected)
