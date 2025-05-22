from django.core.management.base import BaseCommand, CommandError
from django.db                   import transaction

from collections                 import defaultdict, OrderedDict
from optparse                    import make_option
from subprocess                  import call

from nutrient.models             import Nutrient, FoodNutrient

from recipe_mgr.models           import Food, FoodSource, RawState, CookingMethod

import os
import re
import yaml

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

"""
This scripts updates the nutrient values from the CIQUAL or CNF database
(Given link to a zipfile)

It does the following :
- Downloading, parsing, and storing in RAM the PROVIDER values
- Retrieving in RAM PostgreSQL data

Foreach PROVIDER food+nutrient+value entry :
- Retrieve the correct cooking method + raw state from the ciqual food name
- Retrieve the nutrient values in the DB, and compare
- If changed, apply the modifications
"""

class NutrientUpdater(BaseCommand):
    """
    Base class for CNF and CIQUAL updaters
    """
    TMP_PATH = None # Directory in /tmp where the data will be downloaded/extracted
    SOURCE_NAME = None   # 'CIQUAL' or 'CNF'
    ID_BDD_FIELD = None  # 'ciqual_id', or 'cnf_id'
    EXPECTED_NB_NUTRIENTS = 0
    
    # Warning, the following must be used carefully :
    # If True, it will verify that the raw state and cooking methods detected from the name
    # exists in the database
    # Otherwise, it will not
    CHECK_RAW_STATE_COOKING_METHOD = True
    
    option_list = BaseCommand.option_list + (
            make_option('--continue', '-c',
                action='store_true', dest='continue',
                default=False,
                help='Do not download again the ciqual data (in case of retrying)'),
            
            make_option('--allow-change-all', '-a',
                action='store_true', dest='allow_change_all',
                default=False,
                help='Allow that all nutrients for a given food may change (assertion false otherwise)'),
            
            make_option('--only-enabled', '-o',
                action='store_true', dest='only_enabled',
                default=False,
                help='Update only enabled foods, not the disabled ones'),
            )


    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        assert self.TMP_PATH is not None,     "Please define a TMP_PATH"
        assert self.ID_BDD_FIELD is not None, "Please define a ID_BDD_FIELD"
        assert self.SOURCE_NAME is not None, "Please define a SOURCE_NAME"
        self.stats = {
            'updated': defaultdict(int),
            'new': defaultdict(int),
            'deleted': defaultdict(int)
            }
        
        # Is the number of value modifications not too big ? (security)
        self.nb_existing_nutrient_values = defaultdict(int)
        self.nb_changed_nutrient_values = defaultdict(int)
        self.updated_bdd_food_ids = set()
        
        
    """
    ==============================   MAIN METHOD  =======================
    """
    @transaction.atomic
    def handle(self, *args, **options):
        is_continuing = options.get('continue', False)
        self.allow_change_all = options.get('allow_change_all', False)
        self.only_enabled = options.get('only_enabled', False)
        
        if not is_continuing and len(args) != 1:
            raise CommandError('Invalid number of arguments (expected: 1)')
        
        # Initializing directories
        if not is_continuing:
            call(["rm", "-rf", self.TMP_PATH])
            call(["mkdir", self.TMP_PATH])
        os.chdir(self.TMP_PATH)
        
        if not is_continuing:
            # Retrieve data from the website (given link)
            self.download_extract_data(args[0])
    
        # Load CNF/CIQUAL and Postgres data in RAM
        self.preload_data()
        
        # Updating nutrient values
        print("")
        print("Updating...")
        self.update_nutrient_values()
    
    def download_extract_data(self, http_link):
        """
        Retrieve data from the provider website (given link)
        """
        raise NotImplementedError
    
    """
    ================= LOADING DATA IN RAM  =======================
    """
    def preload_data(self):
        """
        Load CNF/CIQUAL and Postgres data in RAM
        """
        print("Preloading CNF/CIQUAL")
        print("- Foods...")
        self.preload_provider_food_names()
        
        print("- Nutrients...")
        self.preload_provider_nutrients()
        
        print("- FoodNutrients...")
        self.preload_provider_foodnutrients()
        
        print("- Nutrients...")
        self.preload_cookingmethods()
        
        print("")
        print("Preloading Postgres BDD")
    
        print("- Foods...")
        self.preload_bdd_foods()
        
        print("- Nutrients...")
        self.preload_bdd_nutrients()
        
        print("- FoodNutrients...")
        self.preload_bdd_foodnutrients()
        
        print("- RawStates and CookingMethods...")
        self.preload_bdd_raw_cooking()
        
    
    def preload_bdd_nutrients(self):
        """
        Preload the nutrients from PostgreSQL
        """
        self.provider_to_nutrient_id = {}
        kwargs = {'%s__isnull' % self.ID_BDD_FIELD : False}
        for nutrient in Nutrient.objects.filter(**kwargs):
            self.provider_to_nutrient_id[getattr(nutrient, self.ID_BDD_FIELD)] = nutrient.id
    
    def preload_bdd_foodnutrients(self):
        """
          {food_id: {(raw_state_id, cooking_method_id): {provider_nutrient_id: FoodNutrient}}}
        """
        self.bdd_foodnutrients = defaultdict(lambda: defaultdict(dict))
        kwargs = {'nutrient__%s__isnull' % self.ID_BDD_FIELD : False}
        for food_nutrient in FoodNutrient.objects.filter(**kwargs).prefetch_related('nutrient'):
            key = (food_nutrient.raw_state_id, food_nutrient.cooking_method_id)
            self.bdd_foodnutrients[food_nutrient.food_id][key][getattr(food_nutrient.nutrient, self.ID_BDD_FIELD)] = food_nutrient
    
    def preload_bdd_foods(self):
        """
        Précharger les Food de la BDD, splitter les original_ids (':'), faire un dico {original_id -> Foods}
        """
        self.bdd_foods = defaultdict(list)
        query = Food.objects.filter(food_source__name=self.SOURCE_NAME)
        if self.only_enabled:
            query = query.filter(enabled=True)
        food_objs = list(query)
        assert len(food_objs) > 0, "no Foods with source : %s" % self.SOURCE_NAME
        for food in food_objs:
            ids = food.original.split(':')
            for id_ in ids:
                self.bdd_foods[int(id_)].append(food)
    
    
    def preload_bdd_raw_cooking(self):
        """
        Preload the cooking_methods and raw_states from database
        """
        self.raw_state_from_id = {}
        self.raw_state_name_to_id = {}
        for raw_state in RawState.objects.all():
            self.raw_state_name_to_id[raw_state.name] = raw_state.id
            self.raw_state_from_id[raw_state.id] = raw_state.name
            
        self.cooking_method_name_to_id = {}
        self.cooking_method_from_id = {}
        for cooking_method in CookingMethod.objects.all():
            self.cooking_method_name_to_id[cooking_method.name] = cooking_method.id
            self.cooking_method_from_id[cooking_method.id] = cooking_method.name
    
    def preload_cookingmethods(self):
        """
        Preload a YAML file containing match :
        Provider string for cooking method -> Internal BDD string for cooking method
        """
        with open(os.path.join(SCRIPT_PATH, "dico_cooking_methods.yml")) as f:
            data  = yaml.load(f)
        
        self.dico_cooking_methods = OrderedDict()
        for key, value in sorted(data.items(), key=lambda x: len(x[0]), reverse=True):
            self.dico_cooking_methods[key] = value
    
    
    def preload_provider_nutrients(self):
        """
        FILLS self.provider_nutrients
        {provider_nutrient_id : provider_name}
        """
        raise NotImplementedError
    
    
    def preload_provider_foodnutrients(self):
        """
        FILLS self.provider_foodnutrients
        {original_id: {nutrient_id: value}}
        """
        raise NotImplementedError
        
    def preload_provider_food_names(self):
        """
        FILLS self.provider_food_id_to_name
        {original_id: original_name}
        """
        raise NotImplementedError
    
    
    """
    ================= RAW STATE / COOKING METHOD DETECTION  =======================
    """
    
    def detect_raw_state(self, name):
        """
        Detect raw state from provider food name
        """
        name = name
        match_canned = re.compile(r'(.+)(appertisée?s?(?:, égouttée?s?)?)(.*)').match(name)
        match_frozen = re.compile(r'(.+)(surgelée?s?|congelée?s?)(.*)').match(name)
        match_fresh = re.compile(r'(.+)[\s,](frais|fraîches?)(.*)').match(name)
        
        if match_canned:
            return "en conserve"
        elif match_frozen:
            return "surgelé"
        return "frais"
    
    def detect_food_cooking_methods(self, food_name):
        """
        Detect cooking method from provider food name
        """
        name_copy = food_name
        food_cooking_methods = set()
        # Match with longer keyword first
        for keyword, cooking_method in self.dico_cooking_methods.items():
            if keyword in name_copy:
                # check that cooking method keyword is not a substring of the food! (like "biscuit")
                i = name_copy.rindex(keyword)

                if name_copy[i-1] not in (' ', ',') or\
                    (len(name_copy) > i + len(keyword) and\
                    name_copy[i + len(keyword)] not in (' ', ',')):
                    continue
                
                food_cooking_methods.add(cooking_method)
                name_copy = name_copy.replace(keyword, '')
                
        if "tartine craquante" in food_name and "grillé" in food_cooking_methods:
            food_cooking_methods.remove("grillé")
        if "à pate" in food_name and "cuite" in food_name:
            food_cooking_methods.remove("cuit")
        if 'au four à micro-ondes' in food_name and "au four" in food_cooking_methods:
            food_cooking_methods.remove("au four")
        elif "au four" in food_name and "cuit" in food_cooking_methods:
            food_cooking_methods.remove("cuit")
        if len(food_cooking_methods) > 1 and 'cru' in food_cooking_methods:
            food_cooking_methods.remove("cru")
        if "à l'eau" in food_cooking_methods and "cuit" in food_cooking_methods:
            food_cooking_methods.remove("cuit")
        if "à la vapeur" in food_cooking_methods and "cuit" in food_cooking_methods:
            food_cooking_methods.remove("cuit")
        if "bien cuit" in food_name and "cuit" in food_cooking_methods:
            food_cooking_methods.remove("cuit")
        for roti_kind in ["rôti de", "rôti d'"]:
            # La CNF et ses rotis...
            if roti_kind in food_name:
                return ["rôti"]
        return list(food_cooking_methods)
    
    def match_provider_food_to_raw_state_cooking_method(self, provider_food_name, raw_state_cooking_ids, bdd_food_id):
        """
        From a food name (ciqual-db like) and a list of available (raw_state_id, cooking_method_id).
        Returns the correct pair matching the name by detecting keywords in it.
        """
        raw_state       = self.detect_raw_state(provider_food_name)
        raw_state_id    = self.raw_state_name_to_id[raw_state]
        cooking_methods = self.detect_food_cooking_methods(provider_food_name)
        
        crude_id = self.cooking_method_name_to_id["cru"]
        
        if len(cooking_methods) == 0:
            if (raw_state_id, crude_id) not in raw_state_cooking_ids:
                if self.CHECK_RAW_STATE_COOKING_METHOD:
                    self.error_raw_state_cooking(bdd_food_id, provider_food_name, raw_state, ["cru"], raw_state_cooking_ids)
            return (raw_state_id, crude_id)
        for cooking_method in sorted(cooking_methods,
                                     key=lambda x: len(x),
                                     reverse=True):
            cooking_method_id = self.cooking_method_name_to_id[cooking_method]
            if (raw_state_id, cooking_method_id) in raw_state_cooking_ids:
                return (raw_state_id, cooking_method_id)
        
        if not self.CHECK_RAW_STATE_COOKING_METHOD:
            cooking_method = self.select_best_cooking_method(provider_food_name, cooking_methods)
            return (raw_state_id, self.cooking_method_name_to_id[cooking_method])
        self.error_raw_state_cooking(bdd_food_id, provider_food_name, raw_state, cooking_methods, raw_state_cooking_ids)

    def select_best_cooking_method(self, provider_food_name, cooking_methods):
        """
        From multiple cooking methods (and not one matching an entry in the DB), returning the correct one
        """
        if len(cooking_methods) == 1:
            return cooking_methods[0]
        assert False, "what cooking_method to choose ?\nFor : %s\nChoices are : %s" % (provider_food_name, cooking_methods)

    def error_raw_state_cooking(self, bdd_food_id, food_name, raw_state, cooking_methods, raw_state_cooking_ids):
        """
        Raise an error when raw_state, cooking_method detected from food name doesn't match
        the content of database
        """
        print("")
        print("Error, cannot find raw_state/cooking_method in DB from food_name")
        print("FOOD (provider name) : ", food_name)
        print("FOOD ID (BDD) : ", bdd_food_id)
        print("Expected raw_state : ", raw_state)
        print("Expected cooking_methods : ", cooking_methods)
        print("")
        print("In DB : ")
        for raw_state_id, cooking_method_id in raw_state_cooking_ids:
            print("- (%s, %s)" % (self.raw_state_from_id[raw_state_id], self.cooking_method_from_id[cooking_method_id]))
        exit(1)
        
        
    """
    ================= COMPARISON / UPDATE OF NUTRIENT VALUES  =======================
    """
    
    def update_nutrient_values(self):
        """
        Updating the nutrient values currently in the DB from the provider file
        """
        nb_foods = len(self.provider_food_id_to_name)
        i_food = 0
        assert(len(self.provider_food_id_to_name) > 0, "no provider_food_id_to_name")
        for provider_food_id, provider_food_name in self.provider_food_id_to_name.items():
            i_food += 1
            if (i_food + 1) % 100 == 0:
                print("%s / %s" % (i_food + 1, nb_foods))
            self.update_provider_food_values(provider_food_id, provider_food_name)
        
        print("")
        for key, values in self.stats.items():
            print(" ==== %s (%s) ==== " % (key, sum(values.values())))
            for nutrient_name, nb in values.items():
                print("- %s : %s" % (nutrient_name[:20], nb))
        print("")
        print("   ==== NUTRIENTS VALUES UPDATE ==== ")
        # Securities
        for provider_nutrient_id, provider_nutrient_name in self.provider_nutrients.items():
            if provider_nutrient_id not in self.EXCLUDED_PROVIDER_NUTRIENT_IDS:
                nb_previous_nutrients = self.nb_existing_nutrient_values[provider_nutrient_id]
                nb_modified_values = self.nb_changed_nutrient_values[provider_nutrient_id]
                if nb_modified_values > 0:
                    if nb_previous_nutrients == 0:
                        print("** 100%% new nutrient values for nutrient %s" % provider_nutrient_name)
                    else:
                        percent_change = 100*float(self.nb_changed_nutrient_values[provider_nutrient_id]) / nb_previous_nutrients
                        print("%s :   %s%%" % (provider_nutrient_name[:10], round(percent_change, 2)))
                        assert percent_change < 20, "Alert : Too many values (> 20%%) have changed for nutrient %s" % provider_nutrient_name

        
        ### Applying updates
        print("")
        if sum(self.stats['updated'].values()) + sum(self.stats['new'].values()) + sum(self.stats['deleted'].values()) == 0:
            print("=== Already up to date ===")
        elif input("Apply ? (y/n) ") == "y":
            print("APPLY")
        else:
            assert False, "ABORT"
        
    def update_provider_food_values(self, provider_food_id, provider_food_name):
        """
        For a given provider food id and food name, updates the corresponding values in the BDD
        """
        # There can be more than one Food in the BDD for on Ciqual element, thanks to "clones"
        bdd_foods = self.bdd_foods[provider_food_id]
        
        provider_foodnutrients = self.provider_foodnutrients[provider_food_id]
        assert len(provider_foodnutrients) <= self.EXPECTED_NB_NUTRIENTS, "More than %i nutrients ? (got %i)" % (self.EXPECTED_NB_NUTRIENTS, len(provider_foodnutrients))
        
        for bdd_food in bdd_foods:
            bdd_foodnutrients = self.bdd_foodnutrients[bdd_food.id]
            # Find from the PGSQL existing tuples (food, cookingmethod, rawstate)
            # Which one matches the provider food name
            raw_state_cooking_ids = bdd_foodnutrients.keys()
            cooking_raw_key = self.match_provider_food_to_raw_state_cooking_method(provider_food_name, raw_state_cooking_ids, bdd_food.id)

            bdd_foodnutrients = bdd_foodnutrients[cooking_raw_key]
            
            key = (bdd_food.id, ) + cooking_raw_key
            assert key not in self.updated_bdd_food_ids, "Food BDD updated twice : %s %s" % (bdd_food.name, cooking_raw_key)
            self.updated_bdd_food_ids.add(key)
    
            self.update_food_nutrient_comparison(bdd_food, cooking_raw_key, 
                                                 bdd_foodnutrients, provider_foodnutrients)
    
    def update_food_nutrient_comparison(self, bdd_food, cooking_raw_key,
                                              bdd_foodnutrients, provider_foodnutrients):
        """
        Updating nutrient values for a given BDD food + raw_state + cooking_method.
        With current foodnutrients, and provider foodnutrients
        
        Comparing and updating values.
        """
        
        all_changed = True
        
        # Now is the difference !
        for provider_nutrient_id, provider_value in provider_foodnutrients.items():
            
            foodnutrient = bdd_foodnutrients.get(provider_nutrient_id, None)
            if foodnutrient:
                current_value = foodnutrient.amount_per_gram
            else:
                current_value = None
            if current_value is not None and provider_value is not None:
                self.nb_existing_nutrient_values[provider_nutrient_id] += 1
            if current_value == provider_value:
                all_changed = False
                continue
            if current_value is not None and provider_value is not None and abs(provider_value - current_value) < 0.0001: # Float precision issue
                all_changed = False
                continue
            if current_value is None:
                status = 'new'
                #print("[NEW] %s (%s) : %s" % (provider_food_name, self.provider_nutrients[provider_nutrient_id], provider_value))
            elif provider_value is None:
                status = 'deleted'
                #print("[DEL] %s (%s) : %s" % (provider_food_name, foodnutrient.nutrient.name, current_value))
            else:
                self.nb_changed_nutrient_values[provider_nutrient_id] += 1
                status = 'updated'
                #if current_value != 0 and abs(provider_value - current_value) / current_value  > 0.2:
                    # More than 20% diff !
                    #print("[UPT] %s (%s) : %s -> %s" % (provider_food_name, foodnutrient.nutrient.name, current_value, provider_value))
            
            self.stats[status][self.provider_nutrients[provider_nutrient_id]] += 1
            # Updating DATABASE
            if foodnutrient is None:
                FoodNutrient.objects.create(food=bdd_food,
                                            nutrient_id = self.provider_to_nutrient_id[provider_nutrient_id],
                                            amount_per_gram = provider_value,
                                            raw_state_id = cooking_raw_key[0],
                                            cooking_method_id = cooking_raw_key[1])
            elif provider_value is None:
                foodnutrient.delete()
            else:
                foodnutrient.amount_per_gram = provider_value
                foodnutrient.save()
        
        assert self.allow_change_all or not all_changed, "Alert : all nutrients modified for food %s" % bdd_food.name
