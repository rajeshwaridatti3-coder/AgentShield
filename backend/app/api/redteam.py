from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, FeatureRecord
from app.services.evaluation import run_suite
from app.services.tracing import record, new_trace_id
router = APIRouter(prefix="/api/redteam", tags=["red-team evaluation"])

@router.post("/run")
def run(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    result=run_suite()
    db.add(FeatureRecord(user_id=user.id,organization=user.organization,kind="redteam_run",status="completed",data=result)); db.commit()
    record(db,new_trace_id(),user,"redteam.completed",{"total":result["total"],"passed":result["passed"]})
    return result

@router.get("/runs")
def runs(db: Session=Depends(get_db), user: User=Depends(get_current_user)):
    rows=db.query(FeatureRecord).filter(FeatureRecord.organization==user.organization,FeatureRecord.kind=="redteam_run").order_by(FeatureRecord.created_at.desc()).limit(50).all()
    return {"runs":[{"id":r.id,"created_at":r.created_at,"result":r.data} for r in rows]}
