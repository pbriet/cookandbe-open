
from common.test                import OptalimTest
from common.model               import reload_object
from common.mock_tools          import FakeNow, fake_today_decorator

from diet_mgr.handlers.base     import DietHandlerBase
from diet_mgr.handlers.slim     import SlimDietHandler

from profile_mgr.models         import ProfileValue

from mock                       import patch

import diet_mgr.tasks
import diet_mgr.handlers.base
import diet_mgr.handlers.slim


class TestMetabolismUpdateWithNoHistoryBefore(OptalimTest):

    def setUp(self):
        super().setUp()
        self.diet = self.create_db_diet("plop")
        with FakeNow(2014, 12, 5):
            self.profile = self.create_db_profile(weight=None, height=None, metabolism=1)
        with FakeNow(2014, 12, 6):
            self.profile.weight = 60
            self.profile.save()

    @fake_today_decorator(2015, 1, 13)
    def test_no_history(self):
        DietHandlerBase(self.diet, self.profile).update_metabolism()
        self.assertEqual(self.profile.metabolism, 1.0) # No data -- no change

class TestMetabolismUpdate(OptalimTest):
    """
    Exemple :
    5 Janvier : 70kg        Départ avec métabolisme 1
    10 Janvier : 70.3kg     (pas de mise à jour, moins de 15 jours écoulés)
    11 Janvier : 72kg       (pas de mise à jour)
    21 Janvier : 70.8kg     Moyenne du poids sur les 3 dernières prises = 71kg. 1kg pris, 16 jours écoulés. Prise de ~62g/jour  -->   -10%
    25 Janvier : 70.2kg     (pas de mise à jour)
    10 Février : 70kg       Moyenne sur les 2 dernières prises : 70.1kg. 900g perdus, 17 jours écoulés. Perte de 53g/jour  --> +5%
    26 Février : 69.8kg     Pas de moyenne : 69.8kg. 300g perdus, 16 jours écoulés. Perte de 18g/jour --> statu quo
    8 Mai : 71.5kg          Pas de moyenne : 71.5kg. 1.7kg pris, 69 jours écoulés. Gain de 25g/jour, mais prise > 800g. -->  -2%
    8 Juin : 71kg           Pas de moyenne : 71kg. 500g perdu, 30 jours écoulés. Perte de 17g/jour, perte > 400g, mais sans tendance -->  statu quo
    16 Juin : 70.9kg        Moyenne : 70.95kg. 550g perdu, 38 jours écoulés. Perte de 14g/jour, perte > 400g tjrs sans tendance longue
    25 Juin : 70.8kg        Pas de moyenne : 70.85kg. 650g perdu, 47 jours écoulés. Perte de 14g/jour, perte > 400g tjrs avec tendance longue --> +2%
    """

    def setUp(self):
        super().setUp()
        self.diet = self.create_db_diet("plop")

    def _update_weight_and_metabolism(self, value, date_values):
        with FakeNow(*date_values):
            self.profile.weight = value
            self.profile.save()
            DietHandlerBase(self.diet, self.profile).update_metabolism()

    @patch.object(diet_mgr.handlers.base, 'MIN_REASONABLE_CALORIES', 1300)
    def test_update_with_min_calories(self):
        with FakeNow(2014, 1, 5):
            # Profile with a caloric need
            self.profile = self.create_db_profile(weight=70, height=180, work_score=0,
                                                  moving_score=0, sport_score=0, sex="female",
                                                  metabolism=0.8)

        self._update_weight_and_metabolism(71, (2014, 1, 20))
        self.assertAlmostEqual(self.profile.metabolism, 0.76, 2) # Lower metabolism

        # Minimum calories
        self.assertEqual(round(self.profile.caloric_need()), 1339)

        self._update_weight_and_metabolism(72, (2014, 2, 10))
        self.assertAlmostEqual(self.profile.metabolism, 0.74, 2) # Metabolism change, but only so that calories are at minimum

        # Minimum calories
        self.assertEqual(round(self.profile.caloric_need()), 1296) # We cannot ensure anymore being strictly at minimum
                                                                   # because of the correction that has been added
                                                                   # Into caloric_need (end of Black&co calculation)



    @patch.object(diet_mgr.handlers.base, 'MIN_REASONABLE_CALORIES', 1300)
    def test_the_metabolism_updater(self):
        with FakeNow(2014, 1, 5):
            self.profile = self.create_db_profile(weight=70)

        self._update_weight_and_metabolism(70.3, (2014, 1, 10))
        self.assertEqual(self.profile.metabolism, 1.0) # No change -- too soon

        self._update_weight_and_metabolism(72, (2014, 1, 11))
        self.assertEqual(self.profile.metabolism, 1.0) # Still no change -- too soon

        self._update_weight_and_metabolism(70.8, (2014, 1, 21))
        self.assertEqual(round(self.profile.metabolism, 1), 0.9) # -10%

        self._update_weight_and_metabolism(70.2, (2014, 1, 25))
        self.assertEqual(round(self.profile.metabolism, 1), 0.9) #  No change -- too soon

        self._update_weight_and_metabolism(70, (2014, 2, 10))
        self.assertEqual(round(self.profile.metabolism, 3), 0.945) # +5%

        self._update_weight_and_metabolism(69.8, (2014, 2, 26))
        self.assertEqual(round(self.profile.metabolism, 3), 0.945) # Relative stability

        self._update_weight_and_metabolism(71.5, (2014, 5, 8))
        self.assertEqual(round(self.profile.metabolism, 4), 0.9261) # Long term weight gain : -2%

        self._update_weight_and_metabolism(71, (2014, 6, 8))
        self.assertEqual(round(self.profile.metabolism, 4), 0.9261) # Small long term weight loss, but no trend.

        self._update_weight_and_metabolism(70.9, (2014, 6, 16))
        self.assertEqual(round(self.profile.metabolism, 6), 0.9261) # Still no trend

        self._update_weight_and_metabolism(70.8, (2014, 6, 25))
        self.assertEqual(round(self.profile.metabolism, 6), 0.944622) # Long term weight loss : +2%


