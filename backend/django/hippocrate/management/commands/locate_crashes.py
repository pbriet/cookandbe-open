from django.core.management.base import BaseCommand
from optalim.mongo               import Mongo

from django.utils                import timezone
import datetime


class Command(BaseCommand):
    args = ''
    help = 'List last week darwin C++ crashes : user_id and time of execution'

    def handle(self, *args, **options):
        
        table = Mongo.log_table('crash_check')
        
        one_hour_ago   = timezone.now() - datetime.timedelta(hours=1)
        one_week_ago   = timezone.now() - datetime.timedelta(days=7)
        
        start_query = {'status': 'start', 'date': {'$gte': one_week_ago, '$lte': one_hour_ago}}
        started_keys = [row['problem_key'] for row in table.find(start_query)]
        
        end_query = {'status': 'end', 'date': {'$gte': one_week_ago}}
        ended_keys = [row['problem_key'] for row in table.find(end_query)]
        
        not_ended = set(started_keys).difference(ended_keys)
        
        for key in not_ended:
            row = table.find_one({"problem_key": key})
            print(row['date'].strftime("%Y-%m-%d %H:%M:%S"), " / user_id = ", row['user_id'])