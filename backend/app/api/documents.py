from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader
from io import BytesIO
from app.core.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
from app.models import User, Document
from app.services.dlp import redact_sensitive
from app.services.retrieval import split_chunks
router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    raw = await file.read()
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "File exceeds configured upload limit")
    name = (file.filename or "upload").lower()
    if not (name.endswith(".txt") or name.endswith(".md") or name.endswith(".pdf")):
        raise HTTPException(415, "Only .txt, .md and .pdf files are supported")
    try:
        if name.endswith(".pdf"):
            reader = PdfReader(BytesIO(raw))
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            content = raw.decode("utf-8")
    except Exception:
        raise HTTPException(400, "Could not parse document")
    if not content.strip():
        raise HTTPException(400, "Document contains no extractable text")
    safe_content, findings = redact_sensitive(content)
    doc = Document(owner_id=user.id, organization=user.organization, filename=file.filename or "upload",
                   content=safe_content, chunks=split_chunks(safe_content))
    db.add(doc); db.commit(); db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "chunks": len(doc.chunks),
            "sensitive_items_redacted": len(findings), "status": "indexed"}

@router.get("")
def list_documents(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.organization == user.organization).order_by(Document.created_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "chunks": len(d.chunks), "created_at": d.created_at} for d in docs]

@router.delete("/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.organization == user.organization).first()
    if not doc: raise HTTPException(404, "Document not found")
    db.delete(doc); db.commit()
    return {"deleted": True}
