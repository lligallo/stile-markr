import unittest
import aiohttp

from exams_analytics.interface.pg_db.raw_import_repository_pg import RawImportRepositoryPG

class TestHttpRestFacade(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        pass

    async def asyncTearDown(self):
        pass
    
    async def test_content_type_correct(self):
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8082/import", headers={"Content-Type": "text/xml"}) as response:
                response_text = await response.text()
                print("Response:", response_text)
                self.assertEqual(response.status, 415)
    
    async def test_incorrect_xml(self):
        xml_data = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><root><element>Value</elementI></root>"

        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8082/import", data=xml_data, headers={"Content-Type": "text/xml+markr"}) as response:
                response_text = await response.text()
                print("Response:", response_text)
                self.assertEqual(response.status, 400)  # Check if the response is successful
    
    async def test_do_a_post(self):
        xml_data = """<?xml version="1.0" encoding="UTF-8" ?>
<mcq-test-results>
	<mcq-test-result scanned-on="2017-12-04T12:12:10+11:00">
		<first-name>KJ</first-name>
		<last-name>Alysander</last-name>
		<student-number>002299</student-number>
		<test-id>9863</test-id>
		<answer question="17" marks-available="1" marks-awarded="0">B</answer>
		<answer question="18" marks-available="1" marks-awarded="1">A</answer>
		<answer question="19" marks-available="1" marks-awarded="0">B</answer>
		<summary-marks available="20" obtained="13" />
	</mcq-test-result>
</mcq-test-results>"""

        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:8082/import", data=xml_data, headers={"Content-Type": "text/xml+markr"}) as response:
                response_text = await response.text()
                print("Response:", response_text)
                self.assertEqual(response.status, 200)  # Check if the response is successful
                

print("Test http facade")
if __name__ == '__main__':
    unittest.main()
