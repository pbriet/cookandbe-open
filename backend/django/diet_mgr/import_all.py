# This file is called to import all the diet handlers
# And initialize them (registering in the Diet Model)

import diet_mgr.handlers.anc

### Level 0 diets ###

import diet_mgr.handlers.vegetarian
import diet_mgr.handlers.vegan
import diet_mgr.handlers.gluten_free

### Level 2 diets ###

import diet_mgr.handlers.slim
import diet_mgr.handlers.easy_digest
import diet_mgr.handlers.cardiovascular
import diet_mgr.handlers.diabete
import diet_mgr.handlers.hypertension
import diet_mgr.handlers.normolipidic
