from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ARRAY, Text, Index
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

"""
    Contains the best results of the exames for each student with traceability
"""
best_marks_of_student_per_test : Table = Table(
    'best_marks_of_student_per_test', metadata,
    Column('student_id', String(50), primary_key=True),
    Column('test_id', String(50), primary_key=True),
    Column('num_questions', Integer, nullable=False),        
    Column('num_correct', Integer, nullable=False),
    Column('import_ids', ARRAY(UUID), nullable=False),  # origin of the marks that were considered to calculate this row
    Column('created_at', DateTime(timezone=True), server_default=func.now(), nullable=False),
    Column('updated_at', DateTime(timezone=True), onupdate=func.now(), nullable=False),
    Index('idx_test_id', 'test_id')  # Index on test_id
)