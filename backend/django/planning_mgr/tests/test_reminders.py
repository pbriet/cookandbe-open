from common.model           import reload_object
from common.test                    import OptalimTest
from common.mock_tools              import fake_today_decorator

from emailing                       import MessageType

from planning_mgr.controller.day    import pick_best_recipes_from_day, pick_recipe_to_evaluate
from planning_mgr.models            import DishType
from planning_mgr.tasks             import send_planning_reminder, send_meals_reminder, send_meals_suggestion
from planning_mgr.tests             import TestWithFilledPlanning

from mock                           import patch

import planning_mgr.tasks
import datetime
import re

class iTestPlanningReminder(OptalimTest):

    CREATE_LAST_DAY = True

    def setUp(self):
        super().setUp()
        # Inactive users
        for i in range(5):
            self.create_db_user()

        dish_type = self.create_db_dishtype()

        # 2 days - 1 day gap - then 2 other days
        self.day1 = self.create_db_day("2012-05-01", creation_date=datetime.date(2012, 4, 30), skipped=False)
        self.day2 = self.create_db_day("2012-05-02", creation_date=datetime.date(2012, 4, 30), skipped=False)
        self.day3 = self.create_db_day("2012-05-04", creation_date=datetime.date(2012, 5, 1), skipped=False)
        if self.CREATE_LAST_DAY:
            self.day4 = self.create_db_day("2012-05-05", creation_date=datetime.date(2012, 5, 1), skipped=False)

        days = [self.day1, self.day2, self.day3]
        if self.CREATE_LAST_DAY:
            days.append(self.day4)

        recipe = self.create_db_recipe()

        # Filling all the days with 1 meal_slot at home and suggested, 1 dish, and 1 dishrecipe
        for day in days:
            meal_slot = self.create_db_mealslot(day)
            dish      = self.create_db_dish(meal_slot, dish_type)
            self.create_db_dishrecipe(dish, recipe, validated=True)

    @patch('planning_mgr.tasks.sendmail_template')
    def _assert_send_email(self, last_day_date, mock_sendmail_template):
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 1)

        args, kargs = mock_sendmail_template.call_args
        self.assertEqual(args,
                        (MessageType.NOTIFICATION, 'planning_mgr/templates/planning_reminder.html',
                        {'date': last_day_date},
                        "Rappel: Votre planning de repas se termine demain"))

        self.assertEqual(len(kargs['users']), 1)
        self.assertEqual(kargs['users'][0].id, self.user.id)

class TestStandardPlanningReminder(iTestPlanningReminder):

    @fake_today_decorator(2012, 4, 25)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_early_check(self, mock_sendmail_template):
        # No reason to send an email at this date, long before planned days
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 1)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_gap_check(self, mock_sendmail_template):
        # Shouldn't send an email when there is a gap
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 4)
    def test_this_is_time(self):
        # Should send an email when tomorrow is the last planned day
        self._assert_send_email(datetime.date(2012, 5, 5))

    @fake_today_decorator(2012, 5, 4)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_dontsend_cause_tomorrow_is_skipped(self, mock_sendmail_template):
        """
        The reminder should have been sent before
        """
        self.day4.skipped = True
        self.day4.save()
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 4)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_dontsend_cause_tomorrow_is_not_visited(self, mock_sendmail_template):
        """
        The reminder should have been sent before
        """
        self.day4.skipped = None
        self.day4.save()
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 3)
    def test_this_is_time_with_skipped(self):
        """
        Next days is planned
        The following day is created, but skipped -> send a reminder
        """
        self.day4.skipped = True
        self.day4.save()

        self._assert_send_email(datetime.date(2012, 5, 4))

    @fake_today_decorator(2012, 5, 3)
    def test_this_is_time_with_not_visited(self):
        """
        Next days is planned
        The following day is created, but not visited -> send a reminder
        """
        self.day4.skipped = None
        self.day4.save()

        self._assert_send_email(datetime.date(2012, 5, 4))

    @fake_today_decorator(2012, 5, 5)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_this_is_too_late(self, mock_sendmail_template):
        # No mail on the last day
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 6)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_this_is_too_late(self, mock_sendmail_template):
        # No mail on the the next days
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 4)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_i_just_planned_it(self, mock_sendmail_template):
        # No mail if the last day was planned no later than 24h
        # Day 4 was planned 6h ago only !
        self.day4.creation_date = datetime.datetime.now() - datetime.timedelta(hours=6)
        self.day4.save()
        send_planning_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

