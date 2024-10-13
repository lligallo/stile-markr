import uuid
import logging 
from enum import Enum
from uuid import UUID

from exams_analytics.application.import_vault.raw_import_repository_abstract import RawImportRepositoryAbstract
from exams_analytics.interface.pg_db.raw_import_repository_pg import RawImportRepositoryPG

logger = logging.getLogger(__name__)

class ImportOrigin(str, Enum):
    SCANNER_SYSTEM = "scanner_system_xyz"       #Do not change this value, it is used in the database

class ImportVaultService:
    import_raw_repository : type[RawImportRepositoryAbstract] = RawImportRepositoryPG

    @classmethod
    async def import_raw_data(cls, origin: ImportOrigin, import_data: str) -> UUID:
        logger.warning("Add the user who did it, once we have authentication")
        import_id : UUID = uuid.uuid1()
        await cls.import_raw_repository.insert_raw_import(import_id, origin, import_data)
        return import_id