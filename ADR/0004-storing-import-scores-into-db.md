# 4. storing import scores into DB

Date: 2024-10-13

## Status

Accepted

## Context

- We are receiving the XML data from the scanners. 
- We only need the available and obtained. Not the date, not the marks, nothing.
    - We don't have to worry if we need other data in the future, it is in the import vault
- In case of repeated score for a student and test, we must keep the max(available) and if it is the same, we should keel max(obtained)
    - We will do this in the PG database. We want to have just one query to insert (or the less possible)

## Decision

- I will parse the xml and fill a dto. The dto should contain the import_id for traceability.
- I will create a service to manage the marks (it will just call the persistence repository now)
- I will create the persistence repository that manages the bulk insert while keeping the max score.

## Consequences