class TestSoloDayPlanningReminder(iTestPlanningReminder):
    """
    Testing planning reminder with only one solo day with empty days before and after
    """
    CREATE_LAST_DAY = False

    @fake_today_decorator(2012, 5, 3)
    def test_this_is_time(self):
        # Should send an email when tomorrow is the last planned day
        self._assert_send_email(datetime.date(2012, 5, 4))

class TestMealsReminder(OptalimTest, TestWithFilledPlanning):

    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        self.init_default_nutrients()
        super().setUp()
        self.init_db_profile_eater()
        # Empty day
        self.create_db_day("2012-05-08")
        # Filled day
        self.init_day(self.create_db_day("2012-05-07", skipped=False))
        # Filled day, but not validated
        self.init_day(self.create_db_day("2012-05-09", skipped=None))

    @fake_today_decorator(2012, 5, 6)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_do_not_send_when_no_day(self, mock_sendmail_template):
        # No mail when there is no day !
        send_meals_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 8)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_do_not_send_day_empty(self, mock_sendmail_template):
        # No mail when day is empty
        send_meals_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 9)
    @patch('planning_mgr.tasks.sendmail_template')
    def test_do_not_send_unvalidated_day(self, mock_sendmail_template):
        # No mail when there is no dishrecipe validated
        send_meals_reminder()
        self.assertEqual(mock_sendmail_template.call_count, 0)

    @fake_today_decorator(2012, 5, 7)
    @patch('emailing.tools.sendmail')
    def test_send_it_baby(self, mock_sendmail):
        # This is the one : one email should be sent !
        send_meals_reminder()
        self.assertEqual(mock_sendmail.call_count, 1)

        args, kargs = mock_sendmail.call_args
        # (subject, message, email, users, emitter, tags=tags, defer=defer, eta=eta, expires=expires)
        self.assertEqual(args[1], "Vos repas équilibrés de Lundi")

        self.assertEqual(len(kargs['users']), 1)
        self.assertEqual(kargs['users'][0].id, self.user.id)
        self.assertTrue(kargs['send_async'])

        content = args[2].replace('\r', '').replace('\n', ' ')
        content = re.sub(' +', ' ', content)
        self.assertTrue("app.localhost/day/2012-05-07" in content)
        self.assertTrue("<b>carrots</b> - 4 big <span style=\"color: #999999;\">(16 g)</span>" in content)


