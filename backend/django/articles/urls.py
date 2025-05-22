from django.urls               import re_path
from articles.views                 import article_from_key, random_articles

urlpatterns = [
    re_path(r'^api/article/from_key/(?P<key>.+)$',  article_from_key),
    re_path(r'^api/article/random',                 random_articles)
]