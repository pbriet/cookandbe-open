#!/bin/sh

# This scripts intends to fill the Optalim database
# with the CIQUAL

# 1- Downloading
# 3- Filtering
# 4- Storing in PGSQL

#### http://www.ansespro.fr/TableCIQUAL/Documents/Ciqual_2012_v02.07_mdb_LISEZMOI.pdf

sudo apt-get install unzip mdbtools
mkdir /tmp/ciqual
cd /tmp/ciqual
wget http://www.ansespro.fr/TableCIQUAL/Documents/Ciqual_2012_v02.07.mdb.zip
unzip Ciqual_2012_v02.07.mdb.zip

# Extracting tables as CSVs
echo "SELECT * FROM COMPILED_DATA" > query.sql
mdb-sql Ciqual_2012_v02.07.mdb -p -d ';' -i query.sql > compiled_data.csv

echo "SELECT * FROM COMPONENT" > query.sql
mdb-sql Ciqual_2012_v02.07.mdb -p -d ';' -i query.sql > components.csv

echo "SELECT * FROM FOOD" > query.sql
mdb-sql Ciqual_2012_v02.07.mdb -p -d ';' -i query.sql > food.csv

echo "SELECT * FROM FOOD_GROUPS" > query.sql
mdb-sql Ciqual_2012_v02.07.mdb -p -d ';' -i query.sql > food_groups.csv

echo "SELECT * FROM REFERENCE" > query.sql
mdb-sql Ciqual_2012_v02.07.mdb -p -d ';' -i query.sql > reference.csv

cd -

python load_ciqual.py /tmp/ciqual/
python clean_ciqual.py
