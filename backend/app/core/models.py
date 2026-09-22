import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class AuditRun(Base):
    __tablename__ = "audit_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=True)
    target_column = Column(String, nullable=False)
    overall_accuracy = Column(Float, nullable=False)
    metrics_json = Column(JSON, nullable=False)  # full AuditResult, stored as-is
    created_at = Column(DateTime, default=datetime.utcnow)

    reports = relationship("Report", back_populates="audit_run")


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_run_id = Column(UUID(as_uuid=True), ForeignKey("audit_runs.id"), nullable=False)
    summary = Column(String, nullable=False)
    findings_json = Column(JSON, nullable=False)  # list of ReportFinding, stored as-is
    validation_passed = Column(String, nullable=False)  # "true"/"false" as string for simplicity
    created_at = Column(DateTime, default=datetime.utcnow)

    audit_run = relationship("AuditRun", back_populates="reports")