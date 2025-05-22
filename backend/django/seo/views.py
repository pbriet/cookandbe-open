from django.http        import HttpResponse

from seo.controller     import generate_sitemap

def get_sitemap(request):
    content = generate_sitemap()
    return HttpResponse(content, content_type="text/xml")