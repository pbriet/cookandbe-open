
from common.mock_tools          import fake_today_decorator
from common.test                import TestAPIWithLogin


class TestPlanificationStatus(TestAPIWithLogin):

    def check_planification_status(self, planned, suggested, days_not_in_list, expected_code = 200):
        print("access token is", self.access_token)
        response = self.client.get('/api/user/%i/planification_status' % self.user.id)
        print(response.data)
        self.assertEqual(response.status_code, expected_code)
        if response.status_code != 200:
            return
        if planned is None:
            self.assertTrue(response.data["planned_to"] is None)
        else:
            self.assertEqual(response.data["planned_to"].strftime("%Y-%m-%d"), planned)
        if suggested is None:
            self.assertTrue(response.data["suggested_to"] is None)
        else:
            self.assertEqual(response.data["suggested_to"].strftime("%Y-%m-%d"), suggested)
        self.assertTrue(response.data["days_not_in_list"] is days_not_in_list)

    @fake_today_decorator(2012, 5, 5)
    def test_planification_status(self):
        self.check_planification_status(None, None, False)

        shopping_list = self.create_db_shopping_list()

        # Past days
        for date in ("2012-05-01", "2012-05-02"):
            self.create_db_day(date, skipped=False)
        self.check_planification_status(None, None, False)

        # Days in shopping list
        for date in ("2012-05-05", "2012-05-06", "2012-05-07"):
            self.create_db_day(date, skipped=False, shopping_list=shopping_list) # Day in shopping_list
        self.check_planification_status("2012-05-07", "2012-05-07", False)

        # No day (08/05/2012)
        self.create_db_day("2012-05-09", skipped=True) # Day skipped
        self.create_db_day("2012-05-10", skipped=None) # Day not validated
        self.check_planification_status("2012-05-09", "2012-05-07", False)

        # Days validated, not in lists
        for date in ("2012-05-11", "2012-05-12"):
            self.create_db_day(date, skipped=False)

        self.check_planification_status("2012-05-12", "2012-05-12", True)

    def test_planification_status_rights(self):
        self.another    = self.create_db_user(name = "someone",                             auto_create_main_profile = True)
        self.admin      = self.create_db_user(name = "god",     roles = ("admin", ),        auto_create_main_profile = True)
        self.dietician  = self.create_db_user(name = "thierry", roles = ("dietician", ),    auto_create_main_profile = True)

        expected = (
            (None,              401), # anonymous
            (self.user,         200),
            (self.another,      403),
            (self.admin,        403),
            (self.dietician,    403),
        )
        for user, expected_code in expected:
            print(user and user.first_name)
            self.change_user(user)
            self.check_planification_status(None, None, False, expected_code)

    def test_empty_planification_status(self):
        """
        Default, with no days
        """
        self.check_planification_status(None, None, False)
