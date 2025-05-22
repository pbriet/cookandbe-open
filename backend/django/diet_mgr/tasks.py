from celery import shared_task

from django.db.models           import Max

from common.date                import get_yesterday, date_to_datetime, tz_aware,\
                                       get_one_week_ago, today, add_days


import diet_mgr.import_all # required to initialize the diet handlers correctly
from diet_mgr.models            import Diet

from emailing.tools             import sendmail_template, MessageType


from paybox                     import LEVEL_PUBLIC_NAMES, Level
from paybox.controller          import get_user_best_tariff_str
from paybox.models              import UserSpecialOffer

from profile_mgr.models         import ProfileValue

from user_mgr.models            import User

import datetime

def apply_update(users):
    for user in users:
        user.diet_handler.update_metabolism()
        user.meta_planning.set_modified()

@shared_task
def update_metabolisms():
    """
    Once a day, apply the diet "update_metabolism" method to all the
    people who updated their weight yesterday
    """
    min_datetime = tz_aware(date_to_datetime(get_yesterday(), datetime.datetime.min.time())) # 00h00
    max_datetime = tz_aware(date_to_datetime(get_yesterday(), datetime.datetime.max.time())) # to 23h59

    last_weight_updates = ProfileValue.objects.filter(metric__key='weight',
                                                      time__gt=min_datetime,
                                                      time__lt=max_datetime).select_related('profile__creator__meta_planning')

    users_per_id = {}
    for weight_update in last_weight_updates:
        user = weight_update.profile.creator
        if user.main_profile_id == weight_update.profile_id:
            # There was an update on the main profile of the user

            if user.main_profile.forced_base_calories:
                # Calories are calculated elsewhere. Do not play with metabolism
                continue

            # Add to list of metabolism updates
            users_per_id[user.id] = user

    apply_update(users_per_id.values())


@shared_task
def remind_weight_update(simulate=False):
    """
    Once a day, retrieve all the users who made their last weight update X days ago precisely
    X depending on diet.

    And drop them an email.
    """
    min_datetime = tz_aware(date_to_datetime(get_yesterday(), datetime.datetime.min.time())) # 00h00
    max_datetime = tz_aware(date_to_datetime(get_yesterday(), datetime.datetime.max.time())) # to 23h59

    one_week_ago = get_one_week_ago()

    # User ids with the last update date of their weight
    user_data = User.objects.filter(main_profile__values__metric__key='weight').values('id', 'diet__key')
    user_data = user_data.annotate(Max('main_profile__values__time'), Max('days__date'))

    for user in user_data:
        last_day_generated = user['days__date__max']
        if last_day_generated is None or last_day_generated < one_week_ago:
            continue # This not an active user, don't bother him/her with weight

        diet_handler = Diet(key=user['diet__key']).handler_cls()
        last_update = user['main_profile__values__time__max']
        required_update_date = last_update + diet_handler.WEIGHT_REMINDER_INTERVAL

        if required_update_date > min_datetime and required_update_date < max_datetime:
            user = User.objects.get(pk=user['id'])

            sendmail_template(MessageType.NOTIFICATION, 'diet_mgr/templates/weight_update.html',
                        {'last_update': last_update}, "Pensez à mettre à jour votre poids",
                        users=[user], send_async=not simulate, tags=['weight_update'])



# 25/05/2015 : task is disabled ! No more special offer.
#@periodic_task(run_every=crontab(minute=0, hour=18))
def auto_diet_special_offer(simulate=False):
    """
    Offer a special reduction to those who :
    - signed up 1 week ago
    - want a premium/freedom diet, but haven't bought it
    """
    two_days_ago = add_days(today(), -2)
    min_datetime = tz_aware(date_to_datetime(two_days_ago, datetime.datetime.min.time())) # 00h00
    max_datetime = tz_aware(date_to_datetime(two_days_ago, datetime.datetime.max.time())) # to 23h59

    users = User.objects.filter(diet__min_subscription_level__gt=0,
                                date_joined__gte=min_datetime, date_joined__lte=max_datetime,
                                subscription_level=0).order_by('id')

    # Discount is valid during 2 days, until 23:59
    discount_valid_until = date_to_datetime(today() + datetime.timedelta(days=2), datetime.datetime.max.time())

    PREMIUM_ADVANTAGES = {
        # Level.FREEDOM: ["<b>Une alimentation sur mesure</b>, à la pointe de la nutrition",
        #                 "Une personnalisation <b>illimitée</b>",
        #                 "Le <b>rééquilibrage automatique</b> : mettez la recette de votre choix, Cook&Be rééquilibre votre journée/semaine  !"],
        Level.PREMIUM: ["<b>Une alimentation sur mesure</b>, à la pointe de la nutrition",
                        "Le service d'un <b>diététicien en ligne</b>, prêt à répondre à vos questions"],
    }

    for user in users:
        UserSpecialOffer.objects.create(discount=50, until=discount_valid_until, user=user)
        level = user.diet.get_min_subscription_level()
        best_tariff = get_user_best_tariff_str(user, level)

        sendmail_template(MessageType.NOTIFICATION, 'diet_mgr/templates/special_offer.html',
                    {'diet': user.diet,
                     'best_tariff': best_tariff,
                     'subscription_name': LEVEL_PUBLIC_NAMES[level],
                     'advantages': PREMIUM_ADVANTAGES[level]
                    }, "-50%% sur %s" % user.diet.email_title,
                    users=[user], send_async=not simulate, tags=['diet_special_offer'])
