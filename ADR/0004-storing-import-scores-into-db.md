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
    - I will limit the max marks you can insert, just to have it under control. I'll add some logs to be able to review if they get close
- I will use an array from postgres to store the import_ids
- I will do a test and make sure the test data makes sense

## Consequences
- When inserting in bulk:
    - There is a maximum number of parameters in SQL queries, so I had to chunk the inserts (to 1000 marks each) 
    - We use SQL (on conflict) to deal with the re-scan but the on-conflict cannot deal with the scans that we are inserting in the current bulk, so we had to filter them in python    -> We have the algorithm of the max in 2 places
    - In my local machine, inserting 10K (in bulks of 1K) took 200ms
- TO CONSIDER:
    - In the future we may have to tune the ids to include the origin or the scan (if not all the systems have the same id "space" for tests and students)
        - If this happens, we just need to add some pre-fix and reimport from the vault

