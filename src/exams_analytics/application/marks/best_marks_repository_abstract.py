from abc import ABC, abstractmethod
from typing import List

from exams_analytics.application.marks.marks_dtos import MarkDTO

class BestMarksRepositoryAbstract(ABC):

    @classmethod
    @abstractmethod
    async def bulk_insert_keeping_max_values_when_same_student_and_test_id(cls, marks: List[MarkDTO]) -> None:
        pass

