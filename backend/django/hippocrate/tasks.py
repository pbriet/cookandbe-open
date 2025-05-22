from celery import shared_task
from optalim.mongo              import Mongo
from django.utils               import timezone
import datetime

@shared_task
def remove_old_logs():
    """
    Remove old logs from Mongo DB
    """
    two_months_ago = timezone.now() - datetime.timedelta(days=60)

    for table_name in ('crash_check', 'darwin_times', 'darwin_quality'):

        table = Mongo.log_table(table_name)

        table.delete_many({"date": {"$lte": two_months_ago}})


    indicators_table = Mongo.hp_table("indicators")
    indicators_table.delete_many({"date": {"$lte": two_months_ago}})

    indicators_v2_table = Mongo.hp_table("indicators_v2")
    indicators_v2_table.delete_many({"date": {"$lte": two_months_ago}})