from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Approval
from app.schemas import ToolProposalIn, ApprovalDecisionIn
from app.services.policy import evaluate_tool
from app.services.tracing import new_trace_id, record
router = APIRouter(prefix="/api/tools", tags=["policy and tools"])

@router.post("/propose")
def propose(payload: ToolProposalIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    decision = evaluate_tool(user, payload.tool_name, payload.arguments)
    trace_id = new_trace_id()
    if not decision.allowed:
        record(db, trace_id, user, "tool.blocked", {"tool": payload.tool_name, "reason": decision.reason})
        return {"status": "blocked", "reason": decision.reason, "trace_id": trace_id}
    if decision.requires_approval:
        item = Approval(user_id=user.id, organization=user.organization, tool_name=payload.tool_name,
                        arguments=payload.arguments, status="pending")
        db.add(item); db.commit(); db.refresh(item)
        record(db, trace_id, user, "tool.pending_approval", {"approval_id": item.id, "tool": payload.tool_name})
        return {"status": "pending_approval", "approval_id": item.id, "trace_id": trace_id}
    record(db, trace_id, user, "tool.allowed", {"tool": payload.tool_name})
    return {"status": "allowed", "message": "Policy allowed the registered tool proposal. No external side effect is executed in this demo."}

@router.get("/approvals")
def approvals(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Approval).filter(Approval.organization == user.organization).order_by(Approval.created_at.desc()).all()
    return [{"id": a.id, "tool_name": a.tool_name, "arguments": a.arguments, "status": a.status,
             "decision_reason": a.decision_reason, "created_at": a.created_at} for a in rows]

@router.post("/approvals/{approval_id}/decision")
def decide(approval_id: int, payload: ApprovalDecisionIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.decision not in {"approved", "rejected"}:
        raise HTTPException(422, "Decision must be approved or rejected")
    item = db.query(Approval).filter(Approval.id == approval_id, Approval.organization == user.organization).first()
    if not item: raise HTTPException(404, "Approval not found")
    if item.status != "pending": raise HTTPException(409, "Approval already decided")
    if payload.decision == "approved" and user.role != "admin":
        raise HTTPException(403, "Only an administrator can approve sensitive actions")
    item.status = payload.decision
    item.decision_reason = payload.reason[:500]
    db.commit()
    record(db, new_trace_id(), user, "approval.decided", {"approval_id": item.id, "decision": item.status})
    return {"id": item.id, "status": item.status}