class TestMetabolismUpdateTask(OptalimTest):

    UPDATED_USER_IDS = []

    def fake_apply_update(users):
        TestMetabolismUpdateTask.UPDATED_USER_IDS = []
        for user in users:
            TestMetabolismUpdateTask.UPDATED_USER_IDS.append(user.id)

    @patch.object(diet_mgr.tasks, 'apply_update', fake_apply_update)
    @fake_today_decorator(2014, 2, 5)
    def _test_update(self):
        diet_mgr.tasks.update_metabolisms()
        return sorted(self.UPDATED_USER_IDS)

    def test_update_required(self):
        with FakeNow(2014, 2, 4, 12, 45):
            # Updated the previous day
            self.create_db_profile()
        self.assertEqual(self._test_update(), [self.user.id])

    def test_update_two_days_ago(self):
        with FakeNow(2014, 2, 3, 12, 45):
            # Updated two days ago -> ignored
            self.create_db_profile()
        self.assertEqual(self._test_update(), [])

    def test_update_secondary_profile(self):
        with FakeNow(2014, 1, 3, 12, 45):
            # Created a month ago
            # Main profile
            main_profile = self.create_db_profile()
            secondary_profile = self.create_db_profile()

        with FakeNow(2014, 2, 4, 12, 45):
            # Yesterday: updating secondary profile
            secondary_profile.weight = 77
            secondary_profile.save()

        self.assertEqual(self._test_update(), [])

    def test_update_multiple_users(self):
        user2 = self.create_db_user()
        user3 = self.create_db_user()

        with FakeNow(2014, 1, 3, 12, 45):
            # User 1 and 2 profiles were created a month ago
            user_profile = self.create_db_profile(creator=self.user)
            user2_profile = self.create_db_profile(creator=user2)

        with FakeNow(2014, 2, 4, 21, 58):
            # User 1 profile was updated yesterday
            user_profile.weight = 33
            user_profile.save()

            # User 3 profile was created yesterday
            user3_profile = self.create_db_profile(creator=user3)

        self.assertEqual(self._test_update(), [self.user.id, user3.id])


