from django.urls               import re_path

from polls.views                    import api_question, api_question_vote, api_question_results,\
                                           api_question_list

urlpatterns = [

    re_path(r'^api/question$',                                      api_question_list),
    re_path(r'^api/question/(?P<question_id>\d+)$',                 api_question),
    re_path(r'^api/question/(?P<question_id>\d+)/vote$',            api_question_vote),
    re_path(r'^secure/api/question/(?P<question_id>\d+)/results$',  api_question_results),

]