

# Running the project
TBD


# Approach
Most of my reasoning is in ADR-2, but here is a summary:
- The future product is about generating analytics of scores, it is not about treating scan particularities (or any of the potentially hundreds of test systems out there).
- IMPORT_VAULT: We don't know the specs of the format of the data + we are not using all the fields + we don't want to ask for a full re-scan if we have a bug. So we are going to store the raw data in a table. This could also give us traceability.
- POSTGRESQL: It's a versatile DB. I don't have much time for the project and I know how to use it. It can aggregate 1-2 millions of rows in under one second. So it should be good to do all calculations.
- PYTHON: Language that I know and that we can find many developers in the future to support it.
- ASYNCIO + QUART + HYPERCORN: Allows the project to scale using tasks (not that we need now, but, again, I'm used to and I think it's more future proof than doing it with threads)
- Task manager: https://github.com/users/lligallo/projects/6/views/1

# Comments for the Boss
- student_number(s) -2319 and 2353- that have different names with the same id


