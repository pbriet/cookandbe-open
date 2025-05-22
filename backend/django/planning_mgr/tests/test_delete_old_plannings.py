from planning_mgr.models import Planning, Day
from common.test import OptalimTest

import datetime
from django.utils import timezone

from planning_mgr.tasks import delete_old_plannings

class TestDayForceSuggest(OptalimTest):
    def setUp(self):
        super().setUp()
        self.init_db_profile_eater()

        # Create a planning that is 3 weeks old, over 2 weeks
        three_weeks_ago = timezone.now() - datetime.timedelta(days=3*7)
        self.planning1 = self.create_db_planning(nb_days = 14, start_date = three_weeks_ago, creation_date=three_weeks_ago)

        user2 = self._create_db_user("user2@cookandbe.com")

        # Create a planning thats is 2 weeks old
        two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
        self.planning2 = self.create_db_planning(user=user2, nb_days=7, start_date=two_weeks_ago, creation_date=two_weeks_ago)

        user3 = self._create_db_user("user3@cookandbe.com")

        # Create a planning that is one month old
        one_month_ago = timezone.now() - datetime.timedelta(days=30)
        self.planning3 = self.create_db_planning(user=user3, nb_days=7, start_date=one_month_ago, creation_date=one_month_ago)

    def test_delete_old_plannings(self):

        delete_old_plannings()

        planning_ids = sorted(list(planning.pk for planning in Planning.objects.all()))

        self.assertEqual(planning_ids, [self.planning1.pk, self.planning2.pk])

        self.assertEqual(Day.objects.count(), 21)