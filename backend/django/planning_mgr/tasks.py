
from celery import shared_task

from django.db                  import transaction
from django.db.models           import Max
from django.template.defaultfilters     import date as date_django_filter
from django.utils               import timezone

from emailing.tools             import sendmail_template, MessageType

from common.date                import get_tomorrow, today, get_yesterday

from hippocrate.controls.generate     import suggest_if_required

from optalim.main               import OptalimWebsite
from optalim.mongo              import Mongo
from optalim.settings           import (DEBUG, TESTING, ENABLE_MEALS_SUGGESTION,
                                        ENABLE_PLANNING_REMINDER, ENABLE_MEALS_REMINDER)

from planning_mgr.models        import Day, Planning, NotNow
from planning_mgr.controller.day    import pick_best_recipes_from_day, pick_recipe_to_evaluate, get_planned_days
from planning_mgr.serializers   import DayToFillSerializer

from recipe_mgr.models          import Recipe
from recipe_mgr.serializers     import PartialRecipeSerializer

from user_mgr.models            import User

import datetime

@shared_task
def send_planning_reminder():
    """
    Every day at 6pm, send a reminder to people whose planification is finished the next day
    """
    if not ENABLE_PLANNING_REMINDER:
        return
    OptalimWebsite.start(init_async=False)
    tomorrow     = get_tomorrow()
    ago_24h      = timezone.now() - datetime.timedelta(hours=24)

    def planned_user_ids(**kargs):
        """
         Returns the list of user ids with a day validated on a given date
        """
        days = Day.objects.filter(skipped=False, **kargs)
        return set(d.user_id for d in days)

    planned_tomorrow  = planned_user_ids(date=tomorrow, creation_date__lte=ago_24h)
    planned_next_days = planned_user_ids(date__gt=tomorrow)

    # Retrieving the list of users for which planification ends tomorrow
    only_planned_tomorrow = planned_tomorrow.difference(planned_next_days)

    users = User.objects.filter(pk__in=only_planned_tomorrow, access_closed=False)

    for user in users:
        sendmail_template(MessageType.NOTIFICATION, 'planning_mgr/templates/planning_reminder.html',
                        {'date': tomorrow}, "Rappel: Votre planning de repas se termine demain",
                        users=[user], send_async=True, tags=['planning_reminder'])


@shared_task(soft_time_limit=60*60, hard_time_limit=62*60)
def send_meals_suggestion(simulate=False):
    """
    Send to all users some suggestions for next day. Except for :
    - Users who have planned something for the next day  (Day skipped != None)
    - Users for whom today is the last day planned  (they just received a reminder)
    """
    if not ENABLE_MEALS_SUGGESTION:
        return
    OptalimWebsite.start(init_async=False)
    date_today     = today()
    tomorrow       = get_tomorrow()
    all_users = User.objects.filter(mail_suggestion=True, enabled=True, access_closed=False)

    def get_user_ids_planned(date):
        # Returns a list of user ids that have planned their meals on a given date
        days = Day.objects.filter(date=date, skipped__isnull=False)
        return set(day.user_id for day in days)

    # Users that have something planned for tomorrow or today
    shouldnt_send_user_ids = get_user_ids_planned(tomorrow).union(get_user_ids_planned(date_today))

    for user in all_users:
        if user.id in shouldnt_send_user_ids:
            continue
        # Generate 7 days if required, else returns existing day
        with transaction.atomic():
            day = suggest_if_required(user, date_today)

        day = Day.objects.prefetch_related('meal_slots__dishes__dishrecipe_set__recipe__ingredients',
                                           'meal_slots__dishes__dish_type').get(pk=day.id)

        recipes = pick_best_recipes_from_day(day)

        if len(recipes) == 0:
            # No recipe is worth it
            continue

        message_args = {'recipes': PartialRecipeSerializer(recipes, many=True).data,
                        'date': date_today}

        sendmail_template(MessageType.DAILY, 'planning_mgr/templates/meals_suggestion.html',
                          message_args, "%s : %s" % (date_django_filter(day.date, 'l j').capitalize(), recipes[0].name),
                          users=[day.user], send_async=not simulate, tags=['meals_suggestion'], with_bcc=False)

@shared_task
def send_meals_reminder(simulate=False):
    """
    Every day at 5am, send a email containing all the meals planned for today
    """
    if not ENABLE_MEALS_REMINDER:
        return
    OptalimWebsite.start(init_async=False)
    # Retrieving planned days for today
    days = get_planned_days(today())
    user_ids = [d.user_id for d in days]

    # Retrieving planned days of yesterday
    yesterdays = get_planned_days(get_yesterday())
    yesterday_per_user_id = dict((d.user_id, d) for d in yesterdays)

    for day in days:
        if not day.user.is_active:
            continue
        yesterday = yesterday_per_user_id.get(day.user_id, None)

        day_serialization = DayToFillSerializer.serialize(day, with_ingredients=True)
        if len(day_serialization['content']) == 0:
            # No meal (no dish activated)
            continue
        did_you_like = None
        if yesterday:
            did_you_like = pick_recipe_to_evaluate(yesterday)
            if did_you_like is not None:
                did_you_like = PartialRecipeSerializer(did_you_like).data

        message_args = {'meals': day_serialization['content'],
                        'first_name': day.user.first_name,
                        'date': day.date,
                        'did_you_like': did_you_like,
                        'is_family': day.user.profile_set.count() > 1}

        sendmail_template(MessageType.NOTIFICATION, 'planning_mgr/templates/meals_reminder.html',
                          message_args, "Vos repas équilibrés de %s" % date_django_filter(day.date, 'l').capitalize(),
                          users=[day.user], send_async=not simulate, tags=['meals_reminder'])


@shared_task
def delete_old_plannings():
    """
    To save disk space and avoid unnessary storage, remove plannings that are older than 2 weeks ago
    """
    two_weeks_ago = timezone.now() - datetime.timedelta(days=14)
    two_days_ago    = timezone.now() - datetime.timedelta(days=2)

    # Deleting plannings that are :
    # - created more than 2 weeks ago
    # - with last day being older than 2 weeks ago
    old_days = Day.objects.filter(date__lte=two_weeks_ago).exclude(skipped__isnull=False)
    old_planning_ids = set(day.planning_id for day in old_days)

    new_days = Day.objects.filter(date__gt=two_weeks_ago)
    new_planning_ids = set(day.planning_id for day in new_days)

    old_planning_ids = old_planning_ids.difference(new_planning_ids)

    query = Planning.objects.filter(
        creation_date__lte=two_weeks_ago,
        pk__in=old_planning_ids)

    indicators_table = Mongo.hp_table("indicators")
    indicators_v2_table = Mongo.hp_table("indicators_v2")

    print("total plannings : %i" % Planning.objects.count())
    print("will delete %i plannings" % query.count())

    # Bulk deletion (with no iteration) explodes memory usage.
    for planning in query:
        planning.delete()
        # Deleting also from Mongo
        indicators_table.delete_many({'planning_id': planning.id})
        indicators_v2_table.delete_many({'planning_id': planning.id})

    # Deleting old "not_nows"
    NotNow.objects.filter(created_at__lt=two_days_ago).delete()

    # Deleting orphans recipes
    Recipe.objects.filter(internal=True, dishrecipe=None).delete()