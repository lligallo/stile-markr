#!/bin/bash

# Exit on error
set -e

echo "Upgrading the database to the latest version..."
alembic upgrade head
echo "Database upgraded successfully."

echo "Starting markr server..."
cd src
python3 -m exams_analytics.interface