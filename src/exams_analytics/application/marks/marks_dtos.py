from typing import List
from uuid import UUID
from pydantic import BaseModel, validator
from datetime import datetime

class MarkDTO(BaseModel):
    student_id: str             #str to allow any student_id in future systems
    test_id: str                #str to allow any test_id in future systems
    num_questions : int
    num_correct: int
    import_ids : List[UUID]      #list of the import_ids that influenced the mark (it is a list since sometimes the marks are reported more than once)

    @validator('import_ids')
    def check_import_ids(cls, v):
        if not v or len(v) < 1:
            raise ValueError('import_ids must contain at least one element')
        return v
    
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

class AggregatedTestResultDTO(BaseModel):
    test_id: str
    mean: float
    stddev: float
    min: float
    max: float
    p25: float
    p50: float
    p75: float
    count: int