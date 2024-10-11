# 2. initial planning

Date: 2024-10-12

## Status

Accepted

## Context

Exercise: https://gist.github.com/nick96/fda49ece0de8e64f58d45b03dda9b0c6

Here a not-very-structured chain of thoughts:

- This is a prototype of a system that if it makes $$$ would be 'cause it ingests test scores data from multiple systems and generates visualizations. 
	- It has to have a solid basement, since the prototype will be evolving 'till it's a product
	- Should be able to deal with different origin of data.
		- We don't know exactly the format
		- There is personal information, but it's not used for this first initial
		- We don't want to loose any data 'cause of a bug or 'cause now we want to, for example get the answers of each question.
		- DECISIONS: Have a RAW_IMPORT_VAULT
			- I will store raw data as it arrive (even if I find it that is not well formatted). 
				- This will allow us:
					- To re-process if needed (bugs or new features)
					- Traceability (if each import have an id we can attach it to any data internally that we process to have traceability)
					- More examples on the input
				- Ideally:
					- We should store the result of the import (was it successful, the moment it was done -so we can have traceability of the code that did it-)
					- It should be encrypted or protected at the database, so if there is personal information we can limit the access to it


PARSING, STORING AND PROCESSING THE DATA
- Our system value prop is to aggregate data, so the less we are related to the scan system the better. Thanks to the IMPORT VAULT we will be able to reprocess that   data, and since we have not much time, I think we can focus on what has to be demoed + have a good basement for the architecture.
	- This means that we really forget about the answers itself
	- This means that we forget about the student_number(s) -2319 and 2353- that have different names with the same id
	- This means that we can process the re-scanned exams, getting the maximum score the boss said and if later on another strategy is best, we can reprocess


ABOUT THE DATA I RECEIVED:
- Student number:
	- There are student numbers that have 2 different names: 2319 and 2353
	- They say it's a number and it almost seems a number, there is one that is 002299, so I would be better of treating as a string
- I'm going to parse the xml and just get the data I need (as my boss says). If later on we want other fields we can reprocess it from the vault.


STORING THE DATA
- I will use postgresql, since I need to solve this first project quick (I have experience) and I don't see a reason on why use a more specialized DB.
- I want to store the scores of each test in a table. I want to be affected the least possible about the particularities of the scanning system. 
	- DOUBT: 
		- should I store each of the scans as if they are different scores of the same exam? But I think it's not, if a student does again the same test in the future this will be another test_id. So the fact that is re-scanned it's not relevant for the statistics. 
	- DECISIONS:
		- Use string for the test_id
		- Use string for student_id (yes, I'm going to store it as student_id not student_number)
		- I'm going to store available_points and obtained_points (one could argue that could be different types of tests and grading system)	-> then at the import there will be a "policy" that is keeping the ones that has the most available points and then the most obtained points
		- I'm going to store the origin of the data, I will add to each row the id of the raw data in the IMPORT VAULT. I think traceability would be useful for both explain and in case of reprocessing
		- So the table will be called: student_test_results
			- primary key: (student_id: str, test_id: str)
			- available_points
			- obtained_points
			- origins_import_vault: array of ids from the import vault
			- date_of_test: -> this will be the scan date
			- updated_on -> this will be an automatic
			
- We will use batch inserts to insert all the data in one query, if there is a conflict (we already received the result in the scan) then we will use ON CLONFLICT to implement the policy of getting the "best score"

AGGREGATING THE DATA
- With the proper indexes, postgresql should be able to calculate the percentiles, max and averages fast enough by now. In this article (https://www.citusdata.com/blog/2017/09/29/what-performance-can-you-expect-from-postgres/) they say postgres can do 1-2 million points aggregated in less than 1 second. If in the future we need realtime we can do materialized views and update them every 5 minutes or implement a dedicated table that we only update the aggregations when new data of a test_id arrives.


ARCHITECTURE
- Postgres: I already decided to use posgresql. I used it recently, its very versatile and I see no need for specialized DB.
- Python: No the fastest language, but good enough. We will find plenty of developers with experience if we want to evolve the product.
- Asyncio: In my last projects I used asyncio's model so the whole system runs lighter. It can be argued that with just threads we should be good now, but I think starting with asyncio built  in won't take that extra effort and will provide us with a high concurrent system.
- Quart and Hypercorn: I will use those for serving the HTTP calls. I think there is a module that generates the documentation for the API.
- Code organization: I will base it on Hexagonal (ports and adapters), I like how we can still have our domain but not tied to the data model.
- Documentation: I will keep the log of my decisions in ADR and I think there is a package for QUART that generates the API documentation (but I won't worry in the first implementaiton, there is going to be just one entry point). + README at high level as specified.
- ORM: Since we are going to use PG for the aggregations, I prefer to use directly SQL. I will use SQLAlchemy CORE to protect me against SQL injection, have an async driver and Alembic to do the migrations.
- Deployment: I will use docker-compose to run it locally and tune it with the operations people later on to deploy
- Development tooling: I will use vscode with devcontainers. So if more people join the project they can develop in no time. If later on they want to use other IDEs, they will manage.
- Proj management: Since I will use github I'm also going to use the projects part. So I can create my task in a Trello style view, and then turn those tasks into issues->branches.


TASKS:

MUST
-[] Create the basic setup of the project
	- IDE devcontainers with python and PG running
	- Python project following hexagonal with a simple REST call that checks that has connection to the PG
	- Script to run the python and the testing from within VScode
	- docker-compose that we can do "up" and have it running
-[] /import stores that data in the IMPORT VAULT (no processing)
-[] /import parses the data and stores in the student_test_results DB
-[] /aggregation provides the data aggregated for the views

COULD
-[] IMPORT VAULT: Make it secure, like encrypted or something
-[] IMPORT VAULT: Allow to provide the result (later on)


## Decision

- I will create the tasks in the proj manager (only the MUST)

## Consequences


