import unittest
from unittest.mock import patch, AsyncMock
from quart import Quart
import csv
from sqlalchemy.ext.asyncio import AsyncConnection
from exams_analytics.application.marks.marks_dtos import MarkDTO
from exams_analytics.interface.pg_db.best_marks_respository_pg import BestMarksRepositoryPG
from exams_analytics.interface.pg_db.raw_import_repository_pg import RawImportRepositoryPG
from exams_analytics.interface.scan_import.http_rest_facade import http_scan_import_quart

class TestExampleData(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await RawImportRepositoryPG.delete_all_rows_only_for_testing()
        await BestMarksRepositoryPG.delete_all_rows_only_for_testing()
        self.client = http_scan_import_quart.test_client()

    async def asyncTearDown(self):
        await RawImportRepositoryPG._instance.engine.dispose() #type: ignore        

    
    async def test_index_database_ready(self):    
        response = await self.client.get('/check')

        # Check that the response is correct
        self.assertEqual(response.status_code, 200)
        text = await response.get_data(as_text=True)
        self.assertEqual(text, "Hello, I'm ready and the database too!")
    
    async def test_post_xml_example_data(self):
        # Read the XML file from the disk
        with open('/workspace/test/exams_analytics/interface/scan_import/test_example_data/example_data.xml', 'r') as xml_file:
            xml_content = xml_file.read()

        # Make a POST request with the XML content as the body
        headers = {'Content-Type': 'text/xml+markr'}
        response = await self.client.post('/import', data=xml_content, headers=headers)

        # Check that the response is correct (adapt this based on your endpoint's expected behavior)
        self.assertEqual(response.status_code, 200)
        text = await response.get_data(as_text=True)

        #now let's check that the data in the database matches the calculated data with jupyter
        #we will just check each one of the studnets in the csv and see if their best mark is the same as the one in the csv

        csv_file_path = "/workspace/test/exams_analytics/interface/scan_import/calculating_output_for_example_data/student_marks.csv"

        num_marks_that_should_be_in_db = 0

        # Open the CSV file and read it line by line
        with open(csv_file_path, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            
            # If the CSV file has a header, you can skip it using next()
            header = next(csv_reader)
            print(f"Header: {header}")
            
            # Read each row of the CSV file
            for row in csv_reader:
                # row is a list where each element corresponds to a column in the CSV
                student_number = row[0]
                test_id = row[1]
                available_marks = row[2]
                obtained_marks = row[3]
                
                #let's get in from the database
                m_db : MarkDTO | None = await BestMarksRepositoryPG.get_maximum_mark_by_student_and_test(student_number, test_id)
                self.assertIsNotNone(m_db, f"Student Number: {student_number}, Test ID: {test_id} not found in the database")
                #print(f"Student Number: {student_number}, Test ID: {test_id}, Available Marks: {available_marks}, Obtained Marks: {obtained_marks}")
                self.assertEqual(m_db.num_questions, int(available_marks), f"Student Number: {student_number}, Test ID: {test_id} has different available marks")   #type: ignore
                self.assertEqual(m_db.num_correct, int(obtained_marks), f"Student Number: {student_number}, Test ID: {test_id} has different obtained marks")  #type: ignore
                
                num_marks_that_should_be_in_db += 1
        
        #let's count the marks in the database
        num_marks_in_db = await BestMarksRepositoryPG.count_all_rows()
        self.assertEqual(num_marks_in_db, num_marks_that_should_be_in_db, "The number of marks in the database is different than the expected number of marks")
                

print("Test http facade")
if __name__ == '__main__':
    unittest.main()
