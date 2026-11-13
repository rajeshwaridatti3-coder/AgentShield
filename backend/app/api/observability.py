from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Trace, Usage
router = APIRouter(prefix="/api", tags=["observability"])

@router.get("/traces")
def traces(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    limit = max(1, min(limit, 200))
    rows = db.query(Trace).filter(Trace.organization == user.organization).order_by(Trace.created_at.desc()).limit(limit).all()
    return [{"trace_id": r.trace_id, "event_type": r.event_type, "details": r.details,
             "latency_ms": r.latency_ms, "created_at": r.created_at} for r in rows]

@router.get("/metrics/summary")
def metrics(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    q = db.query(Usage).filter(Usage.organization == user.organization)
    rows = q.all()
    return {"requests": len(rows), "prompt_tokens": sum(r.prompt_tokens for r in rows),
            "completion_tokens": sum(r.completion_tokens for r in rows),
            "estimated_cost_usd": round(sum(r.estimated_cost_usd for r in rows), 6),
            "average_latency_ms": round(sum(r.latency_ms for r in rows)/len(rows), 2) if rows else 0}
