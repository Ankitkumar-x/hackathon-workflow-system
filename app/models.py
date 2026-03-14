# python-engine/app/models.py
from sqlalchemy import Column, String, JSON, TIMESTAMP, Boolean, Integer, text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

def gen_uuid():
    return str(uuid.uuid4())

class RequestModel(Base):
    __tablename__ = "requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, nullable=True)
    workflow = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('workflow', 'external_id', name='uq_workflow_externalid'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String, nullable=False)
    detail = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    key = Column(String, primary_key=True)
    request_id = Column(UUID(as_uuid=True), nullable=False)
    response_snapshot = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())