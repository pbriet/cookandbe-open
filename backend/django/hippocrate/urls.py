from django.urls               import re_path
from hippocrate.views.api           import days_indicators, days_indicators_details,\
                                           api_improve_day, api_improve_days, suggest,\
                                           day_indicators, fill_days
from hippocrate.views.admin         import darwin_benchmark, darwin_time_logs, darwin_batch_results, darwin_batch_run, darwin_clean_logs



urlpatterns = [

    re_path(r'^api/user/(?P<user_id>\d+)/indicators/(?P<from_date>\d{4}-\d{2}-\d{2})/(?P<constraint_id>\d+)',   days_indicators_details),
    re_path(r'^api/user/(?P<user_id>\d+)/indicators/(?P<from_date>\d{4}-\d{2}-\d{2})',      days_indicators),

    re_path(r'^api/user/(?P<user_id>\d+)/improve/(?P<from_date>\d{4}-\d{2}-\d{2})',         api_improve_days),

    re_path(r'^api/user/(?P<user_id>\d+)/suggest/(?P<date>\d{4}-\d{2}-\d{2})',              suggest),
    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/improve',          api_improve_day),
    re_path(r'^api/user/(?P<user_id>\d+)/fill_days/(?P<from_date>\d{4}-\d{2}-\d{2})',       fill_days),

    re_path(r'^api/user/(?P<user_id>\d+)/day/(?P<date>\d{4}-\d{2}-\d{2})/indicators$',      day_indicators),
    re_path(r'^secure/api/darwin/benchmark/$',      darwin_benchmark),
    re_path(r'^secure/api/darwin/batch_results/$',  darwin_batch_results),
    re_path(r'^secure/api/darwin/batch_run/$',      darwin_batch_run),
    re_path(r'^secure/api/darwin/clean_logs/$',     darwin_clean_logs),
    re_path(r'^secure/api/darwin/time_logs/$',      darwin_time_logs),
]