#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script detects the cooking methods in the CIQUAL database, and
split them into separate tables  (CookingMethod, Food)
"""

from scripts.pgsql_connection   import PGSQLScript
from collections                import defaultdict
import yaml
import re
import numpy


class CIQUALCookingExtractor(PGSQLScript):
    def __init__(self):
        PGSQLScript.__init__(self)
        cur = self.connection.cursor()
        cur.execute("SELECT id FROM recipe_mgr_foodsource WHERE name='CIQUAL'")
        self.ciqual_id = str(cur.fetchone()[0])


        cur.execute("SELECT id, name FROM recipe_mgr_rawstate")
        self.db_raw_states = {}
        for row in cur.fetchall():
            # Name -> ID
            self.db_raw_states[row[1]] = row[0]

        cur.execute("SELECT id, name FROM recipe_mgr_cookingmethod")
        self.db_cooking_methods = {}
        for row in cur.fetchall():
            # Name -> ID
            self.db_cooking_methods[row[1]] = row[0]

        
        self.reload_cooking_methods()
        self.reload_non_cooking_methods()

    def reload_cooking_methods(self):
        with open("cooking_methods.yml") as f:
            self.cooking_methods = yaml.load(f)
            
    def reload_non_cooking_methods(self):
        with open("non_cooking_methods.yml") as f:
            self.non_cooking_methods = yaml.load(f)

    def reload_dico_cooking_methods(self):
        with open("dico_cooking_methods.yml") as f:
            self.dico_cooking_methods = yaml.load(f)
            
    def add_cooking_method(self, value):
        self.cooking_methods.append(value)
        with open("cooking_methods.yml", "a") as f:
            f.write("- %s\n" % value)

    def add_non_cooking_method(self, value):
        self.non_cooking_methods.append(value)
        with open("non_cooking_methods.yml", "a") as f:
            f.write("- %s\n" % value)
            
    def detect(self):
        cur = self.connection.cursor()
        cur.execute("SELECT id, name FROM recipe_mgr_food WHERE food_source_id=%s", [self.ciqual_id])
        all_items = cur.fetchall()
        for i, food in enumerate(all_items):
            food_name = food[1]
            food_name = food_name.split(',')
            if len(food_name) > 1:
                last_sub_food_name = food_name[-1]
                last_sub_food_name = last_sub_food_name.strip()
                if last_sub_food_name in self.non_cooking_methods or last_sub_food_name in self.cooking_methods:
                    continue
                
                print("%i/%i" % (i, len(all_items)))
                print("Unknown sub food name : <%s> (%s)" % (last_sub_food_name, food_name))
                s = ""
                while s not in ("y", "n"):
                    s = input('Is it a cooking method  (y/n) --> ')
                    s = s.lower()
                if s == "y":
                    self.add_cooking_method(last_sub_food_name)
                else:
                    self.add_non_cooking_method(last_sub_food_name)

    def detect_food_raw_state(self, food_name):
        """
        Returns what is the raw state of a given food
        """
        match_canned = re.compile(r'(.+)(appertisée?s?(?:, égouttée?s?)?)(.*)').match(food_name)
        match_frozen = re.compile(r'(.+)(surgelée?s?|congelée?s?)(.*)').match(food_name)
        match_fresh = re.compile(r'(.+)[\s,](frais|fraîches?)(.*)').match(food_name)
        
        if match_canned:
            raw_state = "en conserve"
            food_name = match_canned.group(1) + match_canned.group(3)
        elif match_frozen:
            raw_state = "surgelé"
            food_name = match_frozen.group(1) + match_frozen.group(3)
        else:
            raw_state = "frais"
            if match_fresh and "crême" not in food_name.lower():
                food_name = match_fresh.group(1) + match_fresh.group(3)

        return raw_state, food_name


    def detect_food_cooking_methods(self, food_name):
        """
        Returns the list of cooking_methods that are used for this food
        Also returns the food_name without the cooking method described
        """
        food_cooking_methods = []
        for cooking_method in self.cooking_methods:
            if cooking_method in food_name:
                # check that cooking method keyword is not a substring of the food! (like "biscuit")
                i = food_name.rindex(cooking_method)

                if food_name[i-1] not in (' ', ',') or\
                    (len(food_name) > i + len(cooking_method) and\
                    food_name[i + len(cooking_method)] not in (' ', ',')):
                    #print("sub part of food name: ", food_name)
                    continue


                food_cooking_methods.append(cooking_method)
                food_name = food_name.replace(cooking_method, '')
        return food_cooking_methods, food_name

    def _get_cooking_method(self, factorized_cooking_methods, original_food_name):
        """
        From a list of cooking methods detected, return ONE cooking method (if any)
        """
        if 'Tartine craquante' in original_food_name and "grillé" in factorized_cooking_methods:
            factorized_cooking_methods.remove("grillé")

        if len(factorized_cooking_methods) == 0:
            # Raw product
            #print("RAW: %s" % food_name)
            return None
            
        if len(factorized_cooking_methods) == 1:
            # Cooked one way
            cooking_method = list(factorized_cooking_methods)[0]
            if cooking_method == "cru":
                #print("RAW - explicit: %s" % original_food_name)
                return None
            #print("COOKED (%s): %s" % (cooking_method, original_food_name))
        else:
            if len(factorized_cooking_methods) > 1 and 'surgelé' in factorized_cooking_methods:
                factorized_cooking_methods.remove('surgelé')
                if len(factorized_cooking_methods) == 1:
                    # Frozen + cooked = 1 cooking method
                    factorized_cooking_methods = set(['surgelé ' + factorized_cooking_methods.pop()])
            elif 'cuit' in factorized_cooking_methods:
                factorized_cooking_methods.remove('cuit')
            if 'braisé' in factorized_cooking_methods and 'poêlé' in factorized_cooking_methods:
                # Default will be poêlé
                factorized_cooking_methods.remove('braisé')
            if 'Pomme de terre frite' in original_food_name and len(factorized_cooking_methods) > 1 and 'frit' in factorized_cooking_methods:
                factorized_cooking_methods.remove('frit')
            
            # Cooked multiple ways ??
            assert len(factorized_cooking_methods) == 1, "multiple ways of cooking <%s>: %s" % (original_food_name, list(factorized_cooking_methods))
            cooking_method = factorized_cooking_methods.pop()
            #print("MULTIPLE (%s): %s" % (cooking_method, original_food_name))
            
        return cooking_method


    def _clean_food_name(self, food_name):
        """
        Clean food_name after having removed the cooking methods.
        """

        food_name = food_name.replace('(aliment moyen)', '')
        while food_name[-1] in (' ', ','):
            food_name = food_name[:-1]
        food_name = food_name.replace(', ,', ',')
        food_name = food_name.replace('  ', ' ')
        food_name = food_name.replace(' ,', ',')
        food_name = food_name.strip()
        if food_name.endswith(', ou'): food_name = food_name[:-4]
        if food_name.endswith(' et'): food_name = food_name[:-3]
        
        return food_name
        

    def split(self):
        """
        Split foods between raw food and cooking method
        """
        # Loading / extracting data
        self.reload_dico_cooking_methods()
        self.cooking_methods = sorted(self.dico_cooking_methods.keys(), key=lambda x:len(x), reverse=True)
        cur = self.connection.cursor()
        cur.execute("SELECT id, name, original_id FROM recipe_mgr_food WHERE food_source_id=%s", [self.ciqual_id])

        # Factorizing by food name the different way of cooking one ingredient
        # Food name -> raw state -> cooking method
        by_food_name = defaultdict(lambda: defaultdict(dict))

        all_cooking_methods = set()
        
        for food in cur.fetchall():
            # Iteration on food
            food_id, food_name, original_id = food
            original_food_name = food_name
            food_raw_state, food_name  = self.detect_food_raw_state(food_name)
            food_raw_state_id = self.db_raw_states[food_raw_state]
            food_cooking_methods, food_name = self.detect_food_cooking_methods(food_name)

            # Ok, now we have a list of cooking methods for a given food
            # Some can be redundant, or have different names.
            # Let's use the dictionnary
            factorized_cooking_methods = set()
            for f in food_cooking_methods:
                assert f in self.dico_cooking_methods, "No entry in dico for <%s>" % f
                factorized_cooking_methods.add(self.dico_cooking_methods[f])
                
            # Retrieve the ONE cooking method that will be kept
            cooking_method = self._get_cooking_method(factorized_cooking_methods, original_food_name)
            # Clean the food name
            food_name = self._clean_food_name(food_name)
            if cooking_method is None:
                cooking_method = "cru"
            all_cooking_methods.add(cooking_method)
            by_food_name[food_name][food_raw_state][cooking_method] = {"id": food_id, "original_id": original_id}

        self.alter_database(by_food_name, all_cooking_methods)


    def alter_database(self, by_food_name, all_cooking_methods):
        """
        Change the content of the database
        """
        ### CREATING COOKING METHODS

        cur = self.connection.cursor()
        
        for cooking_method in all_cooking_methods:
            if cooking_method not in self.db_cooking_methods:
                self.db_cooking_methods[cooking_method] = self.solo_insertion([cooking_method], 'recipe_mgr_cookingmethod', ['name'])
    
        for food_name, raw_state_and_cooking_methods in by_food_name.items():
            # All the food ids will be converted into one
            original_ids = []
            loss_coeffs = []
            per_food_id = {}
            category_ids = set()
            for raw_state, cooking_methods in raw_state_and_cooking_methods.items():
                for cooking_method, food_details in cooking_methods.items():
                    per_food_id[food_details['id']] = (raw_state, cooking_method)
                    original_ids.append(str(food_details['original_id']))
                    loss_coeffs.append(food_details['loss_coeff'])
                    cur.execute("SELECT category_id FROM recipe_mgr_foodcategory WHERE food_id='%s'" % food_details['id'])
                    for row in cur.fetchall():
                        category_ids.add(row[0])

            assert numpy.max(loss_coeffs) - numpy.min(loss_coeffs) < 0.1, "hugely variable loss coefficients: <%s> (%s)" %\
                                                                            (food_name, raw_state_and_cooking_methods)

            # Keeping the list of original ids from CIQUAL
            original_id = ":".join(original_ids)
            loss_coeff = numpy.mean(loss_coeffs)

            # Inserting new food
            new_food_id = self.solo_insertion([food_name, food_name, original_id, self.ciqual_id, True],
                                 'recipe_mgr_food',
                                ['name', 'full_name', 'original_id', 'food_source_id', 'enabled'])

            # Setting categories
            for category_id in category_ids:
                self.solo_insertion([new_food_id, category_id], 'recipe_mgr_foodcategory', ['food_id', 'category_id'])

            # Update old entries
            for old_food_id, details in per_food_id.items():
                raw_state, cooking_method = details
                cur.execute("UPDATE recipe_mgr_foodnutrient SET food_id=%s, raw_state_id=%s, cooking_method_id=%s WHERE food_id=%s ",
                            [new_food_id, self.db_raw_states[raw_state], self.db_cooking_methods[cooking_method], old_food_id])
                self.connection.commit()

            # Now deleting old entries
            for old_food_id in per_food_id.keys():
                cur.execute("DELETE FROM recipe_mgr_foodcategory WHERE food_id=%s", [old_food_id])
                self.connection.commit()
                cur.execute("DELETE FROM recipe_mgr_ingredient WHERE food_id=%s", [old_food_id])
                self.connection.commit()
                cur.execute("DELETE FROM recipe_mgr_foodconversion WHERE food_id=%s", [old_food_id])
                self.connection.commit()
                cur.execute("DELETE FROM recipe_mgr_food WHERE id=%s", [old_food_id])
                self.connection.commit()
            
        
if __name__ == "__main__":
    loader = CIQUALCookingExtractor()
    loader.detect()
    loader.split()
