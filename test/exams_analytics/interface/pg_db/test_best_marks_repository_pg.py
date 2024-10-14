from datetime import datetime
import unittest
import time
import uu
import uuid
import numpy as np

from exams_analytics.application.marks.marks_dtos import AggregatedTestResultDTO, MarkDTO, MarkWithImportIdsDTO
from exams_analytics.interface.pg_db.best_marks_respository_pg import BestMarksRepositoryPG



class TestBestMarksRepositoryPG(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await BestMarksRepositoryPG.delete_all_rows_only_for_testing()
        

    async def asyncTearDown(self):
        await BestMarksRepositoryPG._instance.engine.dispose() #type: ignore
        pass

    def assert_mark_dto_equals(self, d1: MarkDTO, d2: MarkDTO):
        self.assertEqual(d1.student_id, d2.student_id, "The student_id is not the same")
        self.assertEqual(d1.test_id, d2.test_id, "The test_id is not the same")
        self.assertEqual(d1.num_questions, d2.num_questions, "The num_questions is not the same")
        self.assertEqual(d1.num_correct, d2.num_correct, "The num_correct is not the same")
    
    def assert_mark_with_import_equals(self, d1: MarkWithImportIdsDTO, d2: MarkWithImportIdsDTO):
        self.assert_mark_dto_equals(d1, d2)
        self.assertEqual(set(d1.import_ids), set(d2.import_ids), "The import_ids are not the same")

    async def test_insert_one(self):
        import_id = uuid.uuid1()
        m_dto = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=8)
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id([m_dto], import_id)
        dto_retrieved : MarkWithImportIdsDTO | None = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", "test1")
        self.assertIsNotNone(dto_retrieved, "The retrieved DTO is None")
        self.assert_mark_dto_equals(m_dto, dto_retrieved)    #type: ignore
        self.assertEqual(dto_retrieved.import_ids, [import_id], "The import_ids are not the same")  #type: ignore

    async def test_insert_one_and_then_change_score_in_db(self):
        #insert one
        m_dto = MarkDTO(student_id="1", test_id="test1", num_questions=9, num_correct=8)
        import_id_1 = uuid.uuid1()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id([m_dto], import_id_1)
        #now better mark
        m_dto_better = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=9)
        import_id_2 = uuid.uuid1()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id([m_dto_better], import_id_2)

        #retrieve and check is better mark
        dto_retrieved : MarkWithImportIdsDTO | None = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", "test1")
        self.assertIsNotNone(dto_retrieved, "The retrieved DTO is None")
        #before comparing we should add the the better the second import_id
        self.assert_mark_dto_equals(m_dto_better, dto_retrieved)    #type: ignore
        self.assertEqual(set(dto_retrieved.import_ids), {import_id_2, import_id_1}, "The import_ids are not the same")  #type: ignore

        #now let's keep the num_questions to 10 but the num_correct to 8, should not change the retrieved mark
        m_dto_worst = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=8)
        import_id_3 = uuid.uuid1()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id([m_dto_worst], import_id_3)
        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", "test1")
        self.assert_mark_dto_equals(m_dto_better, dto_retrieved)    #type: ignore
        self.assertEqual(set(dto_retrieved.import_ids), {import_id_2, import_id_1, import_id_3}, "The import_ids are not the same")  #type: ignore

        #now let's keep the same num_questions to 10 but correct to 10, should change the retrieved mark
        m_dto_new_better = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=10)
        import_id_4 = uuid.uuid1()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id([m_dto_new_better], import_id_4)
        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", "test1")
        self.assert_mark_dto_equals(m_dto_new_better, dto_retrieved)    #type: ignore
    
    async def test_insert_one_and_then_change_score_in_the_bulk_list(self):
        import_uuid = uuid.uuid1()
        m_9_8 = MarkDTO(student_id="1", test_id="test1", num_questions=9, num_correct=8)
        m_10_9 = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=9)
        m_10_8 = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=8)
        m_10_10 = MarkDTO(student_id="1", test_id="test1", num_questions=10, num_correct=10)
        bulk = [m_9_8, m_10_9, m_10_8, m_10_10]

        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(bulk, import_uuid)
        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", "test1")
        self.assertIsNotNone(dto_retrieved, "The retrieved DTO is None")
        self.assert_mark_dto_equals(m_10_10, dto_retrieved)    #type: ignore
    
    async def test_insert_various_of_different_test_and_student(self):
        #insert 10 marks
        marks = []
        test_0 = "test0"
        test_1 = "test1"
        import_uuid = uuid.uuid1()
        marks.append(MarkDTO(student_id="1", test_id=test_0, num_questions=1, num_correct=1))
        marks.append(MarkDTO(student_id="2", test_id=test_1, num_questions=2, num_correct=2))
        marks.append(MarkDTO(student_id="1", test_id=test_0, num_questions=3, num_correct=1))
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(marks, import_uuid)
        
        #check test_0
        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", test_0)
        self.assertEqual(dto_retrieved.num_questions,3, "The number of questions is not 3") #type: ignore
        self.assertEqual(dto_retrieved.num_correct,1, "The number of correct answers is not 1") #type: ignore

        #check test_1
        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("2", test_1)
        self.assertEqual(dto_retrieved.num_questions,2, "The number of questions is not 2") #type: ignore
        self.assertEqual(dto_retrieved.num_correct,2, "The number of correct answers is not 2") #type: ignore

        dto_retrieved = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test("1", test_1)
        self.assertIsNone(dto_retrieved, "The retrieved DTO is not None")
    
    async def test_10K_marks(self):
        marks = []
        import_uuid = uuid.uuid1()
        for i in range(10_000):
            marks.append(MarkDTO(student_id=str(i), test_id="test0", num_questions=i, num_correct=i))
        start = time.time()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(marks, import_uuid)
        print("10K marks took in ms:", int((time.time()-start)*1000))

        for m in marks:
            m.num_questions += 1

        start = time.time()
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(marks, uuid.uuid1())
        print("10K marks with all conflicts took in ms:", int((time.time()-start)*1000))
    
    async def test_aggregates(self):
        marks = []
        import_uuid = uuid.uuid1()
        NUM_QUESTIONS = 10
        NUM_STUDENTS_PER_MARK = 10
        MARK_1 = 5
        MARK_2 = 7
        MARK_3 = 10
        scores = []
        for i in range(NUM_STUDENTS_PER_MARK):
            marks.append(MarkDTO(student_id="A"+str(i), test_id="test0", num_questions=NUM_QUESTIONS, num_correct=MARK_1))
            scores.append(MARK_1 / NUM_QUESTIONS)
        
        for i in range(NUM_STUDENTS_PER_MARK):
            marks.append(MarkDTO(student_id="B"+str(i), test_id="test0", num_questions=NUM_QUESTIONS, num_correct=MARK_2))
            scores.append(MARK_2 / NUM_QUESTIONS)
        
        for i in range(NUM_STUDENTS_PER_MARK):
            marks.append(MarkDTO(student_id="C"+str(i), test_id="test0", num_questions=NUM_QUESTIONS, num_correct=MARK_3))
            scores.append(MARK_3 / NUM_QUESTIONS)

        test_2 = "TEST_DIFFERENT"
        marks.append(MarkDTO(student_id="A_DIFFERENT_ONE", test_id=test_2, num_questions=10, num_correct=10))
        
        await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(marks, import_uuid)
        result : AggregatedTestResultDTO | None = await BestMarksRepositoryPG.calculate_aggregated_test_result("test0")
        self.assertIsNotNone(result, "The result is None")
        
        # Calculating statistics
        mean = np.mean(scores)
        stddev = np.std(scores)
        minimum = np.min(scores)
        maximum = np.max(scores)
        p25 = np.percentile(scores, 25)
        p50 = np.percentile(scores, 50)
        p75 = np.percentile(scores, 75)
        count = len(scores)

        if result is not None:
            self.assertAlmostEqual(result.mean, mean, places=5)
            self.assertAlmostEqual(result.stddev, stddev, places=5)
            self.assertAlmostEqual(result.min, minimum, places=5)
            self.assertAlmostEqual(result.max, maximum, places=5)
            self.assertAlmostEqual(result.p25, p25, places=5)
            self.assertAlmostEqual(result.p50, p50, places=5)
            self.assertAlmostEqual(result.p75, p75, places=5)
            self.assertEqual(result.count, count, "The count is not the same")
        
        #now the other test
        result : AggregatedTestResultDTO | None = await BestMarksRepositoryPG.calculate_aggregated_test_result(test_2)
        self.assertIsNotNone(result, "The result is None")
        if result is not None:
            self.assertAlmostEqual(result.mean, 1, places=5)
            self.assertAlmostEqual(result.stddev, 0, places=5)
            self.assertAlmostEqual(result.min, 1, places=5)
            self.assertAlmostEqual(result.max, 1, places=5)
            self.assertAlmostEqual(result.p25, 1, places=5)
            self.assertAlmostEqual(result.p50, 1, places=5)
            self.assertAlmostEqual(result.p75, 1, places=5)
            self.assertEqual(result.count, 1, "The count is not the same")

    async def test_aggregates_100K(self):
        import_uuid = uuid.uuid1()
        num_marks = 0
        start = time.time()
        for j in range(10):
            marks = []
            for i in range(10_000):
                marks.append(MarkDTO(student_id=f"{j}-{i}", test_id="test0", num_questions=20, num_correct=i))
                num_marks += 1
            await BestMarksRepositoryPG.bulk_insert_keeping_max_values_when_same_student_and_test_id(marks, import_uuid)
            
        print(f"inserting {num_marks} marks took in ms:", int((time.time()-start)*1000))

        start = time.time()
        result : AggregatedTestResultDTO | None = await BestMarksRepositoryPG.calculate_aggregated_test_result("test0")
        print(f"calculating {result.count} marks took in ms:", int((time.time()-start)*1000))   #type: ignore
        

print("Test repo marks")
if __name__ == '__main__':
    unittest.main()

