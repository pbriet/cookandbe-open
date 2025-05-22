from common.test                import OptalimTest

from user_mgr.models            import User

from profile_mgr.models         import Profile

from eater_mgr.models           import Eater
from planning_mgr.models        import MetaPlanning

from recipe_mgr.models          import Ustensil

from mock                       import patch

import planning_mgr.controller.meta
import cookandbe.hooks
import cookandbe.user
import datetime
import json

class TestQuickSignupAPI(OptalimTest):
    CREATE_DEFAULT_USER = False
    NB_USTENSILS = 12

    def setUp(self):
        super().setUp()
        self.init_profile_metrics()
        # More than 30 characters, to ensure that signup is not limited
        self.BIG_EMAIL = 'kaloooooooooooooooooooooooooooooooo1@free.fr'
        self.values = { 'email': self.BIG_EMAIL, 'password': 'toto42', 'first_name': 'Plop', 'app': 'public'}
        for i in range(self.NB_USTENSILS):
            self.create_db_ustensil("U%i" %i, default_check = (i % 2 == 0))

    @patch.object(planning_mgr.controller.meta.DefaultPlanningBuilder, '__call__')
    @patch('cookandbe.user.sendmail_template')
    def _test_successful_signup(self, values, mock_sendmail, mock_planning_builder):
        response = self.client.post('/api/signup/', json.dumps(values),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)
        # Ensuring that the default planning builder has been called
        mock_planning_builder.assert_called_with()
        # Checks
        self.assertEqual(User.objects.count(), 1)
        user = User.objects.get()
        self.assertEqual(Profile.objects.count(), 1)
        profile = Profile.objects.get()
        self.assertTrue(user.main_profile.id, profile.id)
        self.assertEqual(Eater.objects.count(), 1)
        eater = Eater.objects.get()
        self.assertEqual(MetaPlanning.objects.count(), 1)
        meta_planning = user.meta_planning

        # User
        self.assertEqual(user.first_name, 'Plop')
        self.assertEqual(user.last_name, '')
        self.assertTrue(user.check_password(values["password"]))

        # Main profile
        self.assertEqual(profile.birth_date, None)
        self.assertEqual(profile.age, Profile.DEFAULT_AGE)
        self.assertEqual(profile.sex, 'female')
        self.assertTrue(profile.weight is None)
        self.assertTrue(profile.height is None)
        self.assertEqual(profile.creator_id, user.id)

        # Main eater
        self.assertEqual(eater.user_id, user.id)
        self.assertEqual(eater.profile_id, profile.id)

        # Ustensils
        self.assertEqual(user.ustensils.count(), self.NB_USTENSILS / 2)
        self.assertEqual(list(user.ustensils.all()), list(Ustensil.objects.filter(default_check = True)))

        self.assertEqual(mock_sendmail.call_count, 2)

        args, kargs = mock_sendmail.call_args_list[0]
        self.assertEqual(args[3], "Bienvenue sur Cook and Be !")
        self.assertEqual(kargs['email'], values["email"].strip().lower())
        args, kargs = mock_sendmail.call_args_list[1]
        self.assertEqual(args[3], "Donnez-nous votre avis sur Cook&Be")
        self.assertEqual(kargs['eta'], 864000)
        self.assertEqual(kargs['send_async'], True)
        self.assertEqual(kargs['users'], [user])

        return user

    def test_successful_signup(self):
        user = self._test_successful_signup(self.values)
        self.assertEqual(user.email, self.BIG_EMAIL)

    def test_successful_signup_with_trailing_whitespace(self):
        self.values['email'] += ' '
        user = self._test_successful_signup(self.values)
        self.assertEqual(user.email, self.BIG_EMAIL)

    def test_successful_signup_with_uppercase(self):
        self.values['email'] = self.values['email'].replace('o', 'O')
        user = self._test_successful_signup(self.values)
        self.assertEqual(user.email, self.BIG_EMAIL)

    def test_missing_field(self):
        response = self.client.post('/api/signup/', json.dumps({'app': 'public'}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Information manquante")

    def test_invalid_email(self):
        self.values["email"] = "blih@bluh"
        response = self.client.post('/api/signup/', json.dumps(self.values),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Adresse e-mail invalide")

    def test_duplicate_email(self):
        User.objects.create_user(self.BIG_EMAIL, 'toto')
        response = self.client.post('/api/signup/', json.dumps(self.values),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Compte existant")


class TestSignupWithDietAndProfileParams(OptalimTest):
    CREATE_DEFAULT_USER = False

    @patch.object(planning_mgr.controller.meta.DefaultPlanningBuilder, '__call__')
    @patch('cookandbe.user.sendmail_template')
    def _signup(self, expected_status, mock_sendmail, mock_planning_builder, expected_error_message=None):
        response = self.client.post('/api/signup/', json.dumps(self.values),
                                    content_type="application/json")
        self.assertEqual(response.status_code, expected_status)
        if expected_error_message:
            self.assertEqual(response.data["title"], expected_error_message)
            self._check_failure()


    def setUp(self):
        super().setUp()
        self.init_profile_metrics()
        self.values = { 'email': 'toto@titiplops.fr', 'password': 'toto42', 'app': 'public',
                        'first_name': 'Plop', 'diet_key': 'slim',
                        'diet_parameters' : {'objective': 55, 'mode': 'eat_different'},
                        'profile_metrics': {'weight': 70, 'height': 160}
                      }

        self.slim_diet = self.create_db_diet("slim")

    def _check_failure(self):
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(Profile.objects.count(), 0)

    def _check_success(self):
        user = User.objects.get()
        profile = user.main_profile

        self.assertEqual(profile.weight, 70)
        self.assertEqual(profile.height, 160)
        self.assertEqual(user.diet_id, self.slim_diet.id)

        diet_params = {}
        for param in user.diet_parameters.all():
            diet_params[param.name] = (param.float_value, param.string_value)
        self.assertEqual(diet_params, {"objective": (55., None), "mode": (None, 'eat_different')})

    def test_signup_success(self):
        self._signup(201)
        self._check_success()

    def test_fail_invalid_metric1(self):
        self.values['profile_metrics']['wtf'] = 44
        self._signup(200, expected_error_message="Valeur de profil invalide")

    def test_fail_invalid_metric2(self):
        self.values['profile_metrics']['weight'] = "gnark"
        self._signup(200, expected_error_message="Valeur de profil invalide")

    def test_fail_missing_profile_infos(self):
        del self.values['profile_metrics']['weight']  # "slim" diet requires weight to be defined in main profile
        self._signup(200, expected_error_message="Erreur de configuration")

    def test_fail_no_profile_nor_parameters_infos(self):
        del self.values['profile_metrics']
        del self.values['diet_parameters']
        self._signup(200, expected_error_message="Erreur de configuration")

    def test_fail_missing_diet_parameter(self):
        del self.values['diet_parameters']['objective']
        self._signup(200, expected_error_message="Erreur de configuration")

    def test_fail_invalid_diet_parameter(self):
        self.values['diet_parameters']['objective'] = "booh"
        self._signup(200, expected_error_message="Erreur de configuration")