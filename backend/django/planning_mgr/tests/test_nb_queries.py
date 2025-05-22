from common.model                       import reload_object
from common.test                        import TestAPIWithLogin
from planning_mgr.controller.planning   import build_planning

import datetime

class HippocrateNgQueriesTest(TestAPIWithLogin):

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        self.init_db_profile_eater()

    def test_meta_to_planning(self):

        # Yay...  264 queries...
        with self.assertNumQueries(264):
            # Initializing the default metaplanning
            # This requires a few queries... and that's ok.
            response = self.client.post('/api/user/%i/default_planning/init' % self.user.id)
            self.assertEqual(response.status_code, 201)
            reload_object(self.user)

        with self.assertNumQueries(227):
            # Creating a week
            build_planning(self.user, datetime.date(2014, 9, 1), 7)

