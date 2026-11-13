import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Document, Usage
from app.schemas import ChatIn
from app.services.retrieval import retrieve
from app.services.llm import provider
from app.services.dlp import redact_sensitive
from app.services.tracing import new_trace_id, record
router = APIRouter(prefix="/api", tags=["RAG"])

@router.post("/chat")
async def chat(payload: ChatIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    start = time.perf_counter()
    trace_id = new_trace_id()
    safe_question, question_findings = redact_sensitive(payload.question)
    docs = db.query(Document).filter(Document.organization == user.organization).all()
    hits = retrieve(safe_question, docs, payload.top_k)
    context = "\n".join(f"[{h['filename']}#{h['chunk_index']}] {h['text']}" for h in hits if h["score"] > 0.03)
    answer, model = await provider.answer(safe_question, context)
    safe_answer, findings = redact_sensitive(answer)
    latency = (time.perf_counter() - start) * 1000
    record(db, trace_id, user, "rag.completed", {"model": model, "retrieved_chunks": len(hits),
           "dlp_findings": len(findings) + len(question_findings), "question_length": len(safe_question)}, latency)
    usage = Usage(user_id=user.id, organization=user.organization, model=model,
                  prompt_tokens=max(1, len(payload.question + context)//4),
                  completion_tokens=max(1, len(answer)//4), estimated_cost_usd=0.0, latency_ms=latency)
    db.add(usage); db.commit()
    return {"answer": safe_answer, "citations": [{"document_id": h["document_id"], "filename": h["filename"],
            "chunk_index": h["chunk_index"], "score": h["score"], "excerpt": h["text"][:280]} for h in hits if h["score"] > 0.03],
            "trace_id": trace_id, "model": model, "latency_ms": round(latency, 2),
            "abstained": not bool(context), "dlp_redactions": len(findings) + len(question_findings)}
