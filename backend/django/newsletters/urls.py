from django.urls               import re_path
from newsletters.views              import mandrill_templates_list, mandrill_import_template,\
                                           newsletter_list, newsletter_send, newsletter_remove,\
                                           newsletter_details, newsletter_testsend


urlpatterns = [
    re_path(r'^secure/api/newsletter/$',                                    newsletter_list),
    re_path(r'^secure/api/newsletter/(?P<newsletter_id>\d+)$',              newsletter_details),
    re_path(r'^secure/api/newsletter/(?P<newsletter_id>\d+)/send$',         newsletter_send),
    re_path(r'^secure/api/newsletter/(?P<newsletter_id>\d+)/testsend$',     newsletter_testsend),
    re_path(r'^secure/api/newsletter/(?P<newsletter_id>\d+)/remove$',       newsletter_remove),
    re_path(r'^secure/api/newsletter/template_list$',                       mandrill_templates_list),
    re_path(r'^secure/api/newsletter/import_template/(?P<template_name>.+)',mandrill_import_template),
]