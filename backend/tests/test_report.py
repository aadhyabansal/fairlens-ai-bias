import json
from app.engine.report import generate_report
from app.schemas.report import ReportRequest
from app.engine.metrics import run_audit
from app.schemas.audit import AuditRequest


def test_report_grounded_in_real_audit():
    audit_request = AuditRequest(
        dataset_path="data/samples/adult_income.csv",
        target_column="income",
        sensitive_attributes=["sex"],
    )
    audit_result = run_audit(audit_request)

    report_request = ReportRequest(
        audit_json=json.loads(audit_result.model_dump_json()),
        context="Income prediction model",
    )
    report = generate_report(report_request)

    print(f"\nSummary: {report.summary}")
    for f in report.findings:
        print(f"\n[{f.severity.upper()}] {f.title}")
        print(f"  Cited: {f.cited_metric}")
        print(f"  {f.explanation}")
        print(f"  Recommendation: {f.recommendation}")

    print(f"\nValidation passed: {report.validation_passed}")
    print(f"Validation notes: {report.validation_notes}")

    assert len(report.findings) > 0