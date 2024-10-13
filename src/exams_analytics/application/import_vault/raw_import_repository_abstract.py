from uuid import UUID
from abc import ABC
from abc import abstractmethod



class RawImportRepositoryAbstract(ABC):

    @classmethod
    @abstractmethod
    async def insert_raw_import(cls, import_id: UUID, origin: str, import_data: str) -> None:
        pass
