import uuid
import json
import datetime
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.models.diagram import EvalSummary
from app.models.database import get_db, EvalRunRecord, log_audit
from app.core.auth import get_current_user, require_role, verify_csrf
from app.services.eval_suite import EvaluationSuite

router = APIRouter(prefix="/api/eval", tags=["evaluation"])

@router.post("/run", response_model=EvalSummary)
async def run_benchmark_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(require_role("analyst"))
):
    """Executes the reproducible 20-sample AI/ML diagram evaluation benchmark."""
    verify_csrf(request, user)
    summary = EvaluationSuite.run_benchmark()
    run_id = str(uuid.uuid4())

    record = EvalRunRecord(
        id=run_id,
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        executed_by=user.get("email", "unknown"),
        total_samples=summary.total_samples,
        passed_samples=summary.passed_samples,
        pass_rate=summary.pass_rate,
        results_json=json.dumps(summary.model_dump())
    )
    db.add(record)
    db.commit()

    log_audit(db, user.get("email", "unknown"), "RUN_EVAL", "benchmark", run_id, {
        "pass_rate": summary.pass_rate,
        "total": summary.total_samples
    })

    return summary

@router.get("/latest", response_model=Optional[EvalSummary])
async def get_latest_eval(
    db: Session = Depends(get_db),
    user: Dict[str, Any] = Depends(get_current_user)
):
    record = db.query(EvalRunRecord).order_by(EvalRunRecord.timestamp.desc()).first()
    if not record:
        # If no previous run recorded in database, run once dynamically
        return EvaluationSuite.run_benchmark()
    data = json.loads(record.results_json)
    return EvalSummary(**data)
