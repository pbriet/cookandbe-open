#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script intends to load the files from the CIQUAL database
"""

import sys
import os
import codecs
from collections                import defaultdict
from scripts.pgsql_connection   import PGSQLScript
import csv
import re


class CIQUALLoader(PGSQLScript):
    def __init__(self, main_path):
        PGSQLScript.__init__(self)
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM recipe_mgr_foodsource WHERE name='CIQUAL'")
        self.ciqual_id = str(cur.fetchone()[0])
        self.main_path = main_path

    def fill_db(self):
        """
        Load CSV files into PGSQL
        """
        with open(os.path.join(self.main_path, "food_groups.csv")) as f:
            food_groups_to_insert = []
            for i, row in enumerate(csv.reader(f, delimiter=CSV_DELIMITER)):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGGPCD', 'ORIGGPFR', 'ORIGGPENG']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                    
                hierarchy_code, caption_fr, caption_en = row
                food_groups_to_insert.append([hierarchy_code, caption_fr, self.ciqual_id])
            self.multiple_insertion(food_groups_to_insert, "recipe_mgr_category", ["hierarchy_code", "name", "source_id"])


        #We retrieve the food group ID attached to each hierarchy_code
        food_groups_ids = {}
        cur = self.connection.cursor()
        cur.execute("SELECT id, hierarchy_code FROM recipe_mgr_category WHERE source_id='%s'" % self.ciqual_id)
        for food_g in cur.fetchall():
            food_groups_ids[food_g[1]] = food_g[0]


        food_original_id_to_id = {}

        with open(os.path.join(self.main_path, "food.csv")) as f:
            foods_to_insert = []
            for i, row in enumerate(csv.reader(f, delimiter=CSV_DELIMITER)):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGFDCD', 'ORIGFDNM', 'ORIGGPCD', 'ENGFDNAM']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                food_code, caption_fr, hierarchy_code, caption_en = row
                original_id = int(float(food_code))
                # Inserting food
                food_id = self.solo_insertion([self.ciqual_id, caption_fr, caption_fr, "1", original_id], "recipe_mgr_food", ["food_source_id", "name", "full_name", "enabled", "original_id"])
                food_original_id_to_id[original_id] = food_id

                # Inserting link between food and category
                food_group_id = food_groups_ids[hierarchy_code]
                self.solo_insertion([food_id, food_group_id], "recipe_mgr_foodcategory", ["food_id", "category_id"])


        nutrient_original_id_to_id = {}

        NUTRIENT_RE = re.compile('^(.+)\((\S+)\/100g\)$')

        # nutrients we don't want to store
        SKIP_NUTRIENTS = ["Energie, Règlement UE 1169/2011 (kJ/100g)",
                          "Protéines (g/100g)", # 'Protéines brutes' est le standard
                          ]
        # nutrients not in the CNF
        NEW_NUTRIENTS = {"Energie, N x facteur Jones, avec fibres (kJ/100g)" : "energie, n x facteur jones, avec fibres (kilojoules)",
                         "Energie, N x facteur Jones, avec fibres (kcal/100g)" : "energie, n x facteur jones, avec fibres (kilocalories)",
                         "Iode (µg/100g)": "iode",
                         "Polyols totaux (g/100g)": "polyols totaux",
                         "Vitamine E (mg/100g)": "vitamine e", # (sum of tocophérols)
                         "Acides organiques (g/100g)": "acides organiques"}
                         
        # nutrients redundant with CNF
        MATCH_NUTRIENTS = {"Energie, Règlement UE 1169/2011 (kJ/100g)": "énergie (kilojoules)",
                           "Energie, Règlement UE 1169/2011 (kcal/100g)": "énergie (kilocalories)",
                           "Protéines brutes, N x 6.25 (g/100g)": "protéines",
                           "Glucides (g/100g)": "glucides totaux (par différence)",
                           "Sucres (g/100g)": "sucres totaux",
                           "Fibres (g/100g)": "fibres alimentaires totales",
                           "Lipides (g/100g)": "lipides totaux",
                           "AG saturés (g/100g)": "acides gras saturés totaux",
                           "AG monoinsaturés (g/100g)": "acides gras monoinsaturés  totaux",
                           "AG polyinsaturés (g/100g)": "acides gras polyinsaturés totaux",
                           "AG 4:0, butyrique (g/100g)": "acides gras saturés, 4:0, butanoïque",
                           "AG 6:0, caproïque (g/100g)": "acides gras saturés, 6:0, hexanoïque",
                           "AG 8:0, caprylique (g/100g)": "acides gras saturés, 8:0, octanoïque",
                           "AG 10:0, caprique (g/100g)": "acides gras saturés, 10:0, décanoïque",
                           "AG 12:0, laurique (g/100g)": "acides gras saturés, 12:0, dodécanoïque",
                           "AG 14:0, myristique (g/100g)": "acides gras saturés, 14:0, tétradécanoïque",
                           "AG 16:0, palmitique (g/100g)": "acides gras saturés, 16:0, hexadécanoïque",
                           "AG 18:0, stéarique (g/100g)": "acides gras saturés, 18:0,  octadécanoïque",
                           "AG 18:1 9c (n-9), oléique (g/100g)": "acides gras monoinsaturés, 18:1c, octadécénoïque",
                           # Ou bien acide gras monoinsaturés, 18:1t, octadécénoïque,
                           # Ou bien acides gras monoinsaturés, 18:1non différencié, octadécénoïque
                           # Ou aucun de ceux-là ?
                           "AG 18:2 9c,12c (n-6), linoléique (g/100g)": "acides gras polyinsaturés, 18:2 c,c n-6, linoléique, octadécadiénoïque",
                           "AG 18:3 c9,c12,c15 (n-3), alpha-linolénique (g/100g)": "acides gras polyinsaturés, 18:3 c,c,c  n-3, linolénique, octadécatriénoïque",
                           "AG 20:4 5c,8c,11c,14c (n-6), arachidonique (g/100g)": "acides gras polyinsaturés, 20:4 n-6, eïcosatétraénoïque",
                           "AG 20:5 5c,8c,11c,14c,17c (n-3), EPA (g/100g)": "acides gras polyinsaturés, 20:5 n-3, eïcosapentaénoïque",
                           "AG 22:6 4c,7c,10c,13c,16c,19c (n-3), DHA (g/100g)": "acides gras polyinsaturés,  22:6 n-3, docosahexaénoïque",
                           "Beta-Carotène (µg/100g)": "béta carotène",
                           "Vitamine D (µg/100g)": "vitamine d (microgrammes)",
                           "Vitamine B1 ou Thiamine (mg/100g)": "thiamine",
                           "Vitamine B2 ou Riboflavine (mg/100g)": "riboflavine",
                           "Vitamine B3 ou PP ou Niacine (mg/100g)": "niacine (acide nicotinique) préformée",
                           "Vitamine B5 ou Acide pantothénique (mg/100g)": "acide pantothénique",
                           "Vitamine B6 (mg/100g)": "vitamine b-6",
                           "Vitamine B12 (µg/100g)": "vitamine b-12",
                           "Vitamine B9 ou Folates totaux (µg/100g)": "folacine totale",  # Was "équivalents de folate alimentaire (éfa)" before 2013/10/22
                           "Cholestérol (mg/100g)": "cholesterol",
                                                      }

        assert len(set(MATCH_NUTRIENTS.values())) == len(MATCH_NUTRIENTS), "2 similar values for 2 different keys !?"

        skipped_nutrients_ids = set()

        with open(os.path.join(self.main_path, "components.csv")) as f:
            for i, row in enumerate(csv.reader(f, delimiter=CSV_DELIMITER)):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGCPCD', 'C_ORIGCPNMABR', 'C_ENGCPNAMABR']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                    
                nutrient_code, caption_fr, caption_en = row
                original_id = int(float(nutrient_code))
                
                if caption_fr in SKIP_NUTRIENTS:
                    #print("skip <%s>" % caption_fr)
                    skipped_nutrients_ids.add(original_id)
                    continue

                regexp_match = NUTRIENT_RE.match(caption_fr)
                if not regexp_match:
                    assert False, "cannot match nutrient: %s" % caption_fr
                nutrient_name = regexp_match.group(1).strip().lower()
                nutrient_unity = regexp_match.group(2).strip().lower()

                cur = self.connection.cursor()
                cur.execute("SELECT id FROM recipe_mgr_nutrient WHERE name=%s", [nutrient_name])
                if cur.rowcount == 0:
                    if caption_fr in NEW_NUTRIENTS:
                        # Inserting nutrient
                        nutrient_name_to_insert = NEW_NUTRIENTS[caption_fr]
                        nutrient_id = self.solo_insertion([nutrient_name_to_insert, nutrient_unity, "", str(original_id)], "recipe_mgr_nutrient", ["name", "unit", "infoods_tagname", "original_id"])
                    elif caption_fr in MATCH_NUTRIENTS:
                        #print("match <%s>" % nutrient_name)
                        cur.execute("SELECT id FROM recipe_mgr_nutrient WHERE name=%s", [MATCH_NUTRIENTS[caption_fr]])
                        assert cur.rowcount == 1, "failed to retrieve nutrient with name: <%s>" % MATCH_NUTRIENTS[caption_fr]
                        nutrient_id = cur.fetchone()[0]
                    else:
                        assert False, "dunno what to do with this nutrient: <%s> <%s>" % (nutrient_name, caption_fr)
                else:
                    #print("auto-match <%s>" % nutrient_name)
                    nutrient_id = cur.fetchone()[0]


                nutrient_original_id_to_id[original_id] = nutrient_id

        LESS_THAN_RE = re.compile(r'^\< \d+(\,\d+)?$')
        with open(os.path.join(self.main_path, "compiled_data.csv")) as f:
            values_to_insert = []
            for i, row in enumerate(csv.reader(f, delimiter=CSV_DELIMITER)):
                if i == 0: continue # empty line
                if i == 1:
                    assert row == ['ORIGFDCD', 'ORIGCPCD', 'SELVALtexte', 'VALMIN', 'VALMAX', 'N', 'CCEUROFIR', 'C_SOURCE']
                    continue # Headers
                if len(row) == 1 and row[0].endswith("Rows retrieved"):
                    continue # End of file
                food_original_id, nutrient_original_id, value, x, y, z, w, z = row
                food_original_id = int(float(food_original_id))
                nutrient_original_id = int(float(nutrient_original_id))
                if nutrient_original_id in skipped_nutrients_ids:
                    # We haven't kept this nutrient
                    continue
                food_id = food_original_id_to_id[food_original_id]
                nutrient_id = nutrient_original_id_to_id[nutrient_original_id]
                if value == "-":
                    # Missing
                    continue
                if value == "traces" or LESS_THAN_RE.match(value):
                    # ...  what to do ?
                    continue
                value = float(value.replace(",", ".")) / 100  # Per 100g -> per g
                values_to_insert.append([food_id, nutrient_id, value])
        self.multiple_insertion(values_to_insert, "recipe_mgr_foodnutrient", ["food_id", "nutrient_id", "amount_per_gram"])

    
        
if __name__ == "__main__":
    loader = CIQUALLoader(sys.argv[1])
    loader.fill_db()
