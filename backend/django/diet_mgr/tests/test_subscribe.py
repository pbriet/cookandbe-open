from common.test                import TestAPIWithLogin, add_permissions

from django.utils               import timezone

from diet_mgr.handlers.base     import DietHandlerBase
from diet_mgr.models            import Diet

import json

class TestSubscribeToDiet(TestAPIWithLogin):
    """
    Series of test on subscribing to a given diet through the API
    """
    
    def setUp(self):
        super().setUp()
        self.create_db_meta_planning()
        self.create_db_profile() # Set a main profile to the user
        
        self.simple_diet = self.create_db_diet("simple")
        self.disabled_diet = self.create_db_diet("disabled", enabled = False)
        
        self.diet_with_params = self.create_db_diet("with_params")
        
        class FakeSimpleDietHandler(DietHandlerBase):
            DIET_PARAMETERS = {}
            KEY = "simple"
        
        class FakeAdminDietHandler(DietHandlerBase):
            DIET_PARAMETERS = {}
            KEY = "disabled"
        
        class FakeWithParamsDietHandler(DietHandlerBase):
            DIET_PARAMETERS = {
                "mandatory_int":    (int, True),
                "optional_float":   (float, False),
                "mandatory_string": (str, True)
                }
            KEY = "with_params"
    
    def tearDown(self):
        del Diet._handlers['simple']
        del Diet._handlers['disabled']
        del Diet._handlers['with_params']
        
    def test_subscribing_basic(self):
        response = self._subscribe_to(self.simple_diet)
        self.assertEqual(response.status_code, 201)
        self.reload_user()
        self.assertEqual(self.user.diet_id, self.simple_diet.id)
        self.assertEqual(self.user.diet_parameters.count(), 0)
        
    @add_permissions("admin")
    def test_subscribing_admin_disabled_diet(self):
        response = self._subscribe_to(self.disabled_diet)
        self.assertEqual(response.status_code, 201)
        self.reload_user()
        self.assertEqual(self.user.diet_id, self.disabled_diet.id)
        self.assertEqual(self.user.diet_parameters.count(), 0)
        
    @add_permissions("operator")
    def test_subscribing_operator_disabled_diet(self):
        response = self._subscribe_to(self.disabled_diet)
        self.assertEqual(response.status_code, 201)
        self.reload_user()
        self.assertEqual(self.user.diet_id, self.disabled_diet.id)
        self.assertEqual(self.user.diet_parameters.count(), 0)
        
    def test_forbidden_user_disabled_diet_subscribtion(self):
        response = self._subscribe_to(self.disabled_diet)
        self.assertEqual(response.status_code, 403)
        self.reload_user()
        self._ensure_no_diet()

    def _subscribe_to(self, diet, **parameters):
        if len(parameters) == 0:
            post_kargs = {}
        else:
            post_kargs = {'parameters': json.dumps(parameters)}
        return self.client.post('/api/user/%i/subscribe_to_diet/%i' % (self.user.id, diet.id),
                                post_kargs)

    def test_subscribing_complex_correct(self):
        response = self._subscribe_to(self.diet_with_params, mandatory_int=3,
                                      mandatory_string="toto")
        self.assertEqual(response.status_code, 201)
        
        self.reload_user()
        self.assertEqual(self.user.diet_id, self.diet_with_params.id)
        self.assertEqual(self.user.diet_parameters.count(), 2)
        updated_ago = (timezone.now() - self.user.diet_changed_at).seconds
        self.assertTrue(updated_ago < 10 and updated_ago >= 0) # Diet was updated in the last 10s
        
        ## Testing replacing existing values, with the optional arg
        response = self._subscribe_to(self.diet_with_params, mandatory_int=7,
                                      optional_float=2.1, mandatory_string="plops")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user.diet_parameters.count(), 3)
        diet_parameters = dict((dp.name, (dp.float_value, dp.string_value)) for dp in self.user.diet_parameters.all())
        self.assertEqual(diet_parameters, {"mandatory_int": (7, None),
                                           "optional_float": (2.1, None),
                                           "mandatory_string": (None, "plops")})


        response = self.client.get('/api/user/%i/current_diet_parameters' % self.user.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                         {"mandatory_int": 7, "optional_float": 2.1, "mandatory_string": "plops"})
    
    def _ensure_no_diet(self):
        self.reload_user()
        self.assertTrue(self.user.diet_id is None)
        self.assertEqual(self.user.diet_parameters.count(), 0)
    
    def test_missing_mandatory(self):
        response = self._subscribe_to(self.diet_with_params, optional_float=2.3, mandatory_string="toto")
        self.assertEqual(response.data['status'], 'error')
        self._ensure_no_diet()
        
    def test_unknown_arg(self):
        response = self._subscribe_to(self.diet_with_params, mandatory_int=3,
                                      optional_float=2.3, mandatory_string="toto",
                                      what_the_hell=42)
        self.assertEqual(response.data['status'], 'error')
        self._ensure_no_diet()
        
    def test_invalid_types(self):
        response = self._subscribe_to(self.diet_with_params, mandatory_int="oops !",
                                      optional_float=2.3, mandatory_string="ok")
        self.assertEqual(response.data['status'], 'error')
        self._ensure_no_diet()