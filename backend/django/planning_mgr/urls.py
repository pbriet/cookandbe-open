from django.urls               import re_path

from planning_mgr.views.content     import day_content_view, get_menu, day_to_fill,\
                                           meal_type_dish_types, get_next_meal, api_planification_status,\
                                           days_states, days_last_block

from planning_mgr.views.day_actions import not_now, add_dish, delete_dish, validate_dish,\
                                           invalidate_dish_content, day_force_as_filled,\
                                           toggle_dish_activation, toggle_dishrecipe_shopping

from planning_mgr.views.days        import add_days, clear_days_api
from planning_mgr.views.set_recipe  import set_dish_recipe, set_dish_recipes
from planning_mgr.views.mealslot    import MealSlotView, set_mealslot_speed, add_mealslot_eater, remove_mealslot_eater,\
                                           day_structure, set_meal_place, external_meal_suggestions
from planning_mgr.views.metaplanning.attendance     import HomeAttendanceView
from planning_mgr.views.metaplanning.habits         import enable_meal_dish, disable_meal_dish,\
                                                           force_mealtype_dishrecipe, mealtype_habits,\
                                                           set_mealtype_suggest, del_mealtype_static_recipe,\
                                                           add_mealtype_static_recipe, all_mealtypes_habits
from planning_mgr.views.metaplanning.initialize     import api_reset_metaplanning, init_default_metaplanning
from planning_mgr.views.metaplanning.speed          import set_meal_speed



urlpatterns = [
    re_path(r'^secure/api/user/(?P<user_id>\d+)/reset_metaplanning$',       api_reset_metaplanning),

    re_path(r'^api/dish_type/from_meal_type/(?P<meal_type_id>\d+)',     meal_type_dish_types),
    re_path(r'^api/meal_slot/(?P<meal_slot_id>\d+)/set_speed$',         set_mealslot_speed),
    re_path(r'^api/meal_slot/(?P<meal_slot_id>\d+)/add_eater$',         add_mealslot_eater),
    re_path(r'^api/meal_slot/(?P<meal_slot_id>\d+)/remove_eater',       remove_mealslot_eater),
    re_path(r'^api/meal_slot/(?P<meal_slot_id>\d+)/external_suggest$',  external_meal_suggestions),
    re_path(r'^api/meal_slot/(?P<meal_slot_id>\d+)',                    MealSlotView.as_view()),

    re_path(r'^api/user/(?P<user_id>\d+)/planification_status$',        api_planification_status),


    re_path(r'^api/user/(?P<user_id>\d+)/day_to_fill/(?P<date>\d{4}-\d{2}-\d{2})',          day_to_fill),
    re_path('^api/user/(?P<user_id>\d+)/days_states',                                       days_states),

    re_path(r'^api/user/(?P<user_id>\d+)/last_days_block',                                  days_last_block),
    re_path(r'^api/user/(?P<user_id>\d+)/add_days/(?P<from_date>\d{4}-\d{2}-\d{2})',        add_days),
    re_path(r'^api/user/(?P<user_id>\d+)/clear_days/(?P<from_date>\d{4}-\d{2}-\d{2})',      clear_days_api),
    re_path(r'^api/user/(?P<user_id>\d+)/menu/(?P<from_date>\d{4}-\d{2}-\d{2})',            get_menu),
    re_path(r'^api/user/(?P<user_id>\d+)/next_meal',                                        get_next_meal),

    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})$',                 day_content_view),
    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/force_as_filled',  day_force_as_filled),
    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/structure$',       day_structure),
    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/set_meal_place$',  set_meal_place),


    #re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/set_dish/(?P<dish_id>\d+)$', set_dish_recipe),
    # Temporarily not basing url on day
    re_path(r'^api/user/(?P<user_id>\d+)/set_dishrecipe/(?P<dish_id>\d+)$',           set_dish_recipe),
    re_path(r'^api/user/(?P<user_id>\d+)/set_dishrecipes/(?P<dish_id>\d+)$',          set_dish_recipes),
    re_path(r'^api/user/(?P<user_id>\d+)/add_dish/(?P<meal_slot_id>\d+)$',            add_dish),
    re_path(r'^api/user/(?P<user_id>\d+)/delete_dish/(?P<dish_id>\d+)$',              delete_dish),
    re_path(r'^api/user/(?P<user_id>\d+)/validate_dish/(?P<dish_id>\d+)$',            validate_dish),

    re_path(r'^api/user/(?P<user_id>\d+)/toggle_dish_activation/(?P<dish_id>\d+)$',   toggle_dish_activation),
    re_path(r'^api/user/(?P<user_id>\d+)/toggle_dishrecipe_shopping/(?P<dish_id>\d+)$',   toggle_dishrecipe_shopping),

    re_path(r'^api/user/(?P<user_id>\d+)/clear_dish/(?P<dish_id>\d+)$',               invalidate_dish_content),
    re_path(r'^api/user/(?P<user_id>\d+)/not_now/(?P<recipe_id>\d+)$',                not_now),

    re_path(r'^api/planning/(?P<planning_id>\d+)/attendance',           HomeAttendanceView.as_view()),
    re_path(r'^api/user/(?P<user_id>\d+)/default_planning/init$',       init_default_metaplanning),

    re_path(r'^api/user/(?P<user_id>\d+)/meal_types_habits$',                                   all_mealtypes_habits),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/habits$',              mealtype_habits),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/enable_meal_dish',     enable_meal_dish),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/disable_meal_dish',    disable_meal_dish),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/force_recipe',         force_mealtype_dishrecipe),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/set_meal_speed',       set_meal_speed),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/set_suggest',          set_mealtype_suggest),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/add_static_recipe',    add_mealtype_static_recipe),
    re_path(r'^api/user/(?P<user_id>\d+)/meal_type/(?P<meal_type_id>\d+)/del_static_recipe',    del_mealtype_static_recipe),


]