import json
from sqlalchemy.orm import Session
from app.core.models import AuditRun, Report
from app.schemas.audit import AuditResult
from app.schemas.report import ReportResult


def save_audit_run(db: Session, audit_result: AuditResult, dataset_path: str, original_filename: str = None) -> AuditRun:
    db_run = AuditRun(
        dataset_path=dataset_path,
        original_filename=original_filename,
        target_column=audit_result.target_column,
        overall_accuracy=audit_result.overall_accuracy,
        metrics_json=json.loads(audit_result.model_dump_json()),
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run


def save_report(db: Session, audit_run_id, report_result: ReportResult) -> Report:
    db_report = Report(
        audit_run_id=audit_run_id,
        summary=report_result.summary,
        findings_json=json.loads(report_result.model_dump_json())["findings"],
        validation_passed=str(report_result.validation_passed),
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def get_audit_history(db: Session, limit: int = 20):
    return db.query(AuditRun).order_by(AuditRun.created_at.desc()).limit(limit).all()


def get_audit_run(db: Session, run_id):
    return db.query(AuditRun).filter(AuditRun.id == run_id).first()