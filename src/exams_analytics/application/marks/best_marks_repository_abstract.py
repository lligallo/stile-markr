from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from exams_analytics.application.marks.marks_dtos import AggregatedTestResultDTO, MarkDTO

class BestMarksRepositoryAbstract(ABC):

    @classmethod
    @abstractmethod
    async def bulk_insert_keeping_max_values_when_same_student_and_test_id(cls, marks: List[MarkDTO], import_vault_id: UUID) -> None:
        """
        Inserts a list of marks into the database. It keeps the maximum values for each student and test.
        It also stores the import_vault_id that influenced the changes.
        """
        pass

    @classmethod
    @abstractmethod
    async def calculate_aggregated_test_result(cls, test_id: str) -> AggregatedTestResultDTO:
        """
        Calculates the aggregated test result for a given test_id.
        """
        pass
