
import logging
from uuid import UUID

from exams_analytics.application.import_vault.import_dtos import RawImportDTO
from exams_analytics.application.import_vault.raw_import_repository_abstract import RawImportRepositoryAbstract
from exams_analytics.interface.pg_db.database_engine import DatabaseEngine

from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy import text as sql_text
import os

class RawImportRepositoryPG(RawImportRepositoryAbstract):

    _instance = None

    def __init__(self):
        self.engine = DatabaseEngine.get_engine()

    @classmethod
    async def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    async def insert_raw_import(cls, import_id: UUID, origin: str, import_data: str) -> None:
        instance = await cls._get_instance()
        async with instance.engine.begin() as conn: # type: ignore
            conn: AsyncConnection
            sql_query = """
                INSERT INTO import_vault_raw_imports (import_id, origin, import_data)
                VALUES (:import_id, :origin, :import_data)
            """

            values = {
                "import_id": import_id,
                "origin": origin,
                "import_data": import_data
            }
            await conn.execute(sql_text(sql_query), values)

    
    @classmethod
    async def get_raw_import(cls, import_id: UUID) -> RawImportDTO | None:
        instance = await cls._get_instance()
        async with instance.engine.connect() as conn:   # type: ignore
            conn: AsyncConnection
            sql_query = """
                SELECT import_id, origin, import_data, created_at
                FROM import_vault_raw_imports
                WHERE import_id = :import_id
            """
            values = {
                "import_id": import_id
            }
            result = await conn.execute(sql_text(sql_query), values)
            row = result.fetchone()
            if row is None: 
                return None
            return RawImportDTO(import_id=row[0], origin=row[1], import_data=row[2], created_at=row[3])
    
    @classmethod
    async def delete_all_rows_only_for_testing(cls):
        # Do not execute in production or staging, only for local testing
        if (os.getenv('DEPLOYMENT')=='PRODUCTION' or os.getenv('DEPLOYMENT')=='STAGING'):
            raise ValueError("This method should only be used for testing")
        else:
            instance = await cls._get_instance()
            query_delete = """
                    DELETE FROM import_vault_raw_imports
                    """
            async with instance.engine.begin() as conn:  # type: ignore
                conn: AsyncConnection
                await conn.execute(sql_text(query_delete))