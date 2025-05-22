from django.urls               import re_path

from discussion.views               import api_search_publications, publication_from_key, DiscussionViewSet

urlpatterns = [


    re_path(r'^api/discussion/search$',                         DiscussionViewSet.search),
    re_path(r'^api/discussion/search/(?P<keywords>.+)$',        DiscussionViewSet.search),
    re_path(r'^api/discussion/(?P<discussion_id>\d+)/read$',    DiscussionViewSet.read),
    re_path(r'^api/discussion/(?P<discussion_id>\d+)/status$',  DiscussionViewSet.status),
    re_path(r'^api/discussion/(?P<discussion_id>\d+)/set_publication$', DiscussionViewSet.set_publication),

    re_path(r'^api/publication/search$',                        api_search_publications),
    re_path(r'^api/publication/search/(?P<keywords>.+)$',       api_search_publications),
    re_path(r'^api/publication/from_key/(?P<key>.+)$',          publication_from_key),
]