from django.core.management.base import BaseCommand
from django.utils import timezone

from collections                import defaultdict
from common.date                import parse_date_str
from paybox.models              import Transaction
from user_mgr.models            import User

import math
import datetime

class Command(BaseCommand):
    args = 'start_date end_date'
    help = 'Gives stats on fidelity of users (who joined between [2 months ago - 1 month ago])'

    def handle(self, *args, **options):
        if len(args) >= 1:
            start_date = parse_date_str(args[0])
        else:
            start_date = (timezone.now() - datetime.timedelta(days=60)).date()
        if len(args) >= 2:
            end_date = parse_date_str(args[1])
        else:
            end_date = start_date + datetime.timedelta(days=30)
        fidelity = defaultdict(int)
        active = 0
        
        user_ids = set()
        for user in User.objects.prefetch_related('days').filter(date_joined__gte=start_date,
                                                                 date_joined__lte=end_date,
                                                                 user_roles=None):
            user_ids.add(user.id)
            last_date = user.date_joined
            for day in user.days.filter(skipped=False):
                last_date = max(last_date, day.creation_date)
            
            if (datetime.date.today() - last_date.date()).days < 10:
                active += 1
                continue
            
            nb_days = (last_date - user.date_joined).days
            
            fidelity[nb_days] += 1
        
        
        nb_transactions_user, nb_transactions_in_period, nb_transactions_within_1_month = 0, 0, 0
        for transaction in Transaction.objects.select_related('subscription').filter(created_at__gte=start_date,
                                                                                     status=Transaction.STATUS_CONFIRMED):
            if transaction.subscription.user_id in user_ids:
                nb_transactions_user += 1
                if transaction.created_at.date() <= end_date + datetime.timedelta(days=40):
                    nb_transactions_within_1_month += 1
            if transaction.created_at.date() <= end_date:
                nb_transactions_in_period += 1
    
        # Rounding to 5 days
        durations = sorted(fidelity.keys())
        for d in durations:
            if d % 5 != 0:
                fidelity[5 * math.ceil(d // 5)] += fidelity[d]
                del fidelity[d]
        
        
        total = sum(fidelity.values()) + active
        print("%i inscriptions entre le %s et le %s" % (total, start_date, end_date))
        print("")
        print("DUREE DE VIE (activité sur day_planner)")
        print("")
        for key in sorted(fidelity.keys()):
            value = fidelity[key]
            if key == 0:
                key = "Aucun retour"
            else:
                key = "- de %i jours" % key
                
            print("%s => %s (%s%%)" % (key, value, round((100.*value)/total, 1)))
        
        print("")
        print("Actifs récemment : %s (%s%%)" % (active, round((100.*active)/total, 1)))
        print("Utilisateurs payants aujourd'hui : %s (%s%%)" % (nb_transactions_user, round((100.*nb_transactions_user)/total, 1)))
        print("Utilisateurs payants sous 1 mois : %s (%s%%)" % (nb_transactions_within_1_month, round((100.*nb_transactions_within_1_month)/total, 1)))
        print("Paiements pendant période : %s" % nb_transactions_in_period)