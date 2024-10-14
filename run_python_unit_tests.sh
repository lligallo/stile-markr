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

python3 -m unittest test/exams_analytics/empty_unit_test.py
python3 -m unittest test/exams_analytics/interface/pg_db/test_raw_import_repository_pg.py
python3 -m unittest test/exams_analytics/interface/pg_db/test_best_marks_repository_pg.py
python3 -m unittest test/exams_analytics/interface/scan_import/test_example_data/test_example_data.py