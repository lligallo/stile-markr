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

