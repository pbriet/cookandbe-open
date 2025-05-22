from django.urls               import re_path

from shopping_mgr.views             import new_shopping_list, shopping_list_content, shopping_list_available_days,\
                                           send_list_by_email, shopping_list_toggle_item, shopping_list_history,\
                                           delete_shopping_list, ShoppingItemViewSet, shopping_list_fly_menu

urlpatterns = [

    re_path(r'^api/shopping_item/(?P<item_id>\d+)/force',                             ShoppingItemViewSet.force),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/available_days',               shopping_list_available_days),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/build_new$',                   new_shopping_list),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/history',                      shopping_list_history),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/(?P<shopping_list_id>\d+)/delete$',          delete_shopping_list),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/toggle_item/(?P<shopping_item_id>\d+)',      shopping_list_toggle_item),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/(?P<shopping_list_id>\d+)/send_by_mail$',    send_list_by_email),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/(?P<shopping_list_id>\d+)$',                 shopping_list_content),
    re_path(r'^api/user/(?P<user_id>\d+)/shopping_list/(?P<shopping_list_id>\d+)/fly_menu_items$',  shopping_list_fly_menu),

]