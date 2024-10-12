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

python3 -m unittest test/exams_analytics/empty_unit_test.py