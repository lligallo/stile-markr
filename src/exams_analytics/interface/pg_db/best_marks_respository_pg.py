

from typing import Dict, List
import os
from uuid import UUID
import logging
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text as sql_text

from exams_analytics.application.marks.best_marks_repository_abstract import BestMarksRepositoryAbstract
from exams_analytics.application.marks.marks_dtos import AggregatedTestResultDTO, MarkDTO, MarkWithImportIdsDTO
from exams_analytics.interface.pg_db.database_engine import DatabaseEngine, log_db_operation

logger = logging.getLogger(__name__)

class BestMarksRepositoryPG(BestMarksRepositoryAbstract):
    """
    This repository stores the maximum marks per each student and test.
    It allows inserting new marks in bulk.
    See ADR-03 for implementation decisions
    """
    _instance = None
    MAX_MARKS_TO_INSERT = 10_000
    SIZE_MARK_CHUNK_WHEN_BULK_INSERT = 1000

    def __init__(self):
        self.engine = DatabaseEngine.get_engine()

    @classmethod
    async def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    

    @classmethod
    async def __bulk_insert_marks_chunk(cls, conn: AsyncConnection, marks_chunk: List[MarkDTO], import_vault_id: UUID) -> None:
        """
        Inserts a chunk of marks into the database.
            - If a mark already exists for a student and test, it will keep the maximum values.
            - We use the flat_parameters to avoid SQL injection.

        NOTE: If the "algorithm" to keep the maximum values changes needs to be changed you have to change it here and in the method __filter_repeated_marks_keeping_maximum
        """

        sql_query = """
            INSERT INTO best_marks_of_student_per_test (student_id, test_id, num_correct, import_ids)
            VALUES {}
            ON CONFLICT (student_id, test_id)
            DO UPDATE SET
                num_correct = GREATEST(excluded.num_correct, best_marks_of_student_per_test.num_correct),
                import_ids = ARRAY(
                    SELECT DISTINCT unnest(best_marks_of_student_per_test.import_ids || excluded.import_ids)
                )
        """

        # We will be happier if we could just pass the list of marks as a parameter to the query, but we can't. We have to specify the placeholders in the query.
        #IMPORTANT: We do it this way 'cause then we can use the execute it at be protected from SQL injection.
        placeholders = []
        parameters = []

        index = 0
        for mark in marks_chunk:
            placeholders.append(f"(:student_id_{index}, :test_id_{index}, :num_correct_{index}, :import_ids_{index})")
            parameters.extend([
                {"student_id_" + str(index): mark.student_id},
                {"test_id_" + str(index): mark.test_id},
                {"num_correct_" + str(index): mark.num_correct},
                #now we add the import_id as an array
                {"import_ids_" + str(index): [import_vault_id]}
            ])
            index += 1

        # Join the placeholders into a single string
        values_sql = ", ".join(placeholders)

        # Combine the base query with the values string
        full_query = sql_query.format(values_sql)

        # Flatten parameters into one dictionary
        flat_parameters = {k: v for d in parameters for k, v in d.items()}

        logger.debug("Executing SQL Query: %s with Parameters: %s", full_query, flat_parameters)

        # Execute the single query with all the parameters
        await conn.execute(sql_text(full_query), flat_parameters)

    @classmethod
    def __filter_repeated_marks_keeping_maximum(cls, marks: List[MarkDTO]) -> List[MarkDTO]:
        """
            Filters the repeated marks in the list.
            NOTE: If the "algorithm" to keep the maximum values changes needs to be changed you have to change it here and in the method __bulk_insert_marks_chunk
        """
        dict_best_marks : Dict[str,MarkDTO] = {}
        for mark in marks:
            key = f"{mark.student_id}_{mark.test_id}"
            if key in dict_best_marks:
                if mark.num_questions > dict_best_marks[key].num_questions:
                    dict_best_marks[key] = mark
                elif mark.num_questions == dict_best_marks[key].num_questions:
                    if mark.num_correct > dict_best_marks[key].num_correct:
                        dict_best_marks[key] = mark
            else:
                dict_best_marks[key] = mark
        return list(dict_best_marks.values())

    @classmethod
    async def _bulk_insert_marks(cls, conn: AsyncConnection, marks: List[MarkDTO], import_vault_id : UUID) -> None:
        if len(marks) == 0:
            return
        
        # When inserting a new mark, we will have to check if it's better than the previous one.
        # we have to always take the maximum of num_questions and num_correct, independently

        # We can rely on sql ON CONFLICT to update the values that are in the database and get the maximum of the values.
        
        # But we have to make sure that in our insert statement are no repeated values (2 rows about to be inserted cannot be on conflict with each other)
        # We could solve that with a more complicated query (like creating a temporary table) but for clarity we will do it in python.
        # If in the future this is a common case, we can modify it and rely into a more complex query.
        
        best_marks = cls.__filter_repeated_marks_keeping_maximum(marks)

        #time to insert the marks
        #But...There is a limit on the number of parameters that can be passed in a query, so we will break the list of marks into chunks of 1000
        for i in range(0, len(best_marks), cls.SIZE_MARK_CHUNK_WHEN_BULK_INSERT):
            logger.debug("Inserting chunk of marks from %d to %d", i, i+cls.SIZE_MARK_CHUNK_WHEN_BULK_INSERT)
            marks_chunk = best_marks[i:i+cls.SIZE_MARK_CHUNK_WHEN_BULK_INSERT]
            await cls.__bulk_insert_marks_chunk(conn, marks_chunk, import_vault_id)
    
    @classmethod
    def _generate_list_tuple_test_max_questions(cls, marks: List[MarkDTO]) -> List[tuple[str,int]]:
        """
            Generates a list of tuples with the test_id and the maximum number of questions for that test.
        """
        dict_test_max_questions : Dict[str,int] = {}
        for mark in marks:
            if mark.test_id in dict_test_max_questions:
                dict_test_max_questions[mark.test_id] = max(dict_test_max_questions[mark.test_id], mark.num_questions)
            else:
                dict_test_max_questions[mark.test_id] = mark.num_questions
        return [(test_id, max_questions) for test_id, max_questions in dict_test_max_questions.items()]
    
    @classmethod
    async def _update_question_tests(cls, conn: AsyncConnection, list_tuple_test_max_questions: List[tuple[str,int]], import_vault_id: UUID) -> None:
        """
            Updates the table tests with the maximum number of questions for each test.
            Not in batch because we don't expect to have many tests.
        """

        sql_query = """
            INSERT INTO tests (test_id, num_questions, import_ids)
            VALUES (:test_id, :num_questions, :import_ids)
            ON CONFLICT (test_id)
                DO UPDATE
                    SET 
                        num_questions = GREATEST(tests.num_questions, EXCLUDED.num_questions),
                        import_ids = ARRAY(SELECT DISTINCT unnest(tests.import_ids || EXCLUDED.import_ids));                            
            """
        
        for test_id, max_questions in list_tuple_test_max_questions:
            parameters = {
                "test_id": test_id,
                "num_questions": max_questions,
                "import_ids": [import_vault_id]
            }
            logger.debug("Executing SQL Query: %s with Parameters: %s", sql_query, parameters)
            await conn.execute(sql_text(sql_query), parameters)
    
    @classmethod
    @log_db_operation(threshold_ms=200)
    async def bulk_insert_keeping_max_values_when_same_student_and_test_id(cls, marks: List[MarkDTO], import_vault_id : UUID) -> None:
        if len(marks) > cls.MAX_MARKS_TO_INSERT:
            logger.warning(f"Someone requested to insert too many marks. The maximum is {cls.MAX_MARKS_TO_INSERT}. This value was chosen as as resonable limit. If you see this message reconsider this limit.")
            raise ValueError(f"Too many marks to insert. The maximum is {cls.MAX_MARKS_TO_INSERT}")
        if len(marks) > cls.MAX_MARKS_TO_INSERT // 2:
            logger.warning(f"Someone requested to insert a lot of marks {cls.MAX_MARKS_TO_INSERT}. Although it is within the limit {cls.MAX_MARKS_TO_INSERT}, we may want to review this limit.")
        
        list_tuple_test_max_questions = cls._generate_list_tuple_test_max_questions(marks)

        instance = await cls._get_instance()
        async with instance.engine.begin() as conn: # type: ignore
            conn: AsyncConnection
            await cls._update_question_tests(conn, list_tuple_test_max_questions, import_vault_id)
            await cls._bulk_insert_marks(conn, marks, import_vault_id)
    

    @classmethod
    async def __get_maximum_mark_by_student_and_test(cls, conn: AsyncConnection, student_id: str, test_id: str) -> None | MarkWithImportIdsDTO:
        query = """
            SELECT bm.student_id, bm.test_id, t.num_questions, bm.num_correct, bm.import_ids
            FROM best_marks_of_student_per_test bm
            JOIN tests t ON bm.test_id = t.test_id
            WHERE bm.student_id = :student_id AND bm.test_id = :test_id;
            """
        values = {
            "student_id": student_id,
            "test_id": test_id
        }
        result = await conn.execute(sql_text(query), values)
        row = result.fetchone()
        if row is None:
            return None
        else:
            return MarkWithImportIdsDTO(student_id = row[0], test_id = row[1], num_questions = row[2], num_correct = row[3], import_ids = row[4])

    @classmethod
    async def get_maximum_mark_by_student_and_test(cls, student_id: str, test_id: str) -> None | MarkWithImportIdsDTO:
        instance = await cls._get_instance()
        async with instance.engine.begin() as conn: # type: ignore
            conn: AsyncConnection
            return await cls.__get_maximum_mark_by_student_and_test(conn, student_id, test_id)

    @classmethod
    async def __calculate_aggregated_test_result(cls, conn: AsyncConnection, test_id: str) -> AggregatedTestResultDTO | None:
        """
            Using STDDEV_POP instead of STDDEV because we are using the whole population.
            It's implemented in 2 queries for clarity (could do a join but...).
        """

        query = """
            SELECT num_questions FROM tests WHERE test_id = :test_id;
        """
        result = await conn.execute(sql_text(query), {'test_id': test_id})
        row = result.fetchone()
        if row is None:
            return None

        num_questions = int(row[0])

        if num_questions == 0:
            return None

        query= """
            SELECT 
                AVG(num_correct::float / :num_questions ::float) AS mean,
                STDDEV_POP(num_correct::float / :num_questions ::float) AS stddev,
                MIN(num_correct::float / :num_questions ::float) AS min,
                MAX(num_correct::float / :num_questions ::float) AS max,
                PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY num_correct::float / :num_questions ::float) AS p25,
                PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY num_correct::float / :num_questions ::float) AS p50,
                PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY num_correct::float / :num_questions ::float) AS p75,
                COUNT(*) AS count
            FROM 
                best_marks_of_student_per_test
            WHERE
                test_id = :test_id;
            """ 
        
        result = await conn.execute(sql_text(query), {'test_id': test_id, 'num_questions': num_questions})
        row = result.fetchone()
        if row is None:
            return None
        else:
            #check that none of the values are None
            for i in range(8):
                if row[i] is None:
                    return None
            
            if row[7] == 0:
                return None
            
            return AggregatedTestResultDTO(
                test_id = test_id,
                mean = row[0],
                stddev = row[1],
                min = row[2],
                max = row[3],
                p25 = row[4],
                p50 = row[5],
                p75 = row[6],
                count = row[7]
            )

    @classmethod
    @log_db_operation(threshold_ms=500)
    async def calculate_aggregated_test_result(cls, test_id: str) -> AggregatedTestResultDTO | None:
        instance = await cls._get_instance()
        async with instance.engine.connect() as conn: # type: ignore
            conn: AsyncConnection
            return await cls.__calculate_aggregated_test_result(conn, test_id)
    
    
    @classmethod
    async def delete_all_rows_only_for_testing(cls):
        #only executes it if it's a test on a local dev machine
        if (os.getenv('DEPLOYMENT')=='PRODUCTION' or os.getenv('DEPLOYMENT')=='STAGING'):
            raise ValueError("This method should only be used for testing")
        else:
            instance = await cls._get_instance()
            query_delete = """
                    DELETE FROM best_marks_of_student_per_test;
                    """
            query_delete_tests = """
                    DELETE FROM tests;
                    """
            async with instance.engine.begin() as conn:  # type: ignore
                conn: AsyncConnection
                await conn.execute(sql_text(query_delete))
                await conn.execute(sql_text(query_delete_tests))

    @classmethod
    async def count_all_rows(cls) -> int:
        instance = await cls._get_instance()
        async with instance.engine.connect() as conn: # type: ignore
            conn: AsyncConnection
            query = """
                SELECT COUNT(*) FROM best_marks_of_student_per_test
            """
            result = await conn.execute(sql_text(query))
            row = result.fetchone()
            return row[0]