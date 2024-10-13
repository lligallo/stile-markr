
from datetime import datetime
from pydantic import BaseModel
from uuid import UUID

class RawImportDTO(BaseModel):
    import_id: UUID
    origin: str
    import_data: str
    created_at: datetime