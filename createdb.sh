#!/bin/bash

# Database credentials
DB_NAME="wargame"
DB_USER="postgres"
DB_PASSWORD="post"
DB_HOST="localhost"

# path to the SQL file
SQL_FILE="createDatabase.sql"

echo "Creating database..."
PGPASSWORD=$DB_PASSWORD createdb -U $DB_USER -h $DB_HOST $DB_NAME
 -E UTF8 --owner=$DB_USER --connection-limit=-1
PGPASSWORD=$DB_PASSWORD psql -U $DB_USER -h $DB_HOST -d $DB_NAME -f $SQL_FILE
echo "Database created."