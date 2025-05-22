from rest_framework         import serializers
from articles.models        import Article


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('photo',)
        model = Article
        exclude = []


class ArticleLightSerializer(ArticleSerializer):
    class Meta:
        model = Article
        fields = ('id', 'created_at', 'title', 'summary', 'photo', 'published', 'url_key', 'meta_desc', 'meta_keywords')