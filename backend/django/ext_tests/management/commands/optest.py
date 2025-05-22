
from django.core.management         import call_command
from django.core.management.base    import BaseCommand

from optparse                       import make_option

import os, sys, re

"""
ATTENTION:
=========

Pas d'imports optalim ici (excepté settings.py si besoin) afin d'éviter l'initialisation précoce de la BDD (lazy).

"""

class Command(BaseCommand):

    # args = '[--pgsql] [--windows] [--isolate] <test1 test2 ...>'
    # args = '[--long-opt | -short-opt] [--optional-list=<value1>,<value2> ...]  <mandatory1 mandatory2...>'
    help = 'Runs all tests and adds usefull options'

    # option_list = BaseCommand.option_list + (
    #     make_option(
    #         '--pgsql',
    #         action='store_true',
    #         dest='pgsql',
    #         default=False,
    #         help='Force usage of PostgreSql database (production test)'
    #     ),
    #     make_option(
    #         '--windows',
    #         action='store_true',
    #         dest='windows',
    #         default=False,
    #         help='Searches for tests modules (usefull in Windows environments with bad VM rights)'
    #     ),
    #     make_option(
    #         '--isolate',
    #         action='store_true',
    #         dest='isolate',
    #         default=False,
    #         help='Execute each test separately (takes some time)'
    #     ),
    # )

    ### For Django > 1.8
    def add_arguments(self, parser):
        parser.add_argument('--windows',
            action='store_true',
            dest='pgsql',
            default=False,
            help='Force usage of PostgreSql database (production test)')
        parser.add_argument('--pgsql',
            action='store_true',
            dest='windows',
            default=False,
            help='Searches for tests modules (usefull in Windows environments with bad VM rights)'
        ),
        parser.add_argument('--keepdb',
            action='store_true',
            dest='keepdb',
            default=False,
        ),
        parser.add_argument('--isolate',
            action='store_true',
            dest='isolate',
            default=False,
            help='Execute each test separately (takes some time)'
        ),
        parser.add_argument('any_args', nargs='*', type=str)

    def _get_all_tests(self):
        from optalim.settings import DJANGO_PATH
        os.chdir(DJANGO_PATH)
        test_module_list = []
        for app_dir in os.listdir(DJANGO_PATH):
            tests_dir = os.path.join(DJANGO_PATH, app_dir, "tests")
            if os.access(tests_dir, os.R_OK):
                for test_file in os.listdir(tests_dir):
                    if re.match("test_.*\.py", test_file) is not None:
                        test_module = "%s.tests.%s" % (app_dir, os.path.splitext(test_file)[0])
                        test_module_list.append(test_module)
        return test_module_list

    def handle(self, *args, **options):
        # Importing settings to initialize database connection depending on argv
        import optalim.settings

        options_to_pass = dict(options.items())
        for key in ("isolate", "keepdb", "pgsql", "windows", "any_args"):
            if key in options_to_pass:
                options_to_pass.pop(key)

        if options.get('windows', False) and len(args) == 0:
            print("*** Windows mode ON ***")
            args = self._get_all_tests()
        # Ugly: cleaning options because Nose is checking them directly on command line...
        sys.argv = list(arg for arg in sys.argv if arg not in ("--pgsql", "--windows", "--isolate"))
        # Execution
        any_args = options['any_args']
        if options.get('isolate', False):
            print("*** Isolate mode ON ***")
            for test_module in args:
                # command = "python manage.py test %s" % test_module
                # os.system(command)
                call_command('test', test_module, **options_to_pass)
        else:
            call_command('test', *any_args, **options_to_pass)
