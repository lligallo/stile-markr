

from typing import Dict, List
import os

import logging

from exams_analytics.application.marks.best_marks_repository_abstract import BestMarksRepositoryAbstract
from exams_analytics.application.marks.marks_dtos import MarkDTO
from exams_analytics.interface.pg_db.database_engine import DatabaseEngine

logger = logging.getLogger(__name__)

class BestMarksRepositoryPG(BestMarksRepositoryAbstract):
    """
    This repository stores the maximum marks per each student and test.
    It allows inserting new marks in bulk.
    See ADR-03 for implementation decisions
    """
    _instance = None
    MAX_MARKS_TO_INSERT = 10_000
    SIZE_MARK_CHUNK_WHEN_BULK_INSERT = 1000

    def __init__(self):
        self.engine = DatabaseEngine.get_engine()

    @classmethod
    async def _get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    
    @classmethod
    async def bulk_insert_keeping_max_values_when_same_student_and_test_id(cls, marks: List[MarkDTO]) -> None:
        for m in marks:
            print(m)