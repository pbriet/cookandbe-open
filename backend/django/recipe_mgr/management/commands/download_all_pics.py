from django.core.management.base import BaseCommand
from articles.models             import Article, ArticleImage
from blogs.models                import Blog
from recipe_mgr.models           import Recipe, FoodTag
from boto.s3.connection          import S3Connection
from boto.s3.key                 import Key
import os
import time

class Command(BaseCommand):
    args = 'tmp_target_path bucket_name'
    help = 'Download all recipe and article images stored in the DB'

    def handle(self, *args, **options):
        from optalim.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
        conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, host="s3-eu-west-1.amazonaws.com")

        bucket = conn.get_bucket(args[1])

        target_path = args[0]

        OBJS_WITH_IMG = (Article, ArticleImage, Blog, Recipe, FoodTag)

        for cls in OBJS_WITH_IMG:

            objs = cls.objects.filter(photo__isnull=False)
            for i, obj in enumerate(objs):
                print("%i / %i" % (i + 1, len(objs)))
                if not obj.photo.name:
                    continue
                if bucket.get_key(obj.photo.name) is not None:
                    # Already uploaded on S3
                    continue

                print(obj.photo.name)

                photo_name = obj.photo.name
                photo_target_path = target_path

                splitted = photo_name.split('/')

                for dirname in splitted[:-1]:
                    photo_target_path += "/" + dirname
                    if not os.path.exists(photo_target_path):
                        os.mkdir(photo_target_path)

                final_photo_path = photo_target_path + "/" + splitted[-1]

                if not os.path.exists(final_photo_path):
                    # Not downloaded already downloaded

                    os.chdir(photo_target_path)
                    os.system("wget --quiet -t 2 https://localhost:8443/documents/%s" % photo_name)

                    if not os.path.exists(final_photo_path):
                        print("FAIL")
                        continue

                # Upload to S3
                k = Key(bucket)
                k.key = photo_name
                k.set_contents_from_filename(final_photo_path)
