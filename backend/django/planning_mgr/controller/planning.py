
from django.core.exceptions         import ValidationError

from common.date                    import today

from planning_mgr.controller        import DAY_FULL_PREFETCH
from planning_mgr.controller.meta   import build_mealslot_from_meta
from planning_mgr.iterators         import iter_eaters
from planning_mgr.models            import Day, Planning

import datetime

def get_days(user, from_date, nb_days, prefetch=None, allow_empty_days=False, **filters):
    """
    For a given user, return the days from a given date (and a number of days)
    if allow_empty_days, return empty Day objects even if there is nothing in the database on a given date
    """
    filters['user'] = user
    filters['date__gte'] = from_date
    days = Day.objects.filter(**filters)
    if prefetch is not None:
        days = days.prefetch_related(*prefetch).select_related('user__main_profile')
    days = list(days.order_by('date')[:nb_days])
    res_days = []

    for i in range(nb_days):
        expected_date = from_date + datetime.timedelta(days=i)
        if len(days) == 0 or days[0].date != expected_date:
            assert allow_empty_days, "Retrieving discontinued days (%i days from date %s)" % (nb_days, from_date)
            res_days.append(Day(user=user, date=expected_date))
        else:
            res_days.append(days.pop(0))
    return res_days

def get_days_full_prefetch(user, from_date, nb_days, **kargs):
    return get_days(user, from_date, nb_days, DAY_FULL_PREFETCH, **kargs)

def get_planning_including_day(user, date, prefetch=None):
    """
    Return the planning (list of days) in which the given date was initialized
    """
    if prefetch is None:  prefetch = []
    try:
        day = Day.objects.get(user=user, date=date)
    except Day.DoesNotExist:
        return None
    
    return Day.objects.prefetch_related(*prefetch).filter(user=user, planning_id=day.planning_id).order_by('date')

def get_last_planning_days(user):
    """
    Returns the last planning
    """
    planning = Planning.objects.filter(user=user).prefetch_related('days').order_by('-creation_date')[0]
    return sorted(planning.days.all(), key=lambda x: x.date)
    
def get_planning_including_day_full_prefetch(user, date, **kargs):
    return get_planning_including_day(user, date, DAY_FULL_PREFETCH, **kargs)


def clear_days(user, start_date):
    """
    Remove all days from user that starts from a given date
    """
    days_to_delete = Day.objects.filter(user=user, date__gte=start_date)
    planning_ids = set()
    for day in days_to_delete:
        planning_ids.add(day.planning_id)
        day.delete()

    # Removing empty plannings, if so
    Planning.objects.filter(pk__in=planning_ids, days=None).delete()
    
    # Removing shopping lists that include deleted days
    user.shopping_lists.filter(end_date__gte=start_date).delete()

def build_planning(user, start_date, nb_days, clear_existing=True):
    """
    Creates N new days starting from start_date

    It requires the meta planning to be already existing
    
    @param: clear_existing. If True, will delete all the existing days with date >= start_date
    """
    if nb_days > 7 or nb_days < 1:
        raise ValidationError("Building a planning with %i days instead of 7" % nb_days)
    if clear_existing:
        # Remove the existing days with dates that are greater or equal to start_date
        clear_days(user, start_date)
    
    planning = Planning.objects.create(user=user)
    
    day_by_weekday = {}
    for i in range(nb_days):
        day = Day.objects.create(user=user, date=start_date + datetime.timedelta(days=i), planning=planning)
        day_by_weekday[day.weekday] = day

    for meta_day in user.meta_planning.days.prefetch_related('meal_slots__meal_place',
                                                             'meal_slots__meal_slot_eaters__eater',
                                                             'meal_slots__dishes__dish_type',
                                                             'meal_slots__dishes__dishrecipe_set__recipe__ingredients',
                                                             'meal_slots__dishes__dishrecipe_set__recipe__tags',
                                                             'meal_slots__dishes__dishrecipe_set__recipe__ustensils',
                                                             'meal_slots__dishes__dishrecipe_set__recipe__instructions',
                                                             'meal_slots__dishes__dishrecipe_set__recipe__dish_types').all():
        new_day = day_by_weekday.get(meta_day.weekday, None)
        if new_day is None: continue

        for meal_slot in meta_day.meal_slots.all():
            build_mealslot_from_meta(meal_slot, new_day, main_profile_id=user.main_profile_id)

    return sorted(day_by_weekday.values(), key=lambda x: x.date)
           
def get_planning_profiles(days):
    """
    From a list of days, return a list of profile (eaters)
    """
    res = set()
    for eater in iter_eaters(days):
        res.add(eater.profile)
    return res

def days_shopping_listable(user_id):
    """
    Returns the list of days that can be added to a shopping list,
    for a given user
    """
    return Day.objects.filter(user_id=user_id, shopping_list__isnull=True, skipped=False, date__gte=today()).order_by('date')