class TestSlimMetabolismUpdate(OptalimTest):
    """
    Test that a metabolism update
    """
    def setUp(self):
        super().setUp()
        self.create_db_meta_planning()

    @fake_today_decorator(2014, 2, 5)
    @patch('diet_mgr.handlers.slim.sendmail_template')
    @patch.object(diet_mgr.handlers.base.DietHandlerBase, 'update_metabolism', lambda x: x._apply_metabolism_correction(-0.05))
    def test_update(self, mock_sendmail_template):
        with FakeNow(2014, 2, 4, 12, 45):
            self.create_db_profile()

        self.slim = self.create_db_diet("slim")
        self.assign_diet_user(self.user, self.slim, objective=58, mode='eat_different')

        diet_mgr.tasks.update_metabolisms()

        args, kwargs = mock_sendmail_template.call_args
        self.assertEqual(args[2]['percentage'], 5)
        self.assertEqual(round(args[2]['nb_calories']), 2371)
        self.assertEqual(len(kwargs["users"]), 1)
        self.assertEqual(kwargs["users"][0].id, self.user.id)


    @fake_today_decorator(2014, 2, 5)
    @patch.object(diet_mgr.handlers.slim, 'sendmail_template', lambda *args, **kargs: True)
    def _test_losing_at_beginning(self, objective, base_weight, last_weight, expected_metabolism):
        """
        Test the reaction of a one-week weight evolution
        @param objective: what's the user weight-objective
        @param base_weight: what's is initial weight
        @param last_weight: the weight after one week
        @param expected_metabolism: value of metabolism post-weight update
        """
        self.slim = self.create_db_diet("slim")
        with FakeNow(2014, 1, 28, 12, 45):
            self.assign_diet_user(self.user, self.slim, objective=objective, mode='eat_different')
            profile = self.create_db_profile(weight=base_weight)

        with FakeNow(2014, 2, 4, 12, 45):
            profile.weight=last_weight
            profile.save()

        diet_mgr.tasks.update_metabolisms()
        reload_object(profile)

        self.assertEqual(profile.metabolism, expected_metabolism)


    def test_slim_diet_do_not_update_when_losing_at_beginning(self):
        """
        Test that there is not metabolism update when losing weight in the first 10 days
        """
        # One kilo loss in 7 days
        # No modification - accepted at the beginning of the diet
        self._test_losing_at_beginning(60, 70, 69, 1.0)

    def test_slim_diet_losing_a_lot_at_beginning(self):
        """
        Test that there is not metabolism update when losing weight in the first 10 days
        """
        # Two kilos loss in 7 days
        # Metabolism increased
        self._test_losing_at_beginning(60, 70, 68, 1.15)

    def test_slim_diet_losing_standard_at_beginning(self):
        """
        Test that there is not metabolism update when losing weight in the first 10 days
        """
        # 400g loss in 7 days
        # no metabolism change
        self._test_losing_at_beginning(60, 70, 69.6, 1.0)

    def test_slim_diet_losing_too_few_at_beginning(self):
        """
        Test that there is not metabolism update when losing weight in the first 10 days
        """
        # 50g loss in 7 days
        # decreasing metabolism
        self._test_losing_at_beginning(60, 70, 69.95, 0.9)

    def test_slim_diet_gaining_weight_at_beginning(self):
        """
        Test that there is not metabolism update when losing weight in the first 10 days
        """
        # 1kg gain in 7 days
        # decreasing metabolism
        self._test_losing_at_beginning(60, 70, 71, 0.85)


    def _update_weight_and_metabolism(self, value, date_values):
        with FakeNow(*date_values):
            self.profile.weight = value
            self.profile.save()
            SlimDietHandler(self.diet, self.profile).update_metabolism()

    @patch('diet_mgr.handlers.slim.sendmail_template')
    @patch.object(diet_mgr.handlers.base, 'MIN_REASONABLE_CALORIES', 1250)
    @patch.object(diet_mgr.handlers.slim, 'MIN_REASONABLE_CALORIES', 1250)
    def test_update_with_min_calories(self, mock_sendmail_template):
        with FakeNow(2014, 1, 5):
            # Profile with a caloric need of 1346kcal
            self.profile = self.create_db_profile(weight=67, height=172, work_score=0,
                                                  moving_score=0, sport_score=0, sex="female",
                                                  metabolism=0.8)

        self.slim = self.create_db_diet("slim")
        self.assign_diet_user(self.user, self.slim, objective=60, mode='eat_different')

        self._update_weight_and_metabolism(67, (2014, 1, 20)) # Stability
        self.assertAlmostEqual(self.profile.metabolism, 0.777, 2) # Lower metabolism

        # Minimum calories
        self.assertEqual(round(SlimDietHandler(self.slim, self.profile).compute_calories()), 1250)
        # Email has been sent
        self.assertEqual(mock_sendmail_template.call_count, 1)
        args, kwargs = mock_sendmail_template.call_args

        self.assertEqual(args[2]['percentage'], 2)
        self.assertEqual(round(args[2]['nb_calories']), 1250)


        self._update_weight_and_metabolism(67, (2014, 2, 20)) # Still stable
        self.assertAlmostEqual(self.profile.metabolism, 0.78, 2) # Metabolism is at minimum
        # Minimum calories
        self.assertEqual(round(SlimDietHandler(self.slim, self.profile).compute_calories()), 1250)
        # No more emails
        self.assertEqual(mock_sendmail_template.call_count, 1)
