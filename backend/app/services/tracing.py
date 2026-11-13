import uuid, time
from sqlalchemy.orm import Session
from app.models import Trace

def new_trace_id():
    return "tr-" + uuid.uuid4().hex[:16]

def record(db: Session, trace_id: str, user, event_type: str, details: dict, latency_ms: float = 0):
    safe_details = {k: v for k, v in details.items() if k.lower() not in {"password", "api_key", "token", "secret"}}
    db.add(Trace(trace_id=trace_id, user_id=user.id, organization=user.organization,
                 event_type=event_type, details=safe_details, latency_ms=latency_ms))
    db.commit()
