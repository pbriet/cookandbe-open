#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script helps cleaning the Canadian Nutrient File.
It must be used once load_cnf.py is done
"""

import sys
import os
import codecs
from collections                import defaultdict
from scripts.pgsql_connection   import PGSQLScript
import csv
import random
import re

class CNFCleaner(PGSQLScript):
    """
    The purpose of this object is to disable foods that are
    not useful - and to clean conversion unities
    """

    def disable_food(self):
        cur = self.connection.cursor()
        cur.execute("SELECT id, name, enabled FROM recipe_mgr_food")

        we_keep = []

        to_disable = set()
        for row in cur.fetchall():
            i, name, enabled = row

            ends_with = [", HEINZ", ", THIBAULT", ", General Mills", ", Kellogg's", ", Rogers", ", Quaker", ", Nabisco", ", CANOLA HARVEST"]
            contains = [" avec ", " conserve", "O'brien", "Grignotises", "CUP-A-SOUP"]
            for e in ends_with:
                if name.endswith(e):
                    if enabled:
                        to_disable.add(i)
                    break
            else:
                for c in contains:
                    if c in name:
                        if enabled:
                            to_disable.add(i)
                        break
                else:
                    we_keep.append(name)

        print("%i to be disabled" % len(to_disable))
        print("REMAINING (sample):")
        for i in range(10):
            print("- ", we_keep[random.randint(0, len(we_keep) - 1)])

        if len(to_disable):
            update_statement = "UPDATE recipe_mgr_food SET enabled=False WHERE id=%i"
            for food_id in to_disable:
                cur.execute(update_statement % food_id)
            self.connection.commit()
        print("...")
        print("disabled")


    def clean_conversions(self):
        cur = self.connection.cursor()
        cur.execute("SELECT id, name from recipe_mgr_measure")
        measures = [m for m in cur.fetchall()]
        to_delete = []
        to_convert = []
        to_rename = []

        for m in measures:
            measure_id, measure_name = m

            match1 = re.compile("^\d*g$").match(measure_name)
            match2 = re.compile("^([\d\.]+)([\sA-z].*)$").match(measure_name)
            match3 = re.compile("^1\s(.+)$").match(measure_name)

            if match1:
                to_delete.append(m)
            elif match3:
                #1 gros citron -> gros citron
                to_rename.append((m, match3.group(1)))
            elif match2:
                #30ml -> to be divided
                new_name = match2.group(2).strip()
                to_convert.append((m, new_name, 1./float(match2.group(1))))
            else:
                print(measure_name)

        print("to_delete: ", len(to_delete))
        self.delete_measures(to_delete)
        print("to_rename: ", len(to_rename))
        self.rename_measures(to_rename)
        print("to_convert: ", len(to_convert))
        self.convert_measures(to_convert)

        # After all those modifications, some conversions are duplicated
        self.remove_conversion_duplicates()

        self.connection.commit()

    def remove_conversion_duplicates(self):
        cur = self.connection.cursor()

        cur.execute("SELECT id, name FROM recipe_mgr_measure")
        measure_name_to_ids = defaultdict(list)
        for measure in cur.fetchall():
            m_id, name = measure
            measure_name_to_ids[name].append(m_id)

        # First measure with a given name is reference
        # The others are removed
        # This dictionnary takes into key the deleted measures, and what is the replacement
        to_remove = dict()
        for measure_ids in measure_name_to_ids.values():
            if len(measure_ids) <= 1: continue
            for i in measure_ids[1:]:
                to_remove[i] = measure_ids[0]

        cur.execute("SELECT id from recipe_mgr_food")
        food_ids = [i[0] for i in cur.fetchall()]
        for food_id in food_ids:
            cur.execute("SELECT recipe_mgr_foodconversion.id, recipe_mgr_measure.id FROM recipe_mgr_foodconversion JOIN recipe_mgr_measure ON recipe_mgr_measure.id = recipe_mgr_foodconversion.measure_id WHERE recipe_mgr_foodconversion.food_id=%i" % food_id)
            food_measure_to_conv = defaultdict(list)
            for row in cur.fetchall():
                food_measure_to_conv[row[1]].append(row[0])
            for measure_id, conversion_ids in list(food_measure_to_conv.items()):
                if measure_id in to_remove:
                    replaced_with = to_remove[measure_id]
                    # Duplicate
                    if replaced_with in food_measure_to_conv:
                        # To be removed - reference is already here
                        for conversion_id in conversion_ids:
                            cur.execute("DELETE FROM recipe_mgr_foodconversion WHERE id=%i" % conversion_id)
                            assert cur.rowcount
                    else:
                        # Switch as a reference
                        for conversion_id in conversion_ids:
                            food_measure_to_conv[replaced_with].append(conversion_id)
                            cur.execute("UPDATE recipe_mgr_foodconversion SET measure_id=%i WHERE id=%i" % (replaced_with, conversion_id))
                            assert cur.rowcount

        for measure_id in to_remove.keys():
            cur.execute("SELECT recipe_mgr_foodconversion.id, recipe_mgr_foodconversion.food_id FROM recipe_mgr_foodconversion WHERE recipe_mgr_foodconversion.measure_id=%i" % measure_id)
            res = cur.fetchall()
            if len(res):
                row = list(res)[0]
                assert False, "existing food (%i) for conversion (%i) - measure %i" % (row[1], row[0], measure_id)
            cur.execute("DELETE FROM recipe_mgr_measure WHERE id=%i" % measure_id)


    def convert_measures(self, measures_to_convert):
        cur = self.connection.cursor()
        for r in measures_to_convert:
            measure, new_name, factor = r
            m_id, m_name = measure
            cur.execute("UPDATE recipe_mgr_foodconversion SET value=value*%f WHERE measure_id='%i'" % (factor, m_id))
            print("updates %i conversions" % cur.rowcount)
            cur.execute("UPDATE recipe_mgr_measure SET name=%s WHERE id=" + str(m_id), [new_name])
            assert cur.rowcount


    def rename_measures(self, measures_to_rename):
        for r in measures_to_rename:
            measure, new_name = r
            m_id, name = measure
            cur = self.connection.cursor()
            cur.execute("UPDATE recipe_mgr_measure SET name=%s WHERE id=" + str(m_id), [new_name])
        print("renamed: ", len(measures_to_rename))


    def delete_measures(self, measures):
        for measure in measures:
            m_id, name = measure

            cur = self.connection.cursor()
            cur.execute("DELETE FROM recipe_mgr_foodconversion WHERE measure_id='%i'" % m_id)
            print("removed %i conversions" % cur.rowcount)
            cur.execute("DELETE FROM recipe_mgr_measure WHERE id='%i'" % m_id)
            assert cur.rowcount




if __name__ == "__main__":
    cleaner = CNFCleaner()
    cleaner.disable_food()
    cleaner.clean_conversions()
