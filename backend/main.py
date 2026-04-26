import io
import json
import uuid
from datetime import datetime
from typing import List

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from audit import detect_columns, run_all_tests, TEST_METADATA
from database import Base, engine, get_db
from models import AuditSession, TestResult
from schemas import AuditSessionSchema, SessionListItem

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EthicLens Audit API",
    description="AI Ethics Dataset Quality Audit Framework",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TEST_ORDER = [
    'duplicate_detection',
    'category_distribution',
    'cooccurrence',
    'refusal_detection',
    'lexical_diversity',
    'explanation_consistency',
    'severity_validation',
    'class_balance',
]


def get_quality_tier(score: float) -> str:
    if score >= 85:
        return 'Excellent'
    if score >= 70:
        return 'Good'
    if score >= 55:
        return 'Fair'
    return 'Poor'


@app.post("/api/audit", response_model=AuditSessionSchema)
async def run_audit(file: UploadFile = File(...), db: Session = Depends(get_db)):
    filename = file.filename or "unknown"
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''

    try:
        if ext == 'csv':
            # Use engine='python' and sep=None to auto-detect delimiters (comma, semicolon, tab)
            df = pd.read_csv(io.BytesIO(content), sep=None, engine='python', on_bad_lines='warn')
        elif ext in ('json', 'jsonl'):
            try:
                df = pd.read_json(io.BytesIO(content))
            except ValueError:
                # Try JSONL
                df = pd.read_json(io.BytesIO(content), lines=True)
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported file format '{ext}'. Only CSV and JSON files are supported.",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Uploaded file contains no data.")

    col_map = detect_columns(df)
    test_results = run_all_tests(df, col_map)
    composite_score = test_results.pop('composite', None)
    quality_tier = get_quality_tier(composite_score) if composite_score is not None else None

    session_id = str(uuid.uuid4())
    session = AuditSession(
        id=session_id,
        filename=filename,
        total_rows=int(len(df)),
        detected_columns=col_map,
        composite_score=composite_score,
        quality_tier=quality_tier,
        created_at=datetime.utcnow(),
    )
    db.add(session)

    for test_key in TEST_ORDER:
        result = test_results.get(test_key, {})
        test_name = TEST_METADATA.get(test_key, test_key)

        score_val = result.get('score')
        if score_val is not None:
            score_val = int(score_val)

        chart_data = result.get('chart_data')
        metrics = result.get('metrics', {})

        # Sanitize for JSON serialization
        def sanitize(obj):
            if isinstance(obj, dict):
                return {k: sanitize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [sanitize(v) for v in obj]
            if hasattr(obj, 'item'):
                return obj.item()
            return obj

        chart_data = sanitize(chart_data)
        metrics = sanitize(metrics)

        db_result = TestResult(
            session_id=session_id,
            test_name=test_name,
            score=score_val,
            status=result.get('status', 'skipped'),
            metrics=metrics,
            chart_data=chart_data,
            description=result.get('description', ''),
            recommendations=result.get('recommendations', []),
        )
        db.add(db_result)

    db.commit()
    db.refresh(session)

    return AuditSessionSchema.model_validate(session)


@app.get("/api/results/{session_id}", response_model=AuditSessionSchema)
def get_results(session_id: str, db: Session = Depends(get_db)):
    session = db.query(AuditSession).filter(AuditSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return AuditSessionSchema.model_validate(session)


@app.get("/api/sessions", response_model=List[SessionListItem])
def get_sessions(db: Session = Depends(get_db)):
    sessions = (
        db.query(AuditSession)
        .order_by(AuditSession.created_at.desc())
        .limit(10)
        .all()
    )
    return [SessionListItem.model_validate(s) for s in sessions]


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
