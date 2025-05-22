from nutrient.management.commands._nutrient_update  import NutrientUpdater

from subprocess                  import call
from collections                 import defaultdict
import os
import re
import csv
import codecs
"""
This scripts updates the nutrient values from the CNF database
"""

# 2010 : ./manage.py cnf_update http://www.hc-sc.gc.ca/fn-an/alt_formats/hpfb-dgpsa/zip/nutrition/CNF_DBF.zip

CSV_DELIMITER = "$"

class Command(NutrientUpdater):
    args = 'http_link'
    help = 'Load nutrient values from a CNF database file'
    
    TMP_PATH = '/tmp/cnf_dbf'
    ID_BDD_FIELD = 'cnf_id'
    SOURCE_NAME = 'CNF'
    
    EXCLUDED_PROVIDER_NUTRIENT_IDS = []

    EXPECTED_NB_NUTRIENTS = 150
    CHECK_RAW_STATE_COOKING_METHOD = False # Temporary
    
    """
    ================= DOWNLOAD / EXTRACTION  =======================
    """
    def download_extract_data(self, http_link):
        """
        Retrieve data from the ANSES website (given link)
        """
        print("")
        print("Downloading / Extracting CNF...")
        # Downloading and unzipping
        call(["wget", http_link, "-O", "/tmp/cnf_dbf/data.zip"])
        call(["unzip", "data.zip"])
        
        self.extract_cnf("FOOD_NM.DBF", "FD_ID,FD_GRP_ID,A_FD_NMF,L_FD_NMF", "opt_food.txt")
        self.extract_cnf("NT_NM.DBF",   "NT_ID,NT_NMF,UNIT,TAGNAME",         "opt_nutrients.txt")
        self.extract_cnf("NT_AMT.DBF",  "FD_ID,NT_ID,NT_VALUE,STD_ERR",      "opt_food_nutrients.txt")
   
   
    def extract_cnf(self, input_file_name, columns, output_file_name):
        with open(output_file_name, "w") as f:
            try:
                call(["dbf_dump", "--fs=%s" % CSV_DELIMITER, input_file_name, "--fields", columns], stdout=f)
            except FileNotFoundError:
                print("FILE-NOT-FOUND-ERROR")
                print("check that dbf_dump is correctly installed")
                print("Run : sudo apt-get install libdbd-xbase-perl")
                exit(1)
    
    def fix_encoding(self, s):
        """
        Some strings in the DBF files seem not to be correctly encoded  (uppercase accents)
        fix them manually
        """
        FIX_ORDS = {947: 'ô', 969: 'û', 9560: 'è', 9573: 'ê', 9558: 'à', 9570: 'â', 9578: 'ï', 9579: "î"}
        for i in range(len(s)):
            c = s[i]
            if ord(c) in FIX_ORDS:
                s = s[:i] + FIX_ORDS[ord(c)] + s[i + 1:]
            elif ord(c) > 9000:
                assert False, "Invalid char in: %s" % s
        return s

    def preload_provider_nutrients(self):
        """
        FILLS self.provider_nutrients
        {provider_nutrient_id : provider_name}
        """
        self.provider_nutrients = {}
        # NUTRIENTS
        with codecs.open("opt_nutrients.txt", "r", "cp863") as f:
            data = list(csv.reader(f, delimiter=CSV_DELIMITER))
            for row in data:
                row = [r.lower() for r in row]
                nutrient_id = int(row[0])
                nutrient_name = self.fix_encoding(row[1])  # Problems in the encoding of nutrient name
                self.provider_nutrients[nutrient_id] = nutrient_name
    
    def preload_provider_foodnutrients(self):
        """
        FILLS self.provider_foodnutrients
        {original_id: {nutrient_id: value}}
        """
        self.provider_foodnutrients = defaultdict(dict)
        
        # FOOD NUTRIENTS
        with codecs.open("opt_food_nutrients.txt", "r", "cp863") as f:
            for row in csv.reader(f, delimiter=CSV_DELIMITER):
                if row[2] == '':
                    continue  # Unknown amount of nutrients (!?)
                amount_per_gram = float(row[2])/100  # Amount of nutrient per gram instead of per 100g
                if row[3] == '':
                    std_err = None
                else:
                    std_err = float(row[3])/100  # Same for standard deviation
                food_id = int(row[0])
                nutrient_id = int(row[1])
                 
                self.provider_foodnutrients[food_id][nutrient_id] = amount_per_gram
                
    
    def preload_provider_food_names(self):
        """
        FILLS self.provider_food_id_to_name
        {original_id: original_name}
        """
        self.provider_food_id_to_name = {}
        
        with codecs.open("opt_food.txt", "r", "cp863") as food_file:
            for row in csv.reader(food_file, delimiter=CSV_DELIMITER):
                food_name = row[-1] 
                # Problems in the encoding of food name (only short name)
                # self.fix_encoding(row[-2].lower())
                food_id = int(row[0])
                self.provider_food_id_to_name[food_id] = food_name.lower()
                

