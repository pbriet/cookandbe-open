from django.core.management.base        import BaseCommand
import importlib
from django.utils                       import timezone

from user_mgr.models                    import User
import csv

class Command(BaseCommand):
    help = 'Extract emails in a CSV file ./manage.py extract_email_csv slim'

    def add_arguments(self, parser):
        parser.add_argument('diets', nargs='*', type=str)

    def handle(self, **options):

        diets = options['diets']

        if len(diets) == 0:
            # All the users
            users = User.objects.all()
        else:
            users = User.objects.filter(diet__key__in=diets)
        users = users.select_related('main_profile').filter(enabled=True, mail_newsletter=True, access_closed=False, biodymanager_id__isnull=True)

        print("Will extract %i emails" % len(users))

        filename = '%s-email-extract' % timezone.now().strftime("%Y-%m-%d-%H-%M-%S")
        if len(diets):
            filename += "-" + "-".join(diets)
        filename += ".csv"

        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(['Nom', 'Email'])

            for user in users:
                writer.writerow([user.main_profile.nickname, user.email])

        print("-> %s" % filename)