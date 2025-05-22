from django.urls               import include, re_path
from django.urls                    import path
from rest_framework.routers         import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)
from common.rest                    import ReadOnlyRouter

from abtest.views                   import AbCampaignViewSet
from articles.views                 import ArticleViewSet
from blogs.views                    import BlogViewSet
from diet_mgr.views                 import DietViewSet
from eater_mgr.views                import UserEaterViewSet
from location_mgr.views             import LocationViewSet
from notify_mgr.views               import NotificationsViewSet
from paybox.views                   import SubscriptionViewSet
from planning_mgr.views.viewsets    import MealPlaceViewSet, DishViewSet

from optalim.views                  import celery_is_alive, is_alive

from profile_mgr.views              import UserProfileViewSet, TasteViewSet, RestrictedFoodViewSet, AttendanceView

from recipe_mgr.views.cookbook      import CookbookRecipeViewSet
from recipe_mgr.views.dish_type     import DishTypeViewSet
from recipe_mgr.views.food          import FoodViewSet, FoodTypeViewSet
from recipe_mgr.views.food_tag      import FoodTagViewSet, FoodTagSetViewSet
from recipe_mgr.views.ingredient    import IngredientViewSet, FoodConversionViewSet, CookingMethodViewSet,\
                                           RawStateViewSet
from recipe_mgr.views.nutrient      import NutrientViewSet
from recipe_mgr.views.recipe        import RecipeViewSet, RecipeTagViewSet, RecipeInstructionViewSet
from recipe_mgr.views.ustensils     import UstensilCategoryViewSet, UstensilViewSet

from secure.schema                  import api_schema_view, api_schema_list
from secure.stats                   import api_retrieve_stats, api_promo_code_stats

from seo.views                      import get_sitemap

from shopping_mgr.views             import ShoppingItemViewSet, ShoppingCategoryViewSet

from user_mgr.views                 import ConfigStageViewSet, RoleViewSet

from discussion.views               import DiscussionViewSet, MessageViewSet, PublicationViewSet

import optalim.settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Resources available with all methods to the public
PUBLIC_RESOURCES = [(r'dish', DishViewSet),
                    (r'user/(?P<user_id>\d+)/profile', UserProfileViewSet),
                    (r'user/(?P<user_id>\d+)/eater',   UserEaterViewSet),
                    (r'shopping_item', ShoppingItemViewSet),
                    (r'shopping_category', ShoppingCategoryViewSet),
                    (r'taste', TasteViewSet),
                    (r'restricted_food', RestrictedFoodViewSet),
                    (r'recipe', RecipeViewSet),
                    (r'recipe_instruction', RecipeInstructionViewSet),
                    (r'user/(?P<user_id>\d+)/cookbook_recipe', CookbookRecipeViewSet),
                    (r'meal_place', MealPlaceViewSet),
                    (r'discussion', DiscussionViewSet),
                    (r'publication', PublicationViewSet),
                    (r'message', MessageViewSet),
                    (r'ingredient', IngredientViewSet),
                    (r'user/(?P<user_id>\d+)/notification', NotificationsViewSet),
                    (r'config_stage', ConfigStageViewSet)]

# Resources available in read-only to the public, but in read/write for admins
RO_RESOURCES = [(r'recipe_tag', RecipeTagViewSet),
                (r'location', LocationViewSet),
                (r'ustensil', UstensilViewSet),
                (r'ustensil_category', UstensilCategoryViewSet),
                (r'dish_type', DishTypeViewSet),
                (r'nutrient', NutrientViewSet),
                (r'subscription', SubscriptionViewSet),
                (r'food_conversion', FoodConversionViewSet),
                (r'food_tag', FoodTagViewSet),
                (r'food_tag_set', FoodTagSetViewSet),
                (r'food_type', FoodTypeViewSet),
                (r'cooking_method', CookingMethodViewSet),
                (r'raw_state', RawStateViewSet),
                (r'food', FoodViewSet),
                (r'diet', DietViewSet),
                (r'role', RoleViewSet),
                (r'article', ArticleViewSet),
                (r'blog', BlogViewSet),
                (r'ab_campaign', AbCampaignViewSet)]

# Router which will expose the resources in read-write to the public
# Note: there are still some permissions behind, depending on user
public_router = DefaultRouter(trailing_slash=False)
for pattern, viewset in PUBLIC_RESOURCES:
    base_name = pattern.split('/')[-1] # Base name is required for django views... that we don't use !
    public_router.register(pattern, viewset, basename=base_name)

# Router which will expose the resources in read-only to the public
public_ro_router = ReadOnlyRouter(trailing_slash=False)
# Router which will expose the resources in read-write to the admins
secure_router = DefaultRouter(trailing_slash=False)

for pattern, viewset in RO_RESOURCES:
    base_name = pattern.split('/')[-1] # Base name is required for django views... that we don't use !
    public_ro_router.register(pattern, viewset, basename=base_name)
    secure_router.register(pattern, viewset, basename=base_name)

urlpatterns = [

    re_path(r'^admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),
    path('secure/api/token/', TokenObtainPairView.as_view()),
    path('secure/api/token/refresh', TokenRefreshView.as_view()),

    re_path(r'^secure/api/schema/list/',            api_schema_list),
    re_path(r'^secure/api/schema/view/',            api_schema_view),
    re_path(r'^secure/api/stats/get/',              api_retrieve_stats),

    re_path(r'^secure/api/get_promo_code_stats/$',  api_promo_code_stats),

    re_path(r'^api/profile/(?P<profile_id>[^/.]+)/attendance',          AttendanceView.as_view()),


    re_path(r'^', include('abtest.urls')),
    re_path(r'^', include('articles.urls')),
    re_path(r'^', include('diet_mgr.urls')),
    re_path(r'^', include('discussion.urls')),
    re_path(r'^', include('hippocrate.urls')),
    re_path(r'^', include('newsletters.urls')),
    re_path(r'^', include('nutrient.urls')),
    re_path(r'^', include('paybox.urls')),
    re_path(r'^', include('planning_mgr.urls')),
    re_path(r'^', include('polls.urls')),
    re_path(r'^', include('recipe_mgr.urls')),
    re_path(r'^', include('shopping_mgr.urls')),
    re_path(r'^', include('user_mgr.urls')),

    re_path(r'^api/is-alive/?$', is_alive),
    re_path(r'^api/celery-is-alive/?$', celery_is_alive),

    # Public routers
    re_path(r'^api/', include(public_router.urls + public_ro_router.urls)),

    # Secure routers
    re_path(r'^secure/api/', include(secure_router.urls)),

    path('sitemap.xml',  get_sitemap)
]

if optalim.settings.DEBUG_TOOLBAR_ENABLED:
    import debug_toolbar
    urlpatterns +=[
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
