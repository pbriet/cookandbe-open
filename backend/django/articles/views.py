from rest_framework             import viewsets
from rest_framework.decorators  import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response    import Response

from common.decorators          import api_arg
from common.image               import upload_image
from common.model               import reload_object
from common.permissions         import Or, ReadWrite, ReadOnly

from articles.serializers       import ArticleSerializer, ArticleLightSerializer
from articles.models            import Article, ArticleImage

from django.conf                import settings

import re
import datetime
import random

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_arg('key', str)
def article_from_key(request, key):
    try:
        article = Article.objects.get(url_key=key)
    except Article.DoesNotExist:
        return Response({"exists": False}, 200)
    res = ArticleSerializer(article).data
    res["exists"] = True
    return Response(res)

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_arg('nb', int, 5)
@api_arg('light', bool, False)
def random_articles(request, nb, light):
    articles = list(Article.objects.filter(published=True))
    articles = random.sample(articles, nb)
    if light:
        serializer = ArticleLightSerializer
    else:
        serializer = ArticleSerializer
    return Response(serializer(articles, many=True).data)



class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    filtered_fields = ("published", )
    permission_classes = (Or(ReadWrite("author", list = True), ReadOnly(list = True)), )

    def get_queryset(self):
        return Article.objects.order_by('-created_at')

    @api_arg('created_at', datetime.datetime, None)
    def update(self, request, created_at, pk=None):
        """
        Override the update : replacing image links "secure.cookandbe.com" to "www.cookandbe.com"
        """
        res = super(viewsets.ModelViewSet, self).update(request, pk)
        article = self.get_object()
        article.content = article.content.replace(settings.APP_BASE_URL, '')
        article.content = article.content.replace(settings.ANGULAR_APP_BASE_URL, '')
        if created_at:
            article.created_at = created_at  # Weird, Django-rest doesn't update it by default :/
        article.save()
        return res

    @api_arg('max_nb', int, 20)
    @api_arg('published', bool, None)
    @api_arg('light', bool, False)
    def list(self, request, max_nb, published, light, **kwargs):
        queryset = self.get_queryset()
        if published is not None:
            queryset = queryset.filter(published=published)
        articles = list(queryset[:max_nb])
        if light:
            serializer = ArticleLightSerializer
        else:
            serializer = ArticleSerializer
        return Response(serializer(articles, many=True).data)

    @action(detail=True, methods=['post'])
    @api_arg('image', str)
    def upload_img(self, request, pk, image):
        """
        Updates the image attached to the article
        """
        article = self.get_object()
        upload_image(image, article, 'photo', autoresize=False)
        return Response({"status": "ok"})

    @action(detail=True, methods=['post'])
    @api_arg('image', str)
    def add_img(self, request, pk, image):
        """
        Add an image that can be included into the article
        """
        article = self.get_object()
        new_image = ArticleImage.objects.create(article=article)
        upload_image(image, new_image, 'photo', autoresize=False)
        reload_object(new_image)
        return Response({"url": new_image.photo.url, "id": new_image.id})


    @action(detail=True, methods=['get'])
    def list_imgs(self, request, pk):
        """
        Returns the list of images that are attached to this article
        """
        article = self.get_object()
        res = []
        for image in article.images.all():
            res.append({"id": image.id,
                        "url": image.photo.url})
        return Response(res)

    @action(detail=True, methods=['post'])
    @api_arg('image_id', int)
    def remove_img(self, request, pk, image_id):
        article = self.get_object()
        try:
            image = ArticleImage.objects.get(article=article, id=image_id)
        except ArticleImage.DoesNotExist:
            return Response({"error": "image does not exist, or is not attached to this article"}, 400)
        image.delete()
        return Response({"status": "done"})
