import uuid
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.audit import AuditRequest, AuditResult, MitigationRequest, MitigationResult
from app.schemas.text_bias import TextBiasRequest, TextBiasResult
from app.schemas.report import ReportRequest, ReportResult
from app.engine.metrics import run_audit
from app.engine.mitigation import run_mitigation
from app.engine.text_bias import run_text_bias_test
from app.engine.report import generate_report
from app.engine.validation import ValidationError
from app.core.database import get_db
from app.core.models import AuditRun
from app.core import crud

app = FastAPI(title="FairLens API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/mitigate", response_model=MitigationResult)
def mitigate(request: MitigationRequest):
    try:
        return run_mitigation(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text-bias", response_model=TextBiasResult)
def text_bias(request: TextBiasRequest):
    return run_text_bias_test(request)

UPLOAD_DIR = "data/uploads"

@app.post("/upload")
def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    file_id = str(uuid.uuid4())
    saved_path = f"{UPLOAD_DIR}/{file_id}.csv"

    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"dataset_path": saved_path, "original_filename": file.filename}

@app.post("/audit/run", response_model=AuditResult)
def audit_run(request: AuditRequest, db: Session = Depends(get_db)):
    try:
        result = run_audit(request)
        crud.save_audit_run(db, result, request.dataset_path)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/audit/history")
def audit_history(db: Session = Depends(get_db)):
    runs = crud.get_audit_history(db)
    return [
        {
            "id": str(r.id),
            "dataset_path": r.dataset_path,
            "target_column": r.target_column,
            "overall_accuracy": r.overall_accuracy,
            "created_at": r.created_at.isoformat() + "Z",
        }
        for r in runs
    ]

@app.post("/report", response_model=ReportResult)
def report(request: ReportRequest, audit_run_id: str = None, db: Session = Depends(get_db)):
    result = generate_report(request)
    if audit_run_id:
        try:
            run_uuid = uuid.UUID(audit_run_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid audit_run_id format")
        db_run = db.query(AuditRun).filter(AuditRun.id == run_uuid).first()
        if db_run:
            crud.save_report(db, db_run.id, result)
    return result
