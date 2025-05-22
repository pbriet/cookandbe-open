from django.urls               import re_path
from diet_mgr.views                 import (subscribe_to_diet, current_diet_parameters,
                                           diet_excluded_foodtags, diet_forewarned_foodtags,
                                           diet_diagnose, diet_from_key,
                                           diet_from_url_key)


urlpatterns = [

    re_path(r'^api/user/(?P<user_id>\d+)/subscribe_to_diet/(?P<diet_id>\d+)$',              subscribe_to_diet),
    re_path(r'^api/user/(?P<user_id>\d+)/diagnose/(?P<diet_id>\d+)',                        diet_diagnose),
    re_path(r'^api/user/(?P<user_id>\d+)/current_diet_parameters$',                         current_diet_parameters),

    re_path(r'^api/diet/from_key/(?P<diet_key>\S+)$',                                       diet_from_key),
    re_path(r'^api/diet/from_url_key/(?P<url_key>\S+)$',                                    diet_from_url_key),
    re_path(r'^api/diet/(?P<diet_id>\d+)/excluded_foodtags$',                               diet_excluded_foodtags),
    re_path(r'^api/diet/(?P<diet_id>\d+)/forewarned_foodtags$',                             diet_forewarned_foodtags),
]