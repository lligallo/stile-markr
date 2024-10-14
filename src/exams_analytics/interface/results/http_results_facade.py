from quart import Blueprint
import logging
import json

from exams_analytics.application.marks.marks_dtos import AggregatedTestResultDTO
from exams_analytics.application.marks.marks_service import MarksService

http_results_facade = Blueprint("results_facade", __name__)

logger = logging.getLogger(__name__)


@http_results_facade.route('/results/<test_id>/aggregate')
async def aggregate(test_id: str):
    """
    Returns the aggregated results for a test
    """
    logger.warning("There is no security or authentication yet")
    result : AggregatedTestResultDTO | None = await MarksService.aggregate_by_test_id(test_id)
    if result is None:
        return f"No results found for the test id {test_id}", 404
    else:
        results_t = {
                    "mean":result.mean * 100,
                    "stddev":result.stddev * 100,
                    "min":result.min * 100,
                    "max":result.max * 100,
                    "p25":result.p25 * 100,
                    "p50":result.p50 * 100,
                    "p75":result.p75 * 100,
                    "count":result.count
                    }
        formatted_result = {key: round(value, 1) if isinstance(value, float) else value for key, value in results_t.items()}
        output = json.dumps(formatted_result)
        return output, 200