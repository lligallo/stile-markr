# 3. import vault

Date: 2024-10-12

## Status

Accepted

## Context

We are receiving data from the scans in /import. We want to store the data as it arrives since:
- We only have examples, not a full specification -> We don't want to loose data due to an error
- We are not going to use all the data by (not using each of the answers for example) so we want to be able to reprocess in the future
- We want to have traceability

## Decision
- We will create a table to hold this raw data
- We will insert the raw data as soon as arrives at /import
- We will use alembic to manage the migrations
- We are going to check if a migration has to be done every time the server is started

## Consequences


