import logging
from quart import Quart, request
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text as sql_text

from exams_analytics.interface.pg_db.database_engine import DatabaseEngine

http_scan_import_quart = Quart(__name__)

logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

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
