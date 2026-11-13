from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Memory
from app.schemas import MemoryIn
from app.services.dlp import redact_sensitive
router = APIRouter(prefix="/api/memory", tags=["memory governance"])

@router.get("")
def list_memory(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Memory).filter(Memory.user_id == user.id).order_by(Memory.created_at.desc()).all()
    now = datetime.now(timezone.utc)
    def active(m):
        expiry = m.expires_at
        if expiry and expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        return not expiry or expiry > now
    return [{"id": m.id, "content": m.content, "expires_at": m.expires_at} for m in rows if active(m)]

@router.post("")
def add_memory(payload: MemoryIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    safe, findings = redact_sensitive(payload.content)
    if findings: raise HTTPException(422, "Memory contains sensitive information and was not saved")
    item = Memory(user_id=user.id, organization=user.organization, content=safe,
                  expires_at=datetime.now(timezone.utc) + timedelta(days=30))
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "expires_at": item.expires_at}

@router.delete("/{memory_id}")
def delete_memory(memory_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    item = db.query(Memory).filter(Memory.id == memory_id, Memory.user_id == user.id).first()
    if not item: raise HTTPException(404, "Memory not found")
    db.delete(item); db.commit()
    return {"deleted": True}
