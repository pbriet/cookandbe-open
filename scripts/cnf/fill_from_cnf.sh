#!/bin/sh

# This scripts intends to fill the Optalim database
# with the Canadian Nutrient File

# 1- Downloading
# 2- Converting DBF to CSV
# 3- Filtering
# 4- Storing in PGSQL

#### http://www.hc-sc.gc.ca/fn-an/nutrition/fiche-nutri-data/cnf_file_structure-des_fichiers_fcen-eng.php

sudo apt-get install libdbd-xbase-perl unzip

mkdir /tmp/cnf
cd /tmp/cnf

wget http://www.hc-sc.gc.ca/fn-an/alt_formats/hpfb-dgpsa/zip/nutrition/CNF_DBF.zip CNF_DBF.zip
unzip CNF_DBF.zip

# Extract the measure names  (e.g. "1 banana", "1 litre", ...)
dbf_dump --fs='$' MEASURE.DBF --fields MSR_ID,MSR_NMF > opt_measure.txt

# Extract the conversion food to other measures  (CONV_FAC being the ratio)
dbf_dump --fs='$' CONV_FAC.DBF --fields FD_ID,MSR_ID,CONV_FAC > opt_food_conversion.txt

# Extract the amount of grams which cannot be eaten for every portion of 100g of each food.
dbf_dump --fs='$' REFUSE.DBF --fields FD_ID,REFUSE_AMT > opt_food_loss.txt

# Extract the categories
dbf_dump --fs='$' FOOD_GRP.DBF --fields FD_GRP_ID,FD_GRP_NMF > opt_categories.txt

# Extract the foods
dbf_dump --fs='$' FOOD_NM.DBF --fields FD_ID,FD_GRP_ID,A_FD_NMF,L_FD_NMF > opt_food.txt

# Extract the nutrients
dbf_dump --fs='$' NT_NM.DBF --fields NT_ID,NT_NMF,UNIT,TAGNAME > opt_nutrients.txt

# Extract the food nutrients
dbf_dump --fs='$' NT_AMT.DBF --fields FD_ID,NT_ID,NT_VALUE,STD_ERR > opt_food_nutrients.txt

cd -

python load_cnf.py /tmp/cnf
python clean_cnf.py
#rm -rf /tmp/cnf
