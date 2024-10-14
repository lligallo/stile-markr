import logging
from exams_analytics.application.marks.best_marks_repository_abstract import BestMarksRepositoryAbstract
from exams_analytics.application.marks.marks_dtos import AggregatedTestResultDTO, MarkDTO
from exams_analytics.interface.pg_db.best_marks_respository_pg import BestMarksRepositoryPG


logger = logging.getLogger(__name__)

class MarksService:

    best_marks_repository : type[BestMarksRepositoryAbstract] = BestMarksRepositoryPG

    @classmethod
    async def insert_marks(cls, mark_dtos: list[MarkDTO]):
        logger.warning("Add the user who did it, once we have authentication")
        await cls.best_marks_repository.bulk_insert_keeping_max_values_when_same_student_and_test_id(mark_dtos)
    
    @classmethod
    async def aggregate_by_test_id(cls, test_id: str) -> AggregatedTestResultDTO:
        logger.warning("Add the user who did it, once we have authentication")
        return await cls.best_marks_repository.calculate_aggregated_test_result(test_id)
