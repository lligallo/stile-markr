NOTE: This project took me more than 3 hours. I thought it was a good opportunity to explore various things I had in mind (like not using any start boilerplate) and I hope it provides better opportunity to talk.

# Running the project
- required: docker and docker-compose installed
- copy .env_template to .env
- docker-compose up         <- PENDING TO CONFIGURE THE DB with proper security
- the http server is mapped in port 8085

# Approach
Most of my reasoning is in ADR-2, but here is a summary:
- The future product is about generating analytics of scores, it is not about treating scan particularities (or any of the potentially hundreds of test systems out there).
- It is also said that this will be the base of the product, so it's not only a demo.

My decisions:
- Have an "Import Vault service"  so any data that we receive in the API is first stored. This provides traceability (all the internal data has an associated import_id), captures different examples of data -since we don't have specifications- and in case of bugs or new features allows us to reprocess the input. 
- Have a "Marks Service" that coordinates both the ingest and the parsed data within the application. More on the structure of the code in the section below.
- We store all the data in Postgresql (both the import vault and the scores). It's a versatile database that can both store and do the calculations (It can aggregate 1-2 millions of rows in less than 1 second).
    - I decided to create 2 tables. One for the Import Vault, and one for the marks. I haven't created a Test table, I would argue it is best to do in the future when we know what other types of tests we want to support.
- I decided to use python, asyncio, quart and hypercorn. I've been using them in my last two projects and they are fast enough and will allow the application to grow without any big limitation. Python is also great since there are plenty of experienced developers. For migrations I used Alembic, for accessing the database I used SQLAlchemy CORE, not the ORM. I think having access to directly SQL is best for this application.

## Structure of the code (/src)
I followed the Hexagonal (or ports and adapters) architecture.
Inside src:
- Application: this contains the logic of the application. There is not much yet, but it's expected to grow. The Application is not related to any facade (http or anything).
    - import_vault: contains the 'service' that inserts the data into the vault.
    - marks: contains the 'service' that manages the marks (imports and aggregates)
- Domain: There is no domain.
- Interfaces: this contains the inputs and outputs of the system, they interface them with the application layer.
    - pg_db: All the code related to the database, including the schema and migrations.
    - scan_import: Code related to importing the marks (http).
    - results: Code related to results (http).

This structure allows us to separate the logic of the application from the data interface and the database.

## File structure
- .devcontainer: definition of the dev environment for vscode
- .vscode: shared settings for the team in vscode
- ADR: Crud decisions taken during development
- src/exams_analytics: Source code following hexagonal architecture
- test: tests

# Comments for the Boss
- student_number(s) -2319 and 2353- that have different names with the same id


# Development
- I used .vscode. The .devcontainer is configured so the database is up and you are developing within the machine defined at .devcontainers/Dockerfile.dev
- ./run_markr_server_local.sh -> Executes the http server with the parameters of .env file
- ./run_markr_server.sh -> Executes the http server without loading any env variables
- ./run_python_unit_tests.sh -> Executes some tests
- ./run_python_http_endpoints_tests.sh -> Executes tests by calling http endpoints (full integration)

## Alembic 
- Generate a migration: set -a; source .env; set +a; alembic revision --autogenerate -m "DESCRIPTION"

# TODO:
- Better devOps the deployment (I'm sure there are better ways to manage the certificates, even that are only used for local development) 
- Add documentation for the API
- Add configuration to the logging system (now is set to the Basic one)