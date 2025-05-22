from django.core.management.base    import BaseCommand
from django.core import serializers
from django.db import connection

class Command(BaseCommand):
    help = 'Unserialize a JSON file containing models data'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):

        JSONSerializer = serializers.get_serializer("json")
        json_serializer = JSONSerializer()

        with connection.cursor() as cursor:
            cursor.execute("SET session_replication_role = replica;")
            with open(options['file'], "r") as f:
                for obj in serializers.deserialize("json", f):
                    obj.save()

            cursor.execute("SET session_replication_role = DEFAULT;")

