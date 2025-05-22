from collections                import defaultdict

from django.db.models           import Count

from rest_framework.decorators  import api_view, permission_classes
from rest_framework.response    import Response

from common.date                import date_to_datetime, tz_aware
from common.decorators          import api_arg
from common.math                import round_to_closest
from common.permissions         import Allow

from paybox.models              import Transaction, Subscription

from planning_mgr.models        import Day

from shopping_mgr.models        import ShoppingList

from user_mgr.models            import User, ConfigStage, PromotionalCode
from user_mgr.serializers       import PromotionalCodeSerializerWithStats

import datetime

@api_view(['GET'])
@api_arg('from_value', datetime.date)
@api_arg('to_value', datetime.date)
def api_retrieve_stats(request, from_value, to_value):
    
    from_value = tz_aware(date_to_datetime(from_value, datetime.datetime.min.time()))
    to_value = tz_aware(date_to_datetime(to_value, datetime.datetime.max.time()))
    
    # Same length period [before-from] = [from-to]
    previous_period_from = from_value - (to_value - from_value)
    
    tunnel = {}
    old_users = {}
    
    for period_key, from_d, to_d in [('previous', previous_period_from, from_value),
                                     ('period', from_value, to_value)]:
                                        
        period_tunnel = {}
        for key in ('subscriptions', 'no_completion', 'some_completion', 'full_completion',
                    'validated_day', 'shopping_list', 'old_users_active', 'click_buy', 'money'):
            period_tunnel[key] = 0
        
        users = User.objects.filter(date_joined__gte=from_d,
                                    user_roles=None,
                                    date_joined__lte=to_d).prefetch_related("config_stage_completions",
                                                                            "days",
                                                                            "shopping_lists",
                                                                            "main_profile",
                                                                            "profile_set",
                                                                            "subscriptions__transactions")
        users = list(users)
        nb_stages = ConfigStage.objects.count()
        
        for user in users:
            period_tunnel['subscriptions'] += 1
            nb_user_completion = user.config_stage_completions.count()
            if nb_user_completion <= 1:
                period_tunnel['no_completion'] += 1
            else:
                period_tunnel['some_completion'] += 1
                if nb_user_completion == nb_stages:
                    period_tunnel['full_completion'] += 1
            for day in user.days.all():
                if day.is_validated():
                    period_tunnel['validated_day'] += 1
                    break
            if len(user.shopping_lists.all()) > 0:
                period_tunnel['shopping_list'] += 1
            if len(user.subscriptions.all()) > 0:
                if sum(s.total_amount for s in user.subscriptions.all()) > 0:
                    period_tunnel['click_buy'] += 1
                    for subscription in user.subscriptions.all():
                        for transaction in subscription.transactions.all():
                            if transaction.status == Transaction.STATUS_CONFIRMED:
                                period_tunnel['money'] += 1
        
        old_users_period = {}
        # Users that joined before date, and were active during this period
        old_active_users = User.objects.filter(days__creation_date__gte=from_d,
                                               days__creation_date__lte=to_d,
                                               days__skipped=False,
                                               user_roles=None,
                                               date_joined__lt=from_d).\
                                         prefetch_related('subscriptions').distinct()
        old_active_users = list(old_active_users)
        
        old_users_period['nb'] = len(old_active_users)
        old_users_period['nb_with_subscriptions'] = 0
        
        for active_user in old_active_users:
            for subscription in active_user.subscriptions.all():
                if subscription.total_amount > 0 and subscription.start_date <= to_d.date() and subscription.end_date >= from_d.date():
                    old_users_period['nb_with_subscriptions'] += 1
        
        
        old_users_period['shopping_lists'] = ShoppingList.objects.filter(creation_date__gte=from_d,
                                            creation_date__lte=to_d,
                                            user__in=old_active_users).count()
        
        old_users_period['planned_days'] =\
            Day.objects.filter(creation_date__gte=from_d,
                               creation_date__lte=to_d,
                               skipped=False,
                               user__in=old_active_users).count()
        
        
        if period_key == 'period':
            population = analyse_population(users, nb_stages)
            diet_stats = get_diet_stats(users, from_value, to_value)
        
        tunnel[period_key] = period_tunnel
        old_users[period_key] = old_users_period
        
    return Response({'tunnel': tunnel, 'population': population, 'old_users': old_users,
                     'diet_stats': diet_stats}, 200)

def get_diet_stats(users, from_date, to_date):
    """
    Returns stat on diets : which diets, and which percentage are paying
    """
    res = {"diets": defaultdict(int),
           "paying": defaultdict(int)}
    
    for user in users:
        res["diets"][user.diet.key] += 1
        for sub in user.subscriptions.all():
            if sub.start_date <= to_date.date() and sub.end_date >= from_date.date() and sub.total_amount > 0:
                res["paying"][user.diet.key] += 1
    
    return res
    

def analyse_population(users, nb_stages):
    """
    From a list of users, give some metrics
    """
    
    per_gender = defaultdict(int)
    per_age = defaultdict(int) # 20 / 30 / 40 / ...
    per_imc = defaultdict(int)
    per_nb_people = defaultdict(int)
    
    for user in users:
        profile = user.main_profile
        per_gender[profile.sex] += 1
        per_age[round_to_closest(profile.age, 10)] += 1
        if profile.height is not None and profile.weight is not None:
            per_imc[profile.imc_caption] += 1
        
        if user.config_stage_completions.count() == nb_stages:
            per_nb_people[user.profile_set.count()] += 1

    return {'gender': list(per_gender.items()), 'age': list(per_age.items()),
            'imc': list(per_imc.items()), 'nb_people': list(per_nb_people.items())}


@api_view(['GET'])
@permission_classes((Allow('admin'),))
def api_promo_code_stats(self):
    """
    Returns the list of promo codes with their stats
    """
    promo_codes = PromotionalCode.objects.all().annotate(nb_users=Count('users_who_consumed')).filter(nb_users__gt=0).order_by('-nb_users')

    return Response(PromotionalCodeSerializerWithStats(promo_codes, many=True).data)
