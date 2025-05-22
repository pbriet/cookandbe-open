
from user_mgr.models            import User, ConfigStage

from recipe_mgr.models          import Recipe

import datetime

USER_STATS_PREFETCH = (
    "config_stage_completions",
    "days",
    "shopping_lists",
    "main_profile",
    "subscriptions__transactions",
    "profile_set",
    "written_recipes",
)

def get_user_stats(user):
    nb_config_stage = max(ConfigStage.objects.count(), 1)
    res = dict()
    # res["cooked_recipes"] = DishRecipe.objects.filter(validated = True, dish__meal_slot__day__user_id = user.id, dish__meal_slot__day__date__lte = timezone.now(), recipe__internal = False).count()
    res["created_recipes"] = sum(r.internal == False for r in user.written_recipes.all())
    res["published_recipes"] = sum(r.internal == False and r.status >= Recipe.STATUS_PUBLISHED for r in user.written_recipes.all())
    res["nb_profiles"] = user.profile_set.count()
    res["nb_shopping_lists"] = user.shopping_lists.count()
    res["diet_title"] = user.diet and user.diet.title
    res["completion_percentage"] = user.config_stage_completions.count() * 100 / nb_config_stage
    res["nb_planned_days"] = sum(d.skipped is not None for d in user.days.all())
    res["signup_date"] = user.date_joined
    res["name"] = user.get_full_name()
    res["sex"] = user.sex
    res["weight"] = user.main_profile.weight
    res["height"] = user.main_profile.height
    res["imc"] = round(user.main_profile.imc, 1)
    res["age"] = user.main_profile.birth_date and user.main_profile.age
    if res["nb_planned_days"] > 0:
        res["last_planning"] = max(d.modification_date for d in user.days.all() if d.skipped is not None)
        res["last_planned_day"] = max(d.date for d in user.days.all() if d.skipped is not None)
    else:
        res["last_planning"] = None
        res["last_planned_day"] = None
    return res
