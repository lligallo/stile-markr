#!/bin/bash
set -e

# Automatically export variables
set -a
# Load environment variables from .env file
source .env
#change the database so we don't erase the contents during the tests
PG_DBNAME=postgres
set +a

export PYTHONPATH="./src:$PYTHONPATH"

echo "Upgrading the database to the latest version..."
alembic upgrade head
echo "Database upgraded successfully."

echo "THERE MUST BE AN INSTANCE OF THE HTTP SERVER RUNNING FOR THESE TESTS TO EXECUTE"

python3 -m unittest test/exams_analytics/interface/scan_import/test_http_rest_facade.py