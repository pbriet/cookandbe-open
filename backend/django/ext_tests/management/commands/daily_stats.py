from django.core.management.base        import BaseCommand
from user_mgr.models import User
from common.date import add_days, date_to_datetime
from optalim.mongo import Mongo
from optalim.settings import APP_BRAND_NAME
from datetime import date, datetime
from emailing import MessageType
from emailing.tools import sendmail

import copy

class Command(BaseCommand):
    args = ''
    help = 'Generates daily stats on usage. Send an email every 1st of each month'

    def handle(self, *args, **options):

        nb_users = User.objects.filter(access_closed=False).count()

        # Removing two accounts : Cook&Be admin account, Customer admin account
        nb_users -= 2
        today = date_to_datetime(date.today())

        table = Mongo.log_table("usage")
        if len(list(table.find({'date': today}))) > 0:
            print("Already has an entry for %s" % today.strftime("%Y-%m-%d"))
        else:
            print("Adding entry in Mongo")
            table.insert_one({'date': today, 'nb_users': nb_users})

        if today.day == 1:
            print("Day 1 : reporting !")
            # Sending report for last month usage
            yesterday = add_days(today, -1)
            last_month_begin = datetime(yesterday.year, yesterday.month, 1)

            usages = table.find({'date': {'$gte': last_month_begin, '$lte': yesterday}}).sort('date', 1)

            usage_by_day = ""
            nb_total = 0
            for usage in usages:
                usage_by_day += "<li>%s : %s</li>" % (usage['date'].strftime("%d/%m"), usage['nb_users'])
                nb_total += usage['nb_users']

            message = "Utilisation du service %s pour le mois de %s" % (APP_BRAND_NAME, yesterday.strftime("%B"))

            message += "<br/><br/>TOTAL (user.j.) : %s" % nb_total
            message += "<br/>TOTAL (user.m.) : %s" % round(nb_total / yesterday.day)

            message += "<br/><ul>"
            message += usage_by_day
            message += "</ul>"

            sendmail(MessageType.REALTIME, "Rapport d'usage Cook&Be %s" % APP_BRAND_NAME,
                     message, email="briet.pascal@gmail.com", emitter="Cook&Be facturation")





