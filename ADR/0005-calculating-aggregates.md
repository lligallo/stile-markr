# 5. calculating aggregates

Date: 2024-10-14

## Status

Accepted

## Context

We need to calculates aggregates for a particular test ondemand. 
We have to calculate:
- mean
- stddev
- min
- max
- p25
- p50
- p75
- count

## Decision

- I will calculate it in SQL
- I will use the STDDEV_POP since we are considering we have all the population of people that took the exam (I'm not entirely sure if that is the correct one...)
- I will treat the scores internally from 0 to 1, not 100 or 10.

## Consequences
- I added an index to quickly access test_id


