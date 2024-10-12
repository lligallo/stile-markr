from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Boolean, JSON, BigInteger, Index, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func

metadata = MetaData()

"""
    Contains the raw imports
"""
import_vault_imports : Table = Table(
    'import_vault_raw_imports', metadata,
    Column('import_id', UUID(as_uuid=True), default=uuid.uuid1, primary_key=True),
    Column('origin', String(50), nullable=False),  # specifies the origin, format, ... of the import
    Column('import_data', Text, nullable=False),  # the raw data of the import
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False)
)