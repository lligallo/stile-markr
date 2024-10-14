from typing import List
from uuid import UUID
from pydantic import BaseModel, validator
from datetime import datetime

class MarkDTO(BaseModel):
    student_id: str             #str to allow any student_id in future systems
    test_id: str                #str to allow any test_id in future systems
    num_questions : int
    num_correct: int
    
    @validator('test_id')
    def check_test_id_length(cls, v):
        if len(v) > 50:
            raise ValueError('test_id must be 50 characters or fewer')
        return v

    @validator('student_id')
    def check_student_id_length(cls, v):
        if len(v) > 50:
            raise ValueError('test_id must be 50 characters or fewer')
        return v

class MarkWithImportIdsDTO(MarkDTO):
    import_ids : List[UUID]      #list of the import_ids that influenced the mark (it is a list since sometimes the marks are reported more than once)

class AggregatedTestResultDTO(BaseModel):
    test_id: str
    mean: float             # goes from 0 to 1
    stddev: float           # goes from 0 to 1
    min: float              # goes from 0 to 1
    max: float              # goes from 0 to 1
    p25: float              # goes from 0 to 1
    p50: float              # goes from 0 to 1
    p75: float              # goes from 0 to 1
    count: int              # goes from 0 to 1