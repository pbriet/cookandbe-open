
def _obj_match(obj, kargs):
    """
    returns true if all kargs values are the same as object attributes
    """
    for key, value in kargs.items():
        if getattr(obj, key) != value:
            return False
    return True
    


def iter_mealslots(days, **kargs):
    """
    Iterate on all meal_slots of a given planning
    @warning: kargs are not classical django query filters !
    """
    for day in days:
        for meal_slot in day.meal_slots.all():
            if _obj_match(meal_slot, kargs):
                yield meal_slot

def iter_eaters(days):
    for meal_slot in iter_mealslots(days):
        for eater in meal_slot.eaters.all():
            yield eater
            
def iter_dishes(days, ms_kargs=None, **kargs):
    """
    Iterate on all dishes of a given planning
    @warning: kargs are not classical django query filters !
    """
    if ms_kargs is None:
        ms_kargs = {}
    for meal_slot in iter_mealslots(days, **ms_kargs):
        for dish in meal_slot.dishes.all():
            if _obj_match(dish, kargs):
                yield dish

def iter_dishrecipes(days, ms_kargs=None, dish_kargs=None, only_recipe=False, **kargs):
    """
    Iterate on all dish recipes of a given planning
    @warning: kargs are not classical django query filters !
    """
    if ms_kargs is None:   ms_kargs   = {}
    if dish_kargs is None: dish_kargs = {}
    
    for dish in iter_dishes(days, ms_kargs, **dish_kargs):
        for dishrecipe in dish.dishrecipe_set.all():
            if only_recipe:
                if _obj_match(dishrecipe.recipe, kargs):
                    yield dishrecipe.recipe
            else:
                if _obj_match(dishrecipe, kargs):
                    yield dishrecipe

def iter_recipes(days, ms_kargs=None, dish_kargs=None, **kargs):
    """
    Iterate on all recipes of a given planning
    @warning: kargs are not classical django query filters !
    """
    return iter_dishrecipes(days, ms_kargs, dish_kargs, only_recipe=True, **kargs)

