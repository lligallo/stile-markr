import logging
from math import e
from typing import List
from uuid import UUID
from quart import Quart, request
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text as sql_text
import xml.etree.ElementTree as ET

from exams_analytics.application.import_vault.import_vault_service import ImportVaultService, ImportOrigin
from exams_analytics.application.marks.marks_dtos import MarkDTO
from exams_analytics.application.marks.marks_service import MarksService
from exams_analytics.interface.pg_db.database_engine import DatabaseEngine

http_scan_import_quart = Quart(__name__)

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)
logger.warning("THERE IS NO SSL OR AUTHENTICATION YET")

@http_scan_import_quart.after_serving
async def shutdown():
    print("Cleanup tasks here if needed")
    raise KeyboardInterrupt

@http_scan_import_quart.route('/check')
async def index():
    #check there is connection with the database
    print("Trying to connect to the database")
    try:
        engine = DatabaseEngine.get_engine()
        async with engine.begin() as conn: # type: ignore
            conn: AsyncConnection
            result = await conn.execute(sql_text("SELECT 1"))
            row = result.fetchone()
            if row[0] == 1:
                return "Hello, I'm ready and the database too!", 200
            else:
                return "Could not connect to the database", 500
    except Exception as e:
        print(f"{e}")
        return f"There was a problem connecting with the database: {str(e)}", 500
    

def __parse_xml_to_list_marks(xml_str: str, import_id : UUID) -> list[MarkDTO]:
    """
    Parses the XML string and returns a list of MarkDTO objects
    """
    root = ET.fromstring(xml_str)
    mark_dtos = []
    try:
        for mcq_result in root.findall('mcq-test-result'):
            student_number = int(mcq_result.find('student-number').text)    #type: ignore
            test_id = mcq_result.find('test-id').text                       #type: ignore
            if not test_id:
                raise Exception("Test ID is missing")
            available = int(mcq_result.find('summary-marks').get('available'))   #type: ignore
            obtained = int(mcq_result.find('summary-marks').get('obtained'))     #type: ignore
            mark_dtos.append(MarkDTO(student_id=student_number, test_id=test_id, num_questions=available, num_correct=obtained, import_ids=[import_id]))
    except ET.ParseError as e:
        raise Exception(f"XML Parsing Error when trying to parse the mark in position {len(mark_dtos)+1}: {str(e)}. Line {e.position[0]}, Column {e.position[1]}. Code {e.code}. Msg: {e.msg}")
    return mark_dtos

@http_scan_import_quart.route('/import', methods=['POST'])
async def import_marks():
    """
    Receives a POST request with the XML data from the scanner system
        - Stores the raw data into the import vault
        - Parses and inserts the marks
    """
    logger.warning("THERE IS NO SSL OR AUTHENTICATION YET")
    if request.content_type != "text/xml+markr":
        logger.info(f"Invalid content type. Should be text/xml+markr. {request.content_type}")
        return "Invalid content type. Should be text/xml+markr. Unsupported Media Type", 415
    try:
        data = await request.data  # Get the raw XML data
        logger.debug(f"Data received: {data}")    
        xml_str = data.decode('utf-8')

        import_id : UUID = await ImportVaultService.import_raw_data(ImportOrigin.SCANNER_SYSTEM, xml_str)

        try:
            mark_dtos : List[MarkDTO] = __parse_xml_to_list_marks(xml_str, import_id)
        except Exception as e:
            return f"Error parsing the XML: {str(e)}", 400
        
        logger.debug(f"Mark DTOs: {mark_dtos}")
        
        if len(mark_dtos) == 0:
            return "No marks found in the XML. BAD REQUEST", 400

        await MarksService.insert_marks(mark_dtos)

        return f"Data parsed and incorporated into DB, import id is {import_id}", 200

    except Exception as e:
        logger.info(f"Error importing data: {str(e)}")
        return "Error importing data", 500
    
