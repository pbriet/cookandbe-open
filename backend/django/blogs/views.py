
from rest_framework             import viewsets
from rest_framework.decorators  import action

from blogs.models               import Blog

from common.decorators          import api_arg
from common.permissions         import Or, ReadOnly, ReadWrite

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = (Or(ReadWrite("admin", list = True), ReadWrite(user = ("user", )),
                             ReadOnly(list = True)), )

    @action(detail=True, methods=['post'])
    @api_arg('image', str)
    def upload_img(self, request, pk, image):
        """
        Updates the image attached to the blog
        """
        blog = Blog.objects.get(pk=pk)
        upload_image(image, blog, 'photo')
        blog.save()
        return Response({"status": "ok"})
