
import base64
import io

from django.core.files          import File
from PIL                        import Image
from rest_framework.response    import Response
from functools                  import update_wrapper

from optalim.settings           import MEDIA_ROOT

def upload_image(image, obj, image_attr, file_name=None, autoresize=True, width=640, height=400):
    """
    From a Http request, stores the content of the request body into
    obj::image_attr, with the given file_name
    """
    if file_name is None:
        # Recipe id=5  -> recipe_000005.jpg
        file_name = obj.__class__.__name__.lower() + '_' + '%.6i.jpg' % obj.id
    content = image
    file_format, img_data = content.split(';base64,')
    decoded_data = base64.b64decode(img_data)

    image = Image.open(io.BytesIO(decoded_data))

    if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
        # Remove transparency
        image2 = Image.new("RGB", image.size, (255, 255, 255))
        image2.paste(image, mask=image.split()[3]) # 3 is the alpha channel
        image = image2

    if autoresize:
        maxSize = (width, height)
        image.thumbnail(maxSize, Image.ANTIALIAS)

    # Turn back into file-like object
    resizedImageFile = io.BytesIO()
    image.save(resizedImageFile , 'JPEG', optimize = True)
    resizedImageFile.seek(0)    # So that the next read starts at the beginning

    if obj.photo:
        obj.photo.delete(False)
    obj.photo.save(file_name, File(resizedImageFile), save=True)



def no_photo_modifications(photo_field_name):
    """
    DECORATOR for django-rest views update method.
    Check that the photo field is not modified. If so, returns an error indicating that an
    upload method shoud be used
    """
    def decorator(fcn):
        def new_fcn(viewset, request, pk=None):
            data = dict((key, value) for key, value in request.data.items())
            current_obj = viewset.get_object()
            # Django forbid to send an image path without embedding the file
            if photo_field_name in data:
                given_value = data.get(photo_field_name, getattr(current_obj, photo_field_name))
                existing = getattr(current_obj, photo_field_name)
                if not existing:
                    existing = None
                else:
                    existing = (existing.name, existing.url.split('?')[0])
                if given_value is not None:
                    given_value = given_value.split('?')[0]
                    if MEDIA_ROOT and given_value.startswith(MEDIA_ROOT):
                        given_value = given_value[len(MEDIA_ROOT):]

                if (given_value is not None and given_value not in existing):
                    print(given_value)
                    print(existing)
                    return Response({"error": "Use a specific upload method to change image url"}, 403)
                del data[photo_field_name]
            return fcn(viewset, data)
        update_wrapper(new_fcn, fcn)
        return new_fcn
    return decorator