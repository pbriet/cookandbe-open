#!/bin/bash

set -e
set -u

export PGPASSWORD=$POSTGRESQL_INITSCRIPTS_PASSWORD

function create_user_and_database() {
	local database=$1
	echo "  Creating user and database '$database'"
	psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_INITSCRIPTS_USERNAME" --dbname "postgres" <<-EOSQL
	    CREATE USER $database;
	    CREATE DATABASE $database;
	    GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRESQL_MULTIPLE_DATABASES" ]; then
	echo "Multiple database creation requested: $POSTGRESQL_MULTIPLE_DATABASES"
	echo "With user : $POSTGRESQL_USERNAME"
	for db in $(echo $POSTGRESQL_MULTIPLE_DATABASES | tr ',' ' '); do
		if psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_INITSCRIPTS_USERNAME" --dbname "postgres" -lqt | cut -d \| -f 1 | grep -qw $db; then
		 	echo "Already exist."
		else
			create_user_and_database $db
		fi
	done
	echo "Multiple databases created"
fi