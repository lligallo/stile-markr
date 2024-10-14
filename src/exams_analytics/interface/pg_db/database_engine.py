import os
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import quote
import functools
import time

logger = logging.getLogger(__name__)

def check_environment_variables_for_database():
    if os.getenv('PG_USER') is None:
        raise ValueError("The PG_USER environment variable is not set.")
    if os.getenv('PG_PASSWORD') is None:
        raise ValueError("The PG_PASSWORD environment variable is not set.")
    if os.getenv('PG_ADDRESS') is None:
        raise ValueError("The PG_ADDRESS environment variable is not set.")
    if os.getenv('PG_PORT') is None:
        raise ValueError("The PG_PORT environment variable is not set.")
    if os.getenv('PG_DBNAME') is None:
        raise ValueError("The PG_DBNAME environment variable is not set.")

check_environment_variables_for_database()
class DatabaseEngine:
    _engine = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            DATABASE_URL = f"postgresql+asyncpg://{quote(os.getenv('PG_USER',''))}:{quote(os.getenv('PG_PASSWORD',''))}@{os.getenv('PG_ADDRESS','')}:{os.getenv('PG_PORT','')}/{os.getenv('PG_DBNAME','')}"
            cls._engine = create_async_engine(DATABASE_URL, echo=False, pool_recycle=250, pool_pre_ping=True)

        return cls._engine


def log_db_operation(threshold_ms: int| None = None):
    """
    Decorator that logs the duration of a database operation.
    It also includes the threshold_ms parameter, which will log a warning if the operation exceeds the threshold.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            duration_ms = (end_time - start_time) * 1000
            logger.info(f"{func.__name__} took(ms): {int(duration_ms)}")
            if threshold_ms is not None and duration_ms > threshold_ms:
                logger.warning(f"{func.__name__} took (ms): {int(duration_ms)}, which exceeds the threshold of {threshold_ms} ms")
            return result
        return wrapper
    return decorator