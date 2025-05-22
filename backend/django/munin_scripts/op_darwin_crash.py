#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from optalim.mongo      import Mongo

from django.utils       import timezone
import datetime

class DarwinCrashes(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Darwin crashes (last hour)")
        print('graph_category darwin')
        print('graph_args --lower-limit 0')
        print("nb_crashes.draw LINE1")
        print("nb_crashes.label Number of crashes")
        print("nb_crashes.warning 0:5")
        print("nb_crashes.critical 0:20")

    def apply_values(self):
        table = Mongo.log_table('crash_check')

        one_hour_ago   = timezone.now() - datetime.timedelta(hours=1)
        five_mins_ago  = timezone.now() - datetime.timedelta(minutes=5)

        start_query = {'status': 'start', 'date': {'$gte': one_hour_ago, '$lte': five_mins_ago}}
        started_keys = [row['problem_key'] for row in table.find(start_query)]

        end_query = {'status': 'end', 'date': {'$gte': one_hour_ago}}
        ended_keys = [row['problem_key'] for row in table.find(end_query)]

        not_ended = len(set(started_keys).difference(ended_keys))

        print("nb_crashes.value %i" % not_ended)

DarwinCrashes().apply()
