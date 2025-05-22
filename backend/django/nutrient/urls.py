from django.urls               import re_path

from nutrient.views                 import cooking_method_effects, set_cooking_method_effect
from nutrient.views                 import api_get_nutrient_packs, api_enable_nutrient_pack

urlpatterns = [
    re_path(r'^secure/api/food_type/(?P<food_type_id>\d+)/cooking_method_effects$',     cooking_method_effects),
    re_path(r'^secure/api/food_type/(?P<food_type_id>\d+)/set_cooking_method_effect$',  set_cooking_method_effect),


    re_path(r'^api/user/(?P<user_id>\d+)/nutrient_packs',                api_get_nutrient_packs),
    re_path(r'^api/user/(?P<user_id>\d+)/enable_nutrient_pack',          api_enable_nutrient_pack),

]