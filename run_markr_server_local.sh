#!/bin/bash

set -e

# Automatically export variables
set -a
source .env
# Stop automatically exporting variables
set +a

./run_markr_server.sh