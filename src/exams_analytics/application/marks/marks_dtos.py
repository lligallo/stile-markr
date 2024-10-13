from typing import List
from uuid import UUID
from pydantic import BaseModel, validator
from datetime import datetime

class MarkDTO(BaseModel):
    student_id: int
    test_id: str
    num_questions : int
    num_correct: int
    import_ids : List[UUID]      #list of the import_ids that influenced the mark (it is a list since sometimes the marks are reported more than once)

    @validator('import_ids')
    def check_import_ids(cls, v):
        if not v or len(v) < 1:
            raise ValueError('import_ids must contain at least one element')
        return v