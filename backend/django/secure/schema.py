
import tempfile, os
from django.http                import HttpResponse

from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from optalim.settings           import CUSTOM_APPS

from secure.modelviz            import generate_dot

@api_view(['GET'])
def api_schema_list(request):
    return Response(list(CUSTOM_APPS))

@api_view(['GET'])
def api_schema_view(request):
    # Only non system applications are allowed
    apps = set(CUSTOM_APPS)
    # Selecting required apps
    app_names   = request.query_params.get('app_names', None)
    if app_names is not None:
        app_names = app_names.split(',')
        apps = set([appName for appName in apps if appName in app_names])
    # Settings
    dot_ext     = "dot"
    img_ext     = "png"
    # Generating dot file
    dotFile     = tempfile.mktemp(prefix = "tmp_optalim_", suffix = dot_ext, dir = tempfile.gettempdir())
    fd          = open(dotFile, "w")
    fd.write(generate_dot(apps))
    fd.close()
    # Generating image file
    imgFile     = tempfile.mktemp(prefix = "tmp_optalim_", suffix = img_ext, dir = tempfile.gettempdir())
    cmd         = "dot -T{extension} {dotFile} -o {imgFile}".format(dotFile = dotFile, imgFile = imgFile, extension = img_ext)
    os.system(cmd)
    # Creating result
    fd          = open(imgFile, "br")
    res         = HttpResponse(fd.read(), mimetype="image/png")
    fd.close()
    # Cleaning
    os.remove(dotFile)
    os.remove(imgFile)
    # Sending result
    return res