class TestBestRecipeSelection(OptalimTest):
    """
    Test the algorithm that selects the best recipes within a day,
    to put them in the suggestions reminder email
    """
    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()

        self.unique_food = self.create_db_food("food")

        self.full_course = DishType.objects.get(name=DishType.DT_FULL_COURSE)
        snack = DishType.objects.get(name=DishType.DT_SNACK_SWEET)

        self.basic_recipe = self.create_db_recipe("basic", dish_types=[self.full_course])
        self.basic_snack = self.create_db_recipe("basic snack", dish_types=[snack])
        self.nice_recipe = self.create_db_recipe("nice recipe", dish_types=[self.full_course, snack])
        self.nice_recipe_photo = self.create_db_recipe("nice recipe with photo", dish_types=[self.full_course])
        self.really_nice_recipe_photo = self.create_db_recipe("really nice recipe with photo", dish_types=[self.full_course])

        for recipe in [self.basic_recipe, self.basic_snack, self.nice_recipe, self.nice_recipe_photo,
                       self.really_nice_recipe_photo]:
            # Recipes have photo
            recipe.photo = "/home/toto/plop.jpg"
            recipe.save()

        self.great_recipe_no_photo = self.create_db_recipe("no photo", dish_types=[self.full_course, snack])

        self.nice_recipe_photo.auto_photo = False
        self.nice_recipe_photo.save()

        self._add_ingredients(self.basic_recipe, 1)
        self._add_ingredients(self.basic_snack, 1)
        self._add_ingredients(self.nice_recipe, 5)
        self._add_ingredients(self.nice_recipe_photo, 8)
        self._add_ingredients(self.really_nice_recipe_photo, 25)
        self._add_ingredients(self.great_recipe_no_photo, 7)

        def _build_day(content, date):
            day = self.create_db_day(date=date)
            for ms_content in content:
                ms = self.create_db_mealslot(day)
                for recipe in ms_content:
                    dish = self.create_db_dish(ms, dish_type=self.full_course)
                    self.create_db_dishrecipe(dish, recipe)
            return day

        DAY1_CONTENT = [(self.basic_recipe, self.nice_recipe), (self.nice_recipe_photo, self.basic_snack)]
        DAY2_CONTENT = [(self.really_nice_recipe_photo, )]
        self.DAY1_RECIPES = DAY1_CONTENT[0] + DAY1_CONTENT[1]

        self.day1 = _build_day(DAY1_CONTENT, datetime.date(2012, 1, 1))
        self.day2 = _build_day(DAY1_CONTENT, datetime.date(2012, 1, 2))

    def _add_ingredients(self, recipe, nb_ingredients):
        for i in range(nb_ingredients):
            self.create_db_ingredient(recipe, self.unique_food, 100)

    def test_best_recipe_full(self):
        res = pick_best_recipes_from_day(self.day1, max_nb=10, with_score=True, min_rating=None)

        # Replacing recipes by their name
        res = [(r[0].name, r[1]) for r in res]

        self.assertEqual(res,
                         [("nice recipe with photo", 13),
                          ("nice recipe", 5),
                          ("basic", -7),
                          ("basic snack", -10)])

    def _test_simple_pick(self, day, expected, min_rating=None):
        """
        Standard call to pick_best_recipes_from_day
        Compare result with a list of recipe names
        """
        res = pick_best_recipes_from_day(day, min_rating = min_rating)
        # Replacing recipes by their name
        res = [r.name for r in res]

        self.assertEqual(sorted(res), sorted(expected))

    def test_recipe_to_evaluate(self):
        """
        Test of choice of recipe to evaluate
        """
        res = pick_recipe_to_evaluate(self.day1)
        # All recipes are compliant
        self.assertTrue(res.id is not None)

        # Let's say all of them don't have photos
        for recipe in self.DAY1_RECIPES:
            recipe.photo.delete(save=True)

        res = pick_recipe_to_evaluate(self.day1)
        # No recipe is compliant
        self.assertTrue(res is None)

        # Let's put back a photo on basic_recipe (too few ingredients) and nice_recipe
        for recipe in (self.basic_recipe, self.nice_recipe):
            recipe.photo = "/home/toto/plop.jpg"
            recipe.save()
        res = pick_recipe_to_evaluate(self.day1)
        self.assertEqual(res.id, self.nice_recipe.id)

        # Now let's rate nice_recipe
        self.create_db_rating(self.nice_recipe, self.user, 3)
        res = pick_recipe_to_evaluate(self.day1)
        self.assertTrue(res is None)


    def _create_day1_meal_dish(self, meal_kargs, recipe):
        """
        Create on day1 a meal, a dish and a dishrecipe
        """
        ms = self.create_db_mealslot(self.day1, **meal_kargs)
        dish = self.create_db_dish(ms, dish_type=self.full_course)
        self.create_db_dishrecipe(dish, recipe)


    def test_best_recipe_simple(self):
        self._test_simple_pick(self.day1,
                              ["nice recipe with photo", "nice recipe"])

        self._test_simple_pick(self.day1, ["nice recipe with photo"], min_rating=10)


    def test_with_duplicate(self):
        # Adding twice the same recipe in a day
        self._create_day1_meal_dish({}, self.nice_recipe_photo)
        self._test_simple_pick(self.day1,
                              ["nice recipe with photo", "nice recipe"])

    def test_in_external_meal(self):
        # test that a great recipe that is in an external meal is NOT picked
        self._create_day1_meal_dish({'meal_place': self.places['away']}, self.really_nice_recipe_photo)
        self._test_simple_pick(self.day1,
                              ["nice recipe with photo", "nice recipe"])

    def test_in_static_meal(self):
        # test that a great recipe that is in a not suggested meal is NOT picked
        self._create_day1_meal_dish({'suggest': False}, self.really_nice_recipe_photo)
        self._test_simple_pick(self.day1,
                              ["nice recipe with photo", "nice recipe"])

    def test_even_better(self):
        # test that an even better recipe is picked up
        self._create_day1_meal_dish({}, self.really_nice_recipe_photo)
        self._test_simple_pick(self.day1,
                              ["really nice recipe with photo", "nice recipe with photo"])


class TestMealSuggestions(OptalimTest, TestWithFilledPlanning):
    """
    Test the task that send meal suggestions to users
    """
    CREATE_DEFAULT_USER = False
    def setUp(self):
        super().setUp()
        self._init_basic_users()

        # User 0 has a planned day tomorrow
        p = self.create_db_planning(user=self.users[0])
        self.create_db_day("2012-05-02", skipped=False, user=self.users[0], planning=p)

        # User 2 has a planned day today
        p = self.create_db_planning(user=self.users[2])
        self.create_db_day("2012-05-01", skipped=False, user=self.users[2], planning=p)

        # User 3 has a day created tomorrow and today, but not "planned"
        p = self.create_db_planning(user=self.users[3])
        for i in range(1, 8):
            self.create_db_day("2012-05-0%i" % i, skipped=None, user=self.users[3], planning=p)

        # User 4 has "skipped days !"
        p = self.create_db_planning(user=self.users[4])
        for i in range(1, 8):
            self.create_db_day("2012-05-0%i" % i, skipped=True, user=self.users[4], planning=p)

        # User 5 is disabled
        self.users[5].enabled = False
        self.users[5].save()

        # User 6 disabled emails
        self.users[6].mail_suggestion = False
        self.users[6].save()

        dt = self.create_db_dishtype()

        self._fake_recipe = self.create_db_recipe("plop", author=self.users[0], dish_types=[dt])

    def _init_basic_users(self):
        """
        Create users with basic eaters/profile/metaplannings
        """
        self.users = [self.create_db_user("user%i" % i) for i in range(7)]
        for user in self.users:
            self.create_db_meta_planning(user, with_n_days=7)
            profile = self.create_db_profile(creator=user)
            self.create_db_eater(profile, user)

    @patch('planning_mgr.tasks.sendmail_template')
    @patch('hippocrate.controls.generate.optimize_days')
    @fake_today_decorator(2012, 5, 1)
    def test_send_meal_suggestions(self, mock_optimize_days, mock_sendmail):

        def _fake_pick_recipes(*a, **k): return [self._fake_recipe]

        with patch.object(planning_mgr.tasks, 'pick_best_recipes_from_day', _fake_pick_recipes):

            send_meals_suggestion()

            self.assertEqual(mock_sendmail.call_count, 2)

            # Users 1 and 3 should receive a reminder
            user_ids = [kargs['users'][0].id for args, kargs in mock_sendmail.call_args_list]
            self.assertEqual(sorted(user_ids), [self.users[1].id, self.users[3].id])

            args1, kargs1 = mock_sendmail.call_args_list[0]
            self.assertEqual(args1[1], 'planning_mgr/templates/meals_suggestion.html')
            self.assertEqual(args1[2]['date'], datetime.date(2012, 5, 1))
            self.assertEqual(len(args1[2]['recipes']), 1)
            self.assertEqual(args1[2]['recipes'][0]['name'], 'plop')
            self.assertEqual(len(kargs1['users']), 1)
            self.assertEqual(kargs1['users'][0].id, self.users[1].id)

            title = args1[3]
            self.assertEqual(title, "Mardi 1 : plop")

            # Days should have been created for user1 only
            self.assertEqual(mock_optimize_days.call_count, 1)
            args, kargs = mock_optimize_days.call_args_list[0]

            # Created 7 days starting 01/05/2012
            self.assertEqual(len(args[0]), 7)
            self.assertEqual(args[0][0].date, datetime.date(2012, 5, 1))
            self.assertEqual(kargs["start_from_existing_solution"], False)
            self.assertEqual(kargs["minimize_change"], None)
            self.assertEqual(kargs["current_day"].date, datetime.date(2012, 5, 1))

            # Checking that now User1 has a day on May 2nd
            day = self.users[1].days.filter(date=datetime.date(2012, 5, 1))
            self.assertEqual(len(day), 1)
            day = day[0]
            self.assertEqual(day.skipped, None)
            self.assertEqual(day.shopping_list_id, None)
