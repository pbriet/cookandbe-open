from django.urls               import re_path

from recipe_mgr.views.cookbook      import count_cookbook_recipes, delete_cookbook_recipe_by_recipe
from recipe_mgr.views.dish_type     import find_dish_type_aggregations
from recipe_mgr.views.food          import food_search
from recipe_mgr.views.food_tag      import food_tag_search, untagged_food, food_tag_from_key
from recipe_mgr.views.ingredient    import CookingMethodViewSet
from recipe_mgr.views.nutrient      import nutrient_categories
from recipe_mgr.views.ratings       import rate_recipe, ratings_list, moderate_rating, user_recipe_rating
from recipe_mgr.views.recipe        import count_recipe, secure_count_recipe,\
                                           recipe_search, recipe_reject_publication,\
                                           recipe_from_key, recipes_from_food_tag, recipe_publish, random_season_recipe_selection,\
                                           list_personal_recipes, recipes_get_many, private_to_review,\
                                           mark_private_recipe_as_reviewed, duplicate_private_recipe

urlpatterns = [

    re_path(r'^secure/api/food/untagged/$',         untagged_food),
    re_path(r'^secure/api/recipe/count$',                                   secure_count_recipe),
    re_path(r'^secure/api/recipe/private_to_review$',                       private_to_review),
    re_path(r'^secure/api/recipe/(?P<recipe_id>\d+)/reject_publication$',   recipe_reject_publication),
    re_path(r'^secure/api/recipe/(?P<recipe_id>\d+)/mark_private_recipe_as_reviewed$',  mark_private_recipe_as_reviewed),
    re_path(r'^secure/api/recipe/(?P<recipe_id>\d+)/duplicate_private_recipe$',         duplicate_private_recipe),
    re_path(r'^secure/api/recipe/(?P<recipe_id>\d+)/publish$',              recipe_publish),
    re_path(r'^secure/api/rating/(?P<rating_id>\d+)/moderate$',             moderate_rating),


    re_path(r'^api/nutrient_categories', nutrient_categories),

    re_path(r'^api/dish_type/find_aggregations$',               find_dish_type_aggregations),
    re_path(r'^api/user/(?P<user_id>\d+)/cookbook_recipe/count$', count_cookbook_recipes),
    re_path(r'^api/user/(?P<user_id>\d+)/cookbook_recipe/delete_by_recipe_id', delete_cookbook_recipe_by_recipe),

    re_path(r'^api/food/search$',                               food_search),
    re_path(r'^api/food/search/(?P<keyword>.+)$',               food_search),
    re_path(r'^api/food_tag/from_key/(?P<key>.+)$',             food_tag_from_key),
    re_path(r'^api/food_tag/search/(?P<keyword>.+)$',           food_tag_search),
    re_path(r'^api/cooking_method/food/(?P<food_id>\d+)$',      CookingMethodViewSet.food),
    re_path(r'^api/recipe/random_season_selection$',            random_season_recipe_selection),
    re_path(r'^api/recipe/count$',                              count_recipe),
    re_path(r'^api/recipe/search/(?P<keyword>.*)$',             recipe_search),
    re_path(r'^api/recipe/from_key/(?P<key>.+)$',               recipe_from_key),
    re_path(r'^api/recipe/from_food_tag/(?P<food_tag_id>\d+)$', recipes_from_food_tag),
    re_path(r'^api/recipe/get_many$',                           recipes_get_many),
    re_path(r'^api/recipe/(?P<recipe_id>\d+)/rate$',            rate_recipe),
    re_path(r'^api/recipe/(?P<recipe_id>\d+)/ratings$',         ratings_list),
    re_path(r'^api/recipe/(?P<recipe_id>\d+)/user_rating$',     user_recipe_rating),
    re_path(r'^api/user/(?P<user_id>\d+)/personal_recipes$',    list_personal_recipes),
    re_path(r'^api/last_ratings$',                              ratings_list),


]