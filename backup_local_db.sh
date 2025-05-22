#!/bin/bash

# WARNING: This script removes ALL TABLES from local PGSQL
# Then downloads a PostgreSQL backup from staging and restores it

set -ex

echo ""
echo "--> Dumping local DB"
echo ""

now=`date +"%Y_%m_%d_%H_%M_%S"`
filename=pg_local_dump_$1_$now.psql

docker compose exec db /bin/bash -c "/backups/dump_script.sh $1 /backups/$filename && echo Database backuped"
