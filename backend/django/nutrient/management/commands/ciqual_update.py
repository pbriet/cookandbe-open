from nutrient.management.commands._nutrient_update  import NutrientUpdater

from subprocess                  import call
from collections                 import defaultdict
import os
import re
import csv
"""
This scripts updates the nutrient values from the ciqual database
(Given link to a MDB zipfile)
"""

# 2013 : ./manage.py ciqual_update https://pro.anses.fr/TableCIQUAL/Documents/CIQUAL2013-Donneesmdb.zip

LESS_THAN_RE = re.compile(r'^\< (\d+(\,\d+)?)$')

class Command(NutrientUpdater):
    args = 'http_link'
    help = 'Update nutrient values from a CIQUAL MDB'
    
    TMP_PATH = '/tmp/ciqual_mdb'
    ID_BDD_FIELD = 'ciqual_id'
    SOURCE_NAME = 'CIQUAL'
    
    # "Energie, Règlement UE 1169/2011 (kJ/100g)"
    #"Protéines (g/100g)"
    EXCLUDED_PROVIDER_NUTRIENT_IDS = [327, 25000]
    
    EXPECTED_NB_NUTRIENTS = 58

    
    """
    ================= DOWNLOAD / EXTRACTION  =======================
    """
    def download_extract_data(self, http_link):
        """
        Retrieve data from the ANSES website (given link)
        """
        print("")
        print("Downloading / Extracting CIQUAL...")
        # Downloading and unzipping
        call(["wget", http_link, "-O", "/tmp/ciqual_mdb/data.zip"])
        call(["unzip", "data.zip"])
        
        # Retrieving uncompressed filename
        accdb_filename = self.get_accdb_filename()
        self.convert_accdb_to_csv(accdb_filename)
    
    def convert_accdb_to_csv(self, accdb_filename):
        """
        Using mdbtools, extracting data from accdb files
        """
        
        for table_name in ("COMPILED_DATA", "COMPONENT", "FOOD", "FOOD_GROUPS", "REFERENCE"):
            with open("query.sql", "w") as f:
                f.write("SELECT * FROM %s" % table_name)
            with open("%s.csv" % table_name, "w") as f:
                try:
                    call(["mdb-sql", '"%s"' % accdb_filename, "-p", "-d", ";", "-i", "query.sql"], stdout=f)
                except FileNotFoundError:
                    print("FILE-NOT-FOUND-ERROR")
                    print("check that mdbtools is correctly installed")
                    print("Run : sudo apt-get install mdbtools")
                    exit(1)
        
    def get_accdb_filename(self):
        for fname in os.listdir('/tmp/ciqual_mdb'):
            if fname.endswith('.accdb'):
                return fname
        return None
    
    def preload_provider_nutrients(self):
        """
        FILLS self.provider_nutrients
        {provider_nutrient_id : provider_name}
        """
        self.provider_nutrients = {}
        with open("COMPONENT.csv") as f:
            for i, row in enumerate(csv.reader(f, delimiter=';')):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGCPCD', 'ECOMPID', 'INFDSTAG', 'C_ORIGCPNMABR', 'C_ENGCPNAMABR']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                    
                nutrient_code, x, y, caption_fr, caption_en = row
                original_id = int(float(nutrient_code))
                if original_id in self.EXCLUDED_PROVIDER_NUTRIENT_IDS:
                    continue
                self.provider_nutrients[original_id] = caption_fr
    
    def preload_provider_foodnutrients(self):
        """
        FILLS self.provider_foodnutrients
        {original_id: {nutrient_id: value}}
        """
        self.provider_foodnutrients = defaultdict(dict)
        
        with open("COMPILED_DATA.csv") as f:
            for i, row in enumerate(csv.reader(f, delimiter=';')):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGFDCD', 'ORIGCPCD', 'SELVALtexte', 'VALMIN', 'VALMAX', 'N', 'CCEUROFIR', "RANG", "SOURCE"]
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                food_original_id, nutrient_original_id, value, x, y, z, w, y, z = row
                food_original_id = int(float(food_original_id))
                nutrient_original_id = int(float(nutrient_original_id))
                if nutrient_original_id in self.EXCLUDED_PROVIDER_NUTRIENT_IDS:
                    continue
                
                matched = LESS_THAN_RE.match(value)
                if matched:
                    value = float(matched.group(1).replace(',', '.')) / 100
                elif value == "-":
                    # Missing
                    value = None
                elif value == "traces":
                    value = 0
                else:
                    value = float(value.replace(",", ".")) / 100  # Per 100g -> per g
                
                self.provider_foodnutrients[food_original_id][nutrient_original_id] = value
    
    def preload_provider_food_names(self):
        """
        FILLS self.provider_food_id_to_name
        {original_id: original_name}
        """
        self.provider_food_id_to_name = {}
        with open(os.path.join("FOOD.csv")) as f:
            for i, row in enumerate(csv.reader(f, delimiter=';')):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGFDCD', 'ORIGFDNM', 'ENGFDNAM', 'SCINAM', 'ORIGGPCD']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                food_code, caption_fr, caption_en, scientific_name, hierarchy_code = row
                original_id = int(float(food_code))
                self.provider_food_id_to_name[original_id] = caption_fr.lower()

