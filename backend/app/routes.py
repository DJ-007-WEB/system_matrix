import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import SessionLocal, Supplier, Material, PurchaseOrder, Document, Alert, Decision
from .risk import (
    runway_days,
    supplier_score,
    classify_risk,
    fuzzy_supplier_match,
    financial_check,
    normalize_unit,
)
from .extraction import extract_with_provider

router = APIRouter(prefix="/api")

def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

class DecisionIn(BaseModel):
    action: str
    comment: str = ""

def _add_alert(session, po_id, severity, title, message, recommendation, evidence):
    alert = Alert(
        po_id=po_id,
        severity=severity,
        title=title,
        message=message,
        recommendation=recommendation,
        evidence_json=json.dumps(evidence),
    )
    session.add(alert)
    return alert

def _reconcile_document(session, document, extracted):
    evidence_base = {
        "document_id": document.id,
        "filename": document.filename,
        "document_type": extracted.get("document_type"),
        "confidence": extracted.get("confidence", 0),
    }
    alerts = []

    suppliers = session.query(Supplier).all()
    matched_supplier, supplier_match_score = fuzzy_supplier_match(
        extracted.get("supplier_name"), suppliers
    )
    if extracted.get("supplier_name") and not matched_supplier:
        alerts.append(_add_alert(
            session, None, "warning", "Supplier entity needs review",
            f"Could not confidently match supplier '{extracted.get('supplier_name')}' to the supplier master.",
            "Review the supplier identity before using this document for downstream decisions.",
            {**evidence_base, "extracted_supplier": extracted.get("supplier_name"),
             "match_score": supplier_match_score},
        ))

    po_number = extracted.get("po_number")
    po = session.query(PurchaseOrder).filter(PurchaseOrder.po_number == po_number).first() if po_number else None
    if po:
        supplier = session.get(Supplier, po.supplier_id)
        material = session.get(Material, po.material_id)
        items = extracted.get("items") or []
        if items:
            extracted_qty = float(items[0].get("quantity") or 0)
            extracted_unit = normalize_unit(items[0].get("unit"))
            expected_unit = normalize_unit(material.unit)
            if extracted_qty and abs(extracted_qty - po.quantity) > 0.01:
                alerts.append(_add_alert(
                    session, po.id, "warning", f"{po_number}: quantity discrepancy",
                    f"Document quantity {extracted_qty:g} differs from PO quantity {po.quantity:g}.",
                    "Review the line-item discrepancy before accepting the document.",
                    {**evidence_base, "po_number": po_number, "po_quantity": po.quantity,
                     "document_quantity": extracted_qty},
                ))
            if extracted_unit and expected_unit and extracted_unit != expected_unit:
                alerts.append(_add_alert(
                    session, po.id, "warning", f"{po_number}: unit discrepancy",
                    f"Document unit '{extracted_unit}' differs from PO/material unit '{expected_unit}'.",
                    "Confirm the unit conversion or correct the source document.",
                    {**evidence_base, "document_unit": extracted_unit, "expected_unit": expected_unit},
                ))
            if items[0].get("unit_price") is not None and abs(float(items[0]["unit_price"]) - po.unit_price) > 0.01:
                alerts.append(_add_alert(
                    session, po.id, "warning", f"{po_number}: price discrepancy",
                    f"Document unit price {float(items[0]['unit_price']):.2f} differs from PO price {po.unit_price:.2f}.",
                    "Verify the commercial terms before accepting the invoice or delivery document.",
                    {**evidence_base, "po_unit_price": po.unit_price,
                     "document_unit_price": float(items[0]["unit_price"])},
                ))

        financial_issues = financial_check(extracted)
        for issue in financial_issues:
            alerts.append(_add_alert(
                session, po.id, "warning", f"{po_number}: financial discrepancy",
                f"Financial check failed: {issue['type']}.",
                "Review the invoice arithmetic and source values before approval.",
                {**evidence_base, **issue},
            ))

        if extracted.get("promised_delivery_date"):
            try:
                promised = datetime.fromisoformat(extracted["promised_delivery_date"])
                if abs((promised.date() - po.promised_date.date()).days) > 0:
                    alerts.append(_add_alert(
                        session, po.id, "warning", f"{po_number}: promised-date discrepancy",
                        "The document contains a promised delivery date different from the PO.",
                        "Confirm the supplier-confirmed date and update the PO only after human review.",
                        {**evidence_base, "po_promised_date": po.promised_date.isoformat(),
                         "document_promised_date": extracted["promised_delivery_date"]},
                    ))
            except ValueError:
                pass
    elif po_number:
        alerts.append(_add_alert(
            session, None, "warning", f"{po_number}: PO not found",
            "The extracted PO number does not exist in the purchase-order master.",
            "Review the PO reference before linking this document to an order.",
            {**evidence_base, "po_number": po_number},
        ))

    low_conf = extracted.get("low_confidence_fields") or []
    if float(extracted.get("confidence") or 0) < 0.75 or low_conf:
        alerts.append(_add_alert(
            session, po.id if po else None, "warning", "Document requires human review",
            "Gemini marked the extraction as low-confidence or identified ambiguous fields.",
            "Review the extracted fields and source document before downstream action.",
            {**evidence_base, "low_confidence_fields": low_conf},
        ))

    return alerts

@router.get("/dashboard")
def dashboard(session: Session = Depends(db)):
    suppliers = session.query(Supplier).all()
    materials = session.query(Material).all()
    orders = session.query(PurchaseOrder).all()
    alerts = session.query(Alert).order_by(Alert.created_at.desc()).all()
    mm = {m.id: m for m in materials}
    sm = {s.id: s for s in suppliers}
    rows = []
    for p in orders:
        m = mm[p.material_id]
        s = sm[p.supplier_id]
        runway = runway_days(m.on_hand, m.in_transit, m.reserved, m.daily_consumption)
        days = max(0, (p.promised_date - datetime.utcnow()).total_seconds() / 86400)
        delay = max(0, (1 - s.on_time_rate) * 7)
        risk = classify_risk(runway, days, delay)
        rows.append({
            "id": p.id, "po_number": p.po_number, "supplier": s.name,
            "material": m.name, "promised_date": p.promised_date.isoformat(),
            "runway_days": None if runway == float("inf") else round(runway, 1),
            "predicted_delay_days": round(delay, 1), "risk": risk,
        })
    return {
        "summary": {
            "suppliers": len(suppliers),
            "materials": len(materials),
            "open_orders": sum(p.status == "open" for p in orders),
            "critical_alerts": sum(a.severity == "critical" and a.status == "pending" for a in alerts),
            "review_alerts": sum(a.status == "pending" for a in alerts),
        },
        "suppliers": [{
            "id": s.id, "name": s.name, "category": s.category,
            "score": supplier_score(s.on_time_rate, s.order_accuracy, s.quality_issues),
            "on_time_rate": s.on_time_rate, "order_accuracy": s.order_accuracy,
            "quality_issues": s.quality_issues,
        } for s in suppliers],
        "orders": rows,
        "alerts": [{
            "id": a.id, "severity": a.severity, "title": a.title,
            "message": a.message, "recommendation": a.recommendation,
            "status": a.status, "evidence": json.loads(a.evidence_json)
        } for a in alerts],
    }

@router.post("/documents/upload")
async def upload_document(file: UploadFile = File(...), session: Session = Depends(db)):
    allowed = {".pdf", ".png", ".jpg", ".jpeg", ".webp", ".csv", ".xlsx", ".xls"}
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed:
        raise HTTPException(400, "Unsupported file type")
    root = Path(os.getenv("UPLOAD_DIR", "./uploads"))
    root.mkdir(parents=True, exist_ok=True)
    name = Path(file.filename).name
    path = root / name
    path.write_bytes(await file.read())

    extracted = await extract_with_provider(str(path))
    document = Document(
        filename=name,
        document_type=extracted.get("document_type", "unknown"),
        confidence=float(extracted.get("confidence", 0)),
        extracted_json=json.dumps(extracted),
    )
    session.add(document)
    session.flush()

    alerts = _reconcile_document(session, document, extracted)
    session.commit()
    session.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "confidence": document.confidence,
        "extracted": extracted,
        "alerts_created": len(alerts),
    }

@router.get("/documents")
def documents(session: Session = Depends(db)):
    rows = session.query(Document).order_by(Document.created_at.desc()).all()
    return [{
        "id": d.id,
        "filename": d.filename,
        "document_type": d.document_type,
        "confidence": d.confidence,
        "extracted": json.loads(d.extracted_json),
        "created_at": d.created_at.isoformat(),
    } for d in rows]

@router.post("/alerts/{alert_id}/decision")
def decision(alert_id: int, payload: DecisionIn, session: Session = Depends(db)):
    if payload.action not in {"approve", "modify", "reject"}:
        raise HTTPException(400, "Invalid action")
    alert = session.get(Alert, alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = payload.action
    session.add(Decision(alert_id=alert_id, action=payload.action, comment=payload.comment))
    session.commit()
    return {"status": "ok", "alert_id": alert_id, "action": payload.action}

@router.post("/demo/refresh")
def refresh(session: Session = Depends(db)):
    session.query(Alert).delete()
    session.commit()
    orders = session.query(PurchaseOrder).all()
    for p in orders:
        m = session.get(Material, p.material_id)
        s = session.get(Supplier, p.supplier_id)
        runway = runway_days(m.on_hand, m.in_transit, m.reserved, m.daily_consumption)
        days = max(0, (p.promised_date - datetime.utcnow()).total_seconds() / 86400)
        delay = max(0, (1 - s.on_time_rate) * 7)
        risk = classify_risk(runway, days, delay)
        if risk != "normal":
            session.add(Alert(
                po_id=p.id,
                severity="critical" if risk == "production-critical" else "warning",
                title=p.po_number + ": " + risk.replace("-", " "),
                message=f"{m.name} has {runway:.1f} days of runway versus {days + delay:.1f} days until predicted arrival.",
                recommendation="Contact supplier for updated ETA and review alternative sourcing if production coverage is insufficient.",
                evidence_json=json.dumps({
                    "po_number": p.po_number,
                    "supplier": s.name,
                    "material": m.name,
                    "runway_days": round(runway, 1),
                    "predicted_delay_days": round(delay, 1),
                    "promised_date": p.promised_date.isoformat(),
                    "risk_method": "rules-first supplier history + inventory runway",
                }),
            ))
    session.commit()
    return {"status": "refreshed"}
