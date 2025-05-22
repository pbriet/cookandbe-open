from django.urls               import re_path
from abtest.views                   import ab_campaign_results, api_ab_value, api_ab_success


urlpatterns = [
    re_path(r'^secure/api/ab/(?P<campaign_key>\S+)/results$', ab_campaign_results),
    re_path(r'^api/ab/(?P<campaign_key>\S+)/value$',            api_ab_value),
    re_path(r'^api/ab/(?P<campaign_key>\S+)/success$',          api_ab_success)
]