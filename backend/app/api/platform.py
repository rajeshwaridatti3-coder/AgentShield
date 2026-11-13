"""Integrated platform capabilities: evaluation, governance, supply-chain and incident evidence.
All security tests are synthetic and sandboxed; no external tools or side effects are invoked.
"""
from datetime import datetime, timezone
from pathlib import Path
import hashlib, re, uuid
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Document, FeatureRecord, Trace
from app.services.dlp import detect_sensitive, redact_sensitive
from app.services.retrieval import retrieve
from app.services.tracing import record, new_trace_id

router = APIRouter(prefix="/api/platform", tags=["platform intelligence and governance"])

class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=20000)
class AgentIn(BaseModel):
    task: str = Field(min_length=3, max_length=5000)
class ClaimIn(BaseModel):
    claims: list[str] = Field(min_length=1, max_length=30)
class IncidentIn(BaseModel):
    trace_id: str = Field(min_length=4, max_length=80)
class RecordIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    details: dict = Field(default_factory=dict)


def save(db, user, kind, data, status="recorded"):
    item = FeatureRecord(user_id=user.id, organization=user.organization, kind=kind, data=data, status=status)
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get("/dashboard")
def dashboard(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    docs=db.query(Document).filter(Document.organization==user.organization).count()
    traces=db.query(Trace).filter(Trace.organization==user.organization).count()
    rows=db.query(FeatureRecord).filter(FeatureRecord.organization==user.organization).all()
    counts={}
    for r in rows: counts[r.kind]=counts.get(r.kind,0)+1
    return {"organization":user.organization,"documents":docs,"traces":traces,"feature_records":counts,
            "modules":["RAG and retrieval","claim evidence verification","behavioral policy firewall","DLP","memory governance","multi-agent workflow","red-team evaluation","observability","governance center","supply-chain inventory","regression evaluation","incident replay"]}

@router.post("/dlp/scan")
def dlp_scan(payload: TextIn, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    findings=detect_sensitive(payload.text); redacted,_=redact_sensitive(payload.text)
    item=save(db,user,"dlp_scan",{"finding_count":len(findings),"types":sorted({f['type'] for f in findings}),"redacted_preview":redacted[:2000]},"flagged" if findings else "clean")
    record(db,new_trace_id(),user,"dlp.scan",{"finding_count":len(findings),"record_id":item.id})
    return {"record_id":item.id,"finding_count":len(findings),"findings":[{"type":f["type"],"position":f["start"]} for f in findings],"redacted_text":redacted}

@router.post("/agents/run")
def agents_run(payload: AgentIn, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    # Explicitly bounded orchestration pipeline; specialized agents exchange structured results.
    docs=db.query(Document).filter(Document.organization==user.organization).all()
    hits=retrieve(payload.task,docs,5)
    research={"retrieved":len(hits),"evidence":[{"document":h["filename"],"chunk":h["chunk_index"],"score":h["score"],"text":h["text"][:500]} for h in hits if h["score"]>0.03]}
    analyst={"task_type":"knowledge_question","evidence_sufficiency":"sufficient" if research["evidence"] else "insufficient"}
    verifier={"verified_source_count":len(research["evidence"]),"unsupported":not bool(research["evidence"])}
    security={"sensitive_input_findings":len(detect_sensitive(payload.task)),"cross_tenant_scope":"organization-filtered"}
    result={"workflow_id":"wf-"+uuid.uuid4().hex[:12],"agents":[{"name":"supervisor","status":"completed"},{"name":"research","result":research},{"name":"analysis","result":analyst},{"name":"verification","result":verifier},{"name":"security","result":security}],"final_status":"abstain" if verifier["unsupported"] else "evidence_ready","note":"Structured agent workflow; no hidden chain-of-thought is exposed."}
    save(db,user,"agent_workflow",result,result["final_status"]); record(db,new_trace_id(),user,"agents.workflow",{"workflow_id":result["workflow_id"],"status":result["final_status"]})
    return result

@router.post("/claims/verify")
def verify_claims(payload: ClaimIn, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    docs=db.query(Document).filter(Document.organization==user.organization).all()
    all_chunks=[]
    for d in docs:
        for i,c in enumerate(d.chunks or []):
            text=c.get("text","") if isinstance(c,dict) else str(c)
            all_chunks.append((d.filename,i,text))
    out=[]
    for claim in payload.claims:
        terms={w.lower() for w in re.findall(r"[A-Za-z0-9]{4,}",claim)}
        ranked=[]
        for fn,idx,txt in all_chunks:
            words={w.lower() for w in re.findall(r"[A-Za-z0-9]{4,}",txt)}
            score=len(terms & words)/max(1,len(terms))
            if score: ranked.append((score,fn,idx,txt))
        ranked.sort(reverse=True,key=lambda x:x[0]); top=ranked[:3]
        out.append({"claim":claim,"status":"supported_candidate" if top and top[0][0]>=0.35 else "unverified","confidence_score":round(top[0][0],3) if top else 0,"evidence":[{"filename":x[1],"chunk_index":x[2],"excerpt":x[3][:400]} for x in top]})
    save(db,user,"claim_verification",{"results":out})
    return {"results":out,"method":"lexical evidence overlap; human review required; not a semantic proof of truth"}

@router.post("/evaluations/run")
def evaluation_run(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    cases=[("email_redaction", "Contact user@example.com", "[REDACTED:email]"),("key_redaction","Key sk-1234567890abcdefghijklmnop","[REDACTED:api_key_like]"),("clean_text","Public product overview","Public product overview")]
    results=[]
    for cid,raw,expected in cases:
        actual,_=redact_sensitive(raw); passed=(expected in actual) if cid!="clean_text" else actual==expected
        results.append({"case_id":cid,"passed":passed,"expected_behavior":"redact" if cid!="clean_text" else "preserve"})
    summary={"suite":"agentshield-core-regression-v1","total":len(results),"passed":sum(r["passed"] for r in results),"results":results,"scope":"deterministic local controls; not a model safety benchmark"}
    save(db,user,"evaluation_run",summary); return summary

@router.get("/governance")
def governance(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    rows=db.query(FeatureRecord).filter(FeatureRecord.organization==user.organization).order_by(FeatureRecord.created_at.desc()).limit(100).all()
    return {"frameworks":[{"name":"NIST AI RMF","mapping":["Govern","Map","Measure","Manage"],"status":"reference mapping; not certification"},{"name":"OWASP Top 10 for LLM Applications","mapping":["Prompt injection","Sensitive information disclosure","Excessive agency","Vector and embedding weaknesses"],"status":"control crosswalk; validate against chosen version"},{"name":"ISO/IEC 42001","mapping":["AI management system evidence","risk and lifecycle governance"],"status":"informational mapping; no certification claim"}],"evidence":[{"id":r.id,"kind":r.kind,"status":r.status,"created_at":r.created_at,"data":r.data} for r in rows]}

@router.post("/supply-chain/scan")
def supply_chain_scan(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    req=Path(__file__).resolve().parents[2]/"requirements.txt"
    lines=req.read_text(encoding="utf-8").splitlines() if req.exists() else []
    packages=[]
    for line in lines:
        line=line.strip()
        if not line or line.startswith("#"): continue
        match=re.match(r"^([A-Za-z0-9_.-]+)(.*)$",line)
        if match: packages.append({"name":match.group(1),"constraint":match.group(2),"pinned":bool(re.match(r"^==",match.group(2)))})
    digest=hashlib.sha256("\n".join(lines).encode()).hexdigest()
    result={"manifest":"backend/requirements.txt","sha256":digest,"dependency_count":len(packages),"unpinned_count":sum(not p["pinned"] for p in packages),"packages":packages,"limitations":"Local manifest inventory only. No vulnerability database or registry lookup was performed; pinning is not a vulnerability verdict."}
    save(db,user,"supply_chain_scan",result); return result

@router.post("/incidents/replay")
def incident_replay(payload: IncidentIn, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    rows=db.query(Trace).filter(Trace.trace_id==payload.trace_id,Trace.organization==user.organization).order_by(Trace.created_at.asc()).all()
    if not rows: raise HTTPException(404,"Trace not found in this organization")
    result={"incident_id":"inc-"+uuid.uuid4().hex[:10],"source_trace_id":payload.trace_id,"events":[{"event_type":r.event_type,"details":r.details,"latency_ms":r.latency_ms,"created_at":r.created_at.isoformat() if r.created_at else None} for r in rows],"replay_mode":"read_only_evidence_reconstruction","external_side_effects_repeated":False}
    save(db,user,"incident_replay",result); return result

@router.get("/records")
def records(kind: str|None=None, limit:int=100, db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    q=db.query(FeatureRecord).filter(FeatureRecord.organization==user.organization)
    if kind: q=q.filter(FeatureRecord.kind==kind)
    rows=q.order_by(FeatureRecord.created_at.desc()).limit(max(1,min(limit,200))).all()
    return [{"id":r.id,"kind":r.kind,"status":r.status,"data":r.data,"created_at":r.created_at.isoformat() if r.created_at else None} for r in rows]
