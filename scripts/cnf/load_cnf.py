#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script intends to load the files from the Canadian Nutrient File,
previously converted into CSV format.
"""

import sys
import os
import codecs
from collections                import defaultdict
from scripts.pgsql_connection   import PGSQLScript
import csv

class CNFLoader(PGSQLScript):
    def __init__(self, directory):
        PGSQLScript.__init__(self)
        self.directory = directory

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

    def fill_db(self):
        """
        Load CSV files into PGSQL
        """
        # NUTRIENTS
        with codecs.open(os.path.join(self.directory, "opt_nutrients.txt"), "r", "cp863") as f:
            data = list(csv.reader(f, delimiter=CSV_DELIMITER))
            transformed = []
            for row in data:
                row = [r.lower() for r in row]
                row[1] = self.fix_encoding(row[1])  # Problems in the encoding of nutrient name
                transformed.append(row)
            # NT_ID,NT_NMF,UNIT,TAGNAME
            self.multiple_insertion(transformed, "recipe_mgr_nutrient", ["id", "name", "unit", "infoods_tagname"])

        # FOOD CATEGORIES
        with codecs.open(os.path.join(self.directory, "opt_categories.txt"), "r", "cp863") as f:
            data = list(csv.reader(f, delimiter=CSV_DELIMITER))
            # FD_GRP_ID,FD_GRP_NMF
            self.multiple_insertion(data, "recipe_mgr_category", ["id", "name"])

        # FOOD
        with codecs.open(os.path.join(self.directory, "opt_food_loss.txt"), "r", "cp863") as food_loss_file:
            with codecs.open(os.path.join(self.directory, "opt_food.txt"), "r", "cp863") as food_file:
                food_loss_per_food_id = defaultdict(float)
                for row in csv.reader(food_loss_file, delimiter=CSV_DELIMITER):
                    food_loss_per_food_id[row[0]] = float(row[1])/100

                food_entries = []
                food_category_entries = []
                for row in csv.reader(food_file, delimiter=CSV_DELIMITER):
                    row = [r.lower() for r in row]
                    row[-2] = self.fix_encoding(row[-2])  # Problems in the encoding of food name (only short name)
                    #if "saucisse, boeuf, fra" in row[-2]:
                        #print(row[-2])
                        #for i in range(len(row[-2])):
                            #print(ord(row[-2][i]))
                        #exit(1)
                    #FD_ID,FD_GRP_ID,A_FD_NMF,L_FD_NMF
                    food_id = row[0]
                    group_id = row.pop(1)
                    row.append(food_loss_per_food_id[food_id])
                    # Removing loss_coeff
                    row = row[:-1]
                    # Adding enabled=True
                    row.append(True)
                    assert len(row) == 5, "Invalid row: %s" % row
                    food_entries.append(row)
                    food_category_entries.append([food_id, group_id])
                # Insert into food table
                self.multiple_insertion(food_entries, "recipe_mgr_food", ["id", "name", "full_name", "enabled"])
                
                # Insert into foodCategory table
                self.multiple_insertion(food_category_entries, "recipe_mgr_foodcategory", ["food_id", "category_id"])

        # FOOD NUTRIENTS
        with codecs.open(os.path.join(self.directory, "opt_food_nutrients.txt"), "r", "cp863") as f:
            transformed = []
            for row in csv.reader(f, delimiter=CSV_DELIMITER):
                if row[2] == '':
                    continue  # Unknown amount of nutrients (!?)
                row[2] = float(row[2])/100  # Amount of nutrient per gram instead of per 100g
                if row[3] == '':
                    row[3] = None
                else:
                    row[3] = float(row[3])/100  # Same for standard deviation
                 
                transformed.append(row)

            # FD_ID,NT_ID,NT_VALUE,STD_ERR
            self.multiple_insertion(transformed, "recipe_mgr_foodnutrient", ["food_id", "nutrient_id", "amount_per_gram", "std_err"])
        

        # MEASURES
        with codecs.open(os.path.join(self.directory, "opt_measure.txt"), "r", "cp863") as f:
            data = list(csv.reader(f, delimiter=CSV_DELIMITER))
            # FD_GRP_ID,FD_GRP_NMF
            self.multiple_insertion(data, "recipe_mgr_measure", ["id", "name"])
            
            
        with codecs.open(os.path.join(self.directory, "opt_food_conversion.txt"), "r", "cp863") as food_conversion_file:
            data = []
            for row in csv.reader(food_conversion_file, delimiter=CSV_DELIMITER):
                # FD_ID,MSR_ID,CONV_FAC
                if row[2] == '':
                    continue # Invalid entry
                row[2] = float(row[2]) * 100  # Conversions are "comparing to 100g"
                data.append(row)
            self.multiple_insertion(data, "recipe_mgr_foodconversion", ["food_id", "measure_id", "value"])

        
if __name__ == "__main__":
    loader = CNFLoader(sys.argv[1])
    loader.fill_db()
