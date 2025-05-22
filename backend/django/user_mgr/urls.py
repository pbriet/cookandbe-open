from django.urls               import re_path

from user_mgr.views                 import api_current_user, api_init, api_signup,\
                                           api_facebook_signup, api_facebook_login, api_login_as,\
                                           api_user_stats, api_config_stages_status,\
                                           api_set_user_login,\
                                           api_set_user_password, api_reset_password, api_forgot_password,\
                                           api_user_search, api_delete_user, secure_user_add_role,\
                                           secure_user_remove_role, api_user_last_subscriptions, api_user_question_quota, api_get_user_infos,\
                                           api_why_leaving_results, api_set_user_postal_code, api_check_promo_code,\
                                           api_login_through_token

from user_mgr.views.user_config     import api_preconfigure, api_complete_config_stage, api_set_user_settings,\
                                           api_user_add_ustensil, api_user_remove_ustensil, api_reset_configuration,\
                                           api_set_user_email_options, api_user_email_options, api_get_budget_proteins,\
                                           api_set_budget_proteins


urlpatterns = [

    re_path(r'^secure/api/user/(?P<user_id>\d+)$',                          api_get_user_infos),
    re_path(r'^secure/api/user/search/(?P<keyword>.+)',                     api_user_search),
    re_path(r'^secure/api/user/(?P<user_id>\d+)/reset_configuration$',      api_reset_configuration),
    re_path(r'^secure/api/user/(?P<user_id>\d+)/delete$',                   api_delete_user),
    re_path(r'^secure/api/user/(?P<user_id>\d+)/add_role',                  secure_user_add_role),
    re_path(r'^secure/api/user/(?P<user_id>\d+)/remove_role',               secure_user_remove_role),
    re_path(r'^secure/api/user/(?P<user_id>\d+)/last_subscriptions$',       api_user_last_subscriptions),
    re_path(r'^secure/api/polls/why_leaving',                               api_why_leaving_results),

    re_path(r'^api/init/$',                         api_init),
    re_path(r'^api/autologin/$',                    api_login_through_token),
    re_path(r'^secure/api/login_as/$',              api_login_as),
    re_path(r'^api/signup/$',                       api_signup),
    re_path(r'^api/facebook-signup/$',              api_facebook_signup),
    re_path(r'^api/facebook-login/$',               api_facebook_login),
    re_path(r'^api/check_promo_code/(?P<value>\S+)$',  api_check_promo_code),

    re_path(r'^api/forgot_password/$',              api_forgot_password),
    re_path(r'^api/reset_password/$',               api_reset_password),
    re_path(r'^api/current_user/$',                             api_current_user),
    re_path(r'^api/user/(?P<user_id>\d+)/stats',                api_user_stats),
    re_path(r'^api/user/(?P<user_id>\d+)/change_settings',      api_set_user_settings),
    re_path(r'^api/user/(?P<user_id>\d+)/change_login',         api_set_user_login),
    re_path(r'^api/user/(?P<user_id>\d+)/change_password',      api_set_user_password),
    re_path(r'^api/user/(?P<user_id>\d+)/add_ustensil',         api_user_add_ustensil),
    re_path(r'^api/user/(?P<user_id>\d+)/remove_ustensil',      api_user_remove_ustensil),
    re_path(r'^api/user/(?P<user_id>\d+)/question_quota',       api_user_question_quota),

    re_path(r'^api/user/(?P<user_id>\d+)/config_stages$',               api_config_stages_status),
    re_path(r'^api/user/(?P<user_id>\d+)/config_stages/complete$',      api_complete_config_stage),
    re_path(r'^api/user/(?P<user_id>\d+)/email_options$',               api_user_email_options),
    re_path(r'^api/user/(?P<user_id>\d+)/set_email_options$',           api_set_user_email_options),
    re_path(r'^api/user/(?P<user_id>\d+)/set_postal_code$',             api_set_user_postal_code),


    re_path(r'^api/user/(?P<user_id>\d+)/budget_proteins',              api_get_budget_proteins),
    re_path(r'^api/user/(?P<user_id>\d+)/set_budget_proteins',          api_set_budget_proteins),
    re_path(r'^api/user/(?P<user_id>\d+)/preconfigure$',                api_preconfigure),

]