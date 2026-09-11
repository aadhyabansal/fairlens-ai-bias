import uuid
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.schemas.audit import AuditRequest, AuditResult, MitigationRequest, MitigationResult
from app.schemas.text_bias import TextBiasRequest, TextBiasResult
from app.schemas.report import ReportRequest, ReportResult
from app.engine.metrics import run_audit
from app.engine.mitigation import run_mitigation
from app.engine.text_bias import run_text_bias_test
from app.engine.report import generate_report
from app.engine.validation import ValidationError

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


@app.post("/audit/run", response_model=AuditResult)
def audit_run(request: AuditRequest):
    try:
        return run_audit(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/mitigate", response_model=MitigationResult)
def mitigate(request: MitigationRequest):
    try:
        return run_mitigation(request)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/text-bias", response_model=TextBiasResult)
def text_bias(request: TextBiasRequest):
    return run_text_bias_test(request)


@app.post("/report", response_model=ReportResult)
def report(request: ReportRequest):
    return generate_report(request)

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
