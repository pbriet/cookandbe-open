from collections            import defaultdict

from common.test            import OptalimTest, TestAPIWithLogin
from common.mock_tools      import fake_today_decorator, fake_ratio_variable
from common.model           import reload_object

from eater_mgr.ratios       import RatiosCalculator

from planning_mgr.models    import MealSlot, Planning, MealPlace, Dish

from recipe_mgr.models      import DishType

from mock                   import patch
import profile_mgr.models
import datetime
import hippocrate.models.recipe
import eater_mgr.ratios

MALE_PROFILE = {"weight": 73.2,
                "height": 190,
                "birth_date": datetime.datetime(1985, 1, 13),
                "sex": "male",
                "work_score" :8}
MALE_PROFILE_CALORIES  =  3185


FEMALE_PROFILE = {"weight": 73,
                  "height": 174,
                  "birth_date": datetime.datetime(1985, 1, 13),
                  "sex": "female",
                  "work_score" :1,
                  "sport_score": 0,
                  "moving_score": 0}
FEMALE_PROFILE_CALORIES  =  1935


FEMALE_PROFILE_2 = {"weight": 59,
                   "height": 167,
                   "birth_date": datetime.datetime(1985, 1, 13),
                   "sex": "female",
                   "work_score" :0,
                   "sport_score": 0,
                   "moving_score": 0}
FEMALE_PROFILE_CALORIES2 = 1664

class TestProfileRatio(OptalimTest):
    """
    Test the calculation of dish ratios depending on profile (IMC, sex and caloric need)
    """
    def setUp(self):
        super().setUp()
        # Main profile in a male
        self.main_profile = self.create_db_profile(**MALE_PROFILE)
        reload_object(self.user)

    def _cmp_profile_ratios(self, profile, expected_ratio, expected_main_calories):
        """
        Calls RatiosCalculator and check results
        """
        calculator = RatiosCalculator(self.user)
        ratios = calculator.profile_ratios
        calories = round(calculator._profile_calories[self.main_profile.id]) # Rounding main_calories

        for prof_id in ratios.keys():
            ratios[prof_id] = round(ratios[prof_id], 2) # Rounding ratios

        self.assertEqual(calories, round(expected_main_calories))
        self.assertEqual(ratios, {self.main_profile.id: 1,
                                  profile.id: round(expected_ratio, 2)})

    @fake_today_decorator(2014, 3, 1)
    def test_profile_male(self):
        prof = self.create_db_profile(**MALE_PROFILE)
        self._cmp_profile_ratios(prof, 1, MALE_PROFILE_CALORIES)

    @fake_today_decorator(2014, 3, 1)
    def test_profile_female(self):
        prof = self.create_db_profile(**FEMALE_PROFILE)
        self._cmp_profile_ratios(prof, FEMALE_PROFILE_CALORIES / MALE_PROFILE_CALORIES, MALE_PROFILE_CALORIES)


    @fake_today_decorator(2014, 3, 1)
    def _test_with_slim_diet(self, slim_mode, expected_ratio, expected_main_calories):
        """
        Test how the slim diet affects the ratio.
        Given a slim_mode ('mode' parameter for diet 'slim'), what should be the
        expected ratio for the main profile ?
        """
        prof = self.create_db_profile(**FEMALE_PROFILE)
        self.slim = self.create_db_diet("slim")
        self.assign_diet_user(self.user, self.slim, objective=50, mode=slim_mode)

        self._cmp_profile_ratios(prof, expected_ratio, expected_main_calories)


    def test_with_slim_diet(self):
        # same as test_profile_female test * 80%
        self._test_with_slim_diet('eat_less', FEMALE_PROFILE_CALORIES / (MALE_PROFILE_CALORIES * 0.8), MALE_PROFILE_CALORIES * 0.8)

    @fake_today_decorator(2014, 3, 1)
    def test_with_slim_diet2(self):
        # same as test_profile_female test
        self._test_with_slim_diet('eat_different', FEMALE_PROFILE_CALORIES / MALE_PROFILE_CALORIES, MALE_PROFILE_CALORIES)



def mock_recipe_data(calories):
    class MockRecipeData(object):
        def get_data_from_key(*args):
            return calories
    return MockRecipeData

class BaseTestRatios(TestAPIWithLogin):

    @fake_today_decorator(2014, 3, 1)
    @patch.object(eater_mgr.ratios.RatiosCalculator, 'precision_from_nb_eaters', lambda *args, **kargs: 0.5)
    def _computeMealProfileRatios(self, days):
        """
        Retro-compatibility :
        Returns a dictionnary : { meal_slot_id: profile_id : ratio }}
        """

        self.dish_by_id = {}
        for d in Dish.objects.all():
            self.dish_by_id[d.id] = d


        res = defaultdict(lambda: defaultdict(float))
        calculator = RatiosCalculator(self.user)
        dish_ratios = calculator.get_initial_ratios(days)

        for dish_id, total_ratio in dish_ratios.items():
            dish = self.dish_by_id[dish_id]
            mealslot = dish.meal_slot
            profiles = [eater.profile for eater in mealslot.eaters.all()]

            ratio_per_profile = calculator.split_ratios(total_ratio, profiles)

            for p_id, value in ratio_per_profile.items():
                res[mealslot.id][p_id] = round(value, 4)

        return res



class TestMealProfileRatio(BaseTestRatios):
    """
    Testing the calculation of ratio on given profiles/meals
    """
    def setUp(self):
        super().setUp()
        self.init_default_nutrients()

        self.prof1 = self.create_db_profile(**MALE_PROFILE)   # Calories = 3185
        self.prof2 = self.create_db_profile(**FEMALE_PROFILE_2) # Calories = 1664

        self.eater1 = self.create_db_eater(self.prof1)
        self.eater2 = self.create_db_eater(self.prof2)

        self.dt1 = self.create_db_dishtype("half_day_dish", standard_calories = 1150)  # 2 dishes like that, and you're good !
        self.dt2 = self.create_db_dishtype("quarter_day_dish", standard_calories = 575)

        self.day = self.create_db_day()
        self.mealslot1 = self.create_db_mealslot(self.day, with_eaters=[self.eater1, self.eater2])
        self.mealslot2 = self.create_db_mealslot(self.day, with_eaters=[self.eater1])

        # Big mealslot : 1150 * 2 = 2300kcal
        self.dish1_1 = self.create_db_dish(self.mealslot1, self.dt1)
        self.dish1_2 = self.create_db_dish(self.mealslot1, self.dt1)

        # Small mealslot  575 kcal
        self.dish2 = self.create_db_dish(self.mealslot2, self.dt2)


    def test_ratios(self):
        res = self._computeMealProfileRatios([self.day])

        # structure = 2875kcal  (2*1150 + 575)
        # prof1 = 3185 kcal (ratio 1)
        # prof2 = 1664 kcal (ratio 0.5249)

        # meal ratio = 3185 / 2875 = 1.10
        # meal1 = 1.1 * (1 + 0.52) = 1.67 (rounded)
        # meal2 = 1.1 * 1 = 1.1 (rounded)
        self.assertEqual(res,
            {
                self.mealslot1.id: {
                    self.prof1.id: 0.9853,
                    self.prof2.id: 0.5147
                 },
                self.mealslot2.id: {
                    self.prof1.id: 1.0
                 },
            })


    def test_without_profile2(self):
        # Removing profile2 from meal1
        self.mealslot1.meal_slot_eaters.filter(eater=self.eater2).delete()

        res = self._computeMealProfileRatios([self.day])

        # Same as before, but :
        # meal1 = 1.1 * 1 = 1.1 (rounded)

        # Becomes same as meal2
        self.assertEqual(res,
            {
                self.mealslot1.id: {
                    self.prof1.id: 1.0
                 },
                self.mealslot2.id: {
                    self.prof1.id: 1.0
                 },
            })


    def _test_with_custom_meal(self, nb_calories):
         # Forced recipe has <nb_calories> kcal
        with patch.object(hippocrate.models.recipe.RecipeDataBuilder, 'get_or_build_many', lambda *x: [mock_recipe_data(nb_calories)]):
            # Changing dishtype 2 to a custom dish
            self.dt2.standard_calories = None
            self.dt2.name = DishType.DT_CUSTOM
            self.dt2.save()

            # Adding a dishrecipe in dish2
            recipe = self.create_db_recipe()
            self.create_db_dishrecipe(self.dish2, recipe, user=self.user, validated=True)

            res = self._computeMealProfileRatios([self.day])

        return res


    def test_custom_meal(self):
        """
        Test with a custom meal which has a few calories, and its effect
        """
        res = self._test_with_custom_meal(600)
        #
        # structure = 2300kcal variable, 600kcal static
        # prof1 = 3185 kcal (ratio 1)
        # prof2 = 1664 kcal (ratio 0.5249)

        # meal ratio = (3185 - 600) / 2300 = 1.12
        # meal1 = 1.12 * (1 + 0.52) = 1.7 (rounded)
        # meal2 = 1.12 * 1 = 1.12 (rounded)
        self.assertEqual(res,
            {
                self.mealslot1.id: {
                    self.prof1.id: 0.9853,
                    self.prof2.id: 0.5147
                },
                self.mealslot2.id: {
                    self.prof1.id: 1.0
                },
            })

    def test_custom_meal2(self):
        """
        Test with a custom meal which is really big. The meal ratio being very low, it should use a 0.5 default meal ratio
        """
        res = self._test_with_custom_meal(2500)

        #
        # structure = 2300kcal variable, 2000kcal static
        # prof1 = 3185 kcal (ratio 1)
        # prof2 = 1664 kcal (ratio 0.5249)

        # meal ratio = (3185 - 2500) / 2300 = 0.3  --> 0.5
        # meal1 = 0.5 * (1 + 0.52) = 0.76 (rounded)
        # meal2 = 1 [custom !] * 1 = 1
        self.assertEqual(res,
            {
                self.mealslot1.id: {
                    self.prof1.id: 0.6568,
                    self.prof2.id: 0.3432
                },
                self.mealslot2.id: {
                    self.prof1.id: 1.0
                },
            })


    def test_custom_meals_only(self):
        """
        Test that with only static dishes, structural ratio is 1
        """
        # Removing dish_type1 and using only dish_type2 (which is turned into custo in _test_with_custom_meal)
        self.dish2.dish_type = self.dt1
        self.dish2.save()
        # Removing eater2 from meal1
        self.mealslot1.eaters.filter(profile=self.prof2).delete()

        res = self._test_with_custom_meal(60000) # Excessively high value, but the ratio calculation shouldn't use it

        self.assertEqual(res,
            {
                self.mealslot1.id: {
                    self.prof1.id: 1.0
                },
                self.mealslot2.id: {
                    self.prof1.id: 1.0
                },
            })



class TestTheCustomExternal(BaseTestRatios):
    """
    Test with a custom meal which is switched to "away", with multiple eaters

    Ensure that there is no problem with ratio. (it used to crash)
    """

    def setUp(self):
        super().setUp()

        self.init_default_meal_type_settings()
        self.init_profile_metrics()
        self.init_db_profile_eater()
        self.init_default_nutrients()

        # Creating a default planning
        response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
        self.assertEqual(response.status_code, 201)
        reload_object(self.user)


        # Switching breakfast in "static mode"
        MealSlot.objects.filter(meal_type__name="Petit déjeuner").update(suggest=False)

        # Saying that we are away at this meal
        away = MealPlace.objects.get(key="away")
        MealSlot.objects.filter(meal_type__name="Petit déjeuner").update(meal_place=away)

    def test_the_custom_external(self):

        # Adding some new eaters
        response = self.client.post('/api/user/%i/profile' % self.user.id,
                                    {'creator': self.user.id,
                                     'nickname': 'other_person',
                                     'weight': 70,
                                     'height': 140,
                                     'birth_date': "2001-03-02T00:00:00Z",
                                     'sex': 'male'})
        self.assertEqual(response.status_code, 201)

        # Creating a planning
        response = self.client.post('/api/user/%i/add_days/2010-01-01' % self.user.id)
        self.assertEqual(response.status_code, 201)

        # Calculating ratios
        p = Planning.objects.get()
        days = list(p.days.all())
        res = self._computeMealProfileRatios(days)

        # Just checking it's not crashing
        self.assertEqual(len(res), 21) # 7*3 = 21 meals