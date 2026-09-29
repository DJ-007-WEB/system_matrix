import json,os
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter,Depends,UploadFile,File,HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .database import SessionLocal,Supplier,Material,PurchaseOrder,Document,Alert,Decision
from .risk import runway_days,supplier_score,classify_risk
from .extraction import extract_with_provider
router=APIRouter(prefix="/api")
def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()
class DecisionIn(BaseModel): action:str; comment:str=""
@router.get("/dashboard")
def dashboard(session:Session=Depends(db)):
    suppliers=session.query(Supplier).all(); materials=session.query(Material).all(); orders=session.query(PurchaseOrder).all(); alerts=session.query(Alert).order_by(Alert.created_at.desc()).all()
    mm={m.id:m for m in materials}; sm={s.id:s for s in suppliers}; rows=[]
    for p in orders:
        m=mm[p.material_id]; s=sm[p.supplier_id]; runway=runway_days(m.on_hand,m.in_transit,m.reserved,m.daily_consumption); days=max(0,(p.promised_date-datetime.utcnow()).total_seconds()/86400); delay=max(0,(1-s.on_time_rate)*7); risk=classify_risk(runway,days,delay)
        rows.append({"id":p.id,"po_number":p.po_number,"supplier":s.name,"material":m.name,"promised_date":p.promised_date.isoformat(),"runway_days":None if runway==float("inf") else round(runway,1),"predicted_delay_days":round(delay,1),"risk":risk})
    return {"summary":{"suppliers":len(suppliers),"materials":len(materials),"open_orders":sum(p.status=="open" for p in orders),"critical_alerts":sum(a.severity=="critical" and a.status=="pending" for a in alerts)},"suppliers":[{"id":s.id,"name":s.name,"category":s.category,"score":supplier_score(s.on_time_rate,s.order_accuracy,s.quality_issues),"on_time_rate":s.on_time_rate,"order_accuracy":s.order_accuracy,"quality_issues":s.quality_issues} for s in suppliers],"orders":rows,"alerts":[{"id":a.id,"severity":a.severity,"title":a.title,"message":a.message,"recommendation":a.recommendation,"status":a.status,"evidence":json.loads(a.evidence_json)} for a in alerts]}
@router.post("/documents/upload")
async def upload_document(file:UploadFile=File(...),session:Session=Depends(db)):
    allowed={".pdf",".png",".jpg",".jpeg",".webp",".csv",".xlsx",".xls"}; ext=Path(file.filename or "").suffix.lower()
    if ext not in allowed: raise HTTPException(400,"Unsupported file type")
    root=Path(os.getenv("UPLOAD_DIR","./uploads")); root.mkdir(parents=True,exist_ok=True); name=Path(file.filename).name; path=root/name; path.write_bytes(await file.read())
    extracted=await extract_with_provider(str(path)); doc=Document(filename=name,document_type=extracted.get("document_type","unknown"),confidence=float(extracted.get("confidence",0)),extracted_json=json.dumps(extracted)); session.add(doc); session.commit(); session.refresh(doc)
    return {"id":doc.id,"filename":doc.filename,"document_type":doc.document_type,"confidence":doc.confidence,"extracted":extracted}
@router.post("/alerts/{alert_id}/decision")
def decision(alert_id:int,payload:DecisionIn,session:Session=Depends(db)):
    if payload.action not in {"approve","modify","reject"}: raise HTTPException(400,"Invalid action")
    a=session.get(Alert,alert_id)
    if not a: raise HTTPException(404,"Alert not found")
    a.status=payload.action; session.add(Decision(alert_id=alert_id,action=payload.action,comment=payload.comment)); session.commit(); return {"status":"ok"}
@router.post("/demo/refresh")
def refresh(session:Session=Depends(db)):
    session.query(Alert).delete(); session.commit(); orders=session.query(PurchaseOrder).all()
    for p in orders:
        m=session.get(Material,p.material_id); s=session.get(Supplier,p.supplier_id); runway=runway_days(m.on_hand,m.in_transit,m.reserved,m.daily_consumption); days=max(0,(p.promised_date-datetime.utcnow()).total_seconds()/86400); delay=max(0,(1-s.on_time_rate)*7); risk=classify_risk(runway,days,delay)
        if risk!="normal": session.add(Alert(po_id=p.id,severity="critical" if risk=="production-critical" else "warning",title=p.po_number+": "+risk.replace("-"," "),message=f"{m.name} has {runway:.1f} days of runway versus {days+delay:.1f} days until predicted arrival.",recommendation="Contact supplier for updated ETA and review alternative sourcing if production coverage is insufficient.",evidence_json=json.dumps({"po_number":p.po_number,"supplier":s.name,"runway_days":round(runway,1),"predicted_delay_days":round(delay,1),"promised_date":p.promised_date.isoformat()})))
    session.commit(); return {"status":"refreshed"}
