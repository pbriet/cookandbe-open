
import threading
import os
from importlib import import_module
import sys
import imp

class OptalimWebsite(object):
    """
    This class contains the main function that initialize
    the Optalim website
    """

    @staticmethod
    def pre_cache():
        """
        Loads in cache (if not already) : FoodTags, DishTypes, ...
        """
        from optalim.precache                   import cache_food_tags
        food_tags_changed = cache_food_tags()

        from nutrient.helpers                   import NutrientCalculatorCache
        NutrientCalculatorCache.init_added_sugars_food_types()

        from hippocrate.models.recipestorage    import MainRecipeStorage
        MainRecipeStorage.initialize(reinit_cache=food_tags_changed)

        from memory.controls                    import MemoryManager
        MemoryManager.initialize()

    @staticmethod
    def load_darwin_config(config_filename=None):
        """
        Load configuration file for Darwin
        """
        from hippocrate_cpp.core import load_darwin_config
        django_root_path = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
        if config_filename is None:
            config_filename = "darwin.yml"
        load_darwin_config(os.path.join(django_root_path, "hippocrate", "config", config_filename))

    @staticmethod
    def init_mongo_indexes():
        from optalim.mongo import Mongo
        Mongo.hp_table("indicators").create_index("planning_id")
        Mongo.hp_table("indicators_v2").create_index("planning_id")
        Mongo.log_table("crash_check").create_index("date")
        Mongo.log_table("darwin_times").create_index("date")
        Mongo.log_table("darwin_quality").create_index("date")
        Mongo.log_table("usage").create_index("date")


    @staticmethod
    def load_hooks():
        """
        Loads the "hooks.py" files located in apps, to initialize hooks
        """
        from django.conf import settings

        for app in settings.CUSTOM_APPS:

            try:
                import_module(app)
                app_path = sys.modules[app].__path__
            except AttributeError:
                continue
            try:
                imp.find_module('hooks', list(app_path))
            except ImportError:
                continue
            module_name = '%s.%s' % (app, 'hooks')
            print("Loading %s" % module_name)
            import_module(module_name)

    @staticmethod
    def start(init_async=True):
        OptalimWebsite.load_hooks()
        OptalimWebsite.load_darwin_config()

        OptalimWebsite.init_mongo_indexes()

        # The following import is required to initialize the diet handlers correctly
        import diet_mgr.import_all

        if init_async:
            thread = threading.Thread(target=OptalimWebsite.pre_cache)
            thread.start()
        else:
            OptalimWebsite.pre_cache()
