import uuid
import unittest
from exams_analytics.interface.pg_db.raw_import_repository_pg import RawImportRepositoryPG
from datetime import datetime, timezone, timedelta

class TestRawImportRepositoryPG(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await RawImportRepositoryPG.delete_all_rows_only_for_testing()

    async def asyncTearDown(self):
        await RawImportRepositoryPG._instance.engine.dispose() #type: ignore
    
    async def test_insert_raw_import(self):
        import_id = uuid.uuid1()
        origin = "test"
        import_data = "test data"
        utc_now = datetime.now(timezone.utc)        #this is going to be at the database
        await RawImportRepositoryPG.insert_raw_import(import_id, origin, import_data)

        result = await RawImportRepositoryPG.get_raw_import(import_id)

        self.assertEqual(result.import_id, import_id)   #type: ignore
        self.assertEqual(result.origin, origin)            #type: ignore
        self.assertEqual(result.import_data, import_data)   #type: ignore
        time_difference = abs(result.created_at - utc_now)  #type: ignore
        self.assertTrue(time_difference < timedelta(seconds=1)) #type: ignore
    
    async def test_repeated_id(self):
        import_id = uuid.uuid1()
        origin = "test"
        import_data = "test data"
        await RawImportRepositoryPG.insert_raw_import(import_id, origin, import_data)

        with self.assertRaises(Exception):
            await RawImportRepositoryPG.insert_raw_import(import_id, origin, import_data)
    
    async def test_inexistent_id(self):
        import_id = uuid.uuid1()
        result = await RawImportRepositoryPG.get_raw_import(import_id)
        self.assertIsNone(result)
