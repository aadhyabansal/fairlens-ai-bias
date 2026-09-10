from pydantic import BaseModel, Field

class ReportFinding(BaseModel):
    title: str
    explanation: str        # plain-language, real-world-harm framing
    cited_metric: str       # which metric/number this finding is grounded in
    severity: str           # "low" / "moderate" / "high" / "critical"
    recommendation: str     # specific, tied to the cited metric/feature

class ReportRequest(BaseModel):
    audit_json: dict        # raw dict form of AuditResult (or MitigationResult, TextBiasResult)
    context: str = ""       # optional: "lending model", "hiring dataset", etc.

class ReportResult(BaseModel):
    summary: str
    findings: list[ReportFinding]
    validation_passed: bool
    validation_notes: list[str] = Field(default_factory=list)