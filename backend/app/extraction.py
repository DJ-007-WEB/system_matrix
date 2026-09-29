import asyncio
import json
import mimetypes
import os
from pathlib import Path
from typing import List, Literal, Optional

from pydantic import BaseModel, Field\nfrom google.genai import types


DocumentType = Literal[
    "po",
    "delivery_note",
    "invoice",
    "quotation",
    "grn",
    "rejection_note",
    "supplier_message",
    "unknown",
]


class LineItem(BaseModel):
    description: str = ""
    quantity: Optional[float] = None
    unit: str = ""
    unit_price: Optional[float] = None


class ExtractedDocument(BaseModel):
    document_type: DocumentType = "unknown"
    po_number: Optional[str] = None
    supplier_name: Optional[str] = None
    promised_delivery_date: Optional[str] = None
    supplier_confirmed_date: Optional[str] = None
    actual_delivery_date: Optional[str] = None
    gstin: Optional[str] = None
    hsn_code: Optional[str] = None
    e_way_bill: Optional[str] = None
    irn: Optional[str] = None
    currency: Optional[str] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    items: List[LineItem] = Field(default_factory=list)
    confidence: float = 0.0
    low_confidence_fields: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


EXTRACTION_PROMPT = """
You are the document-understanding component of SupplyChain Sentinel.

Extract only information explicitly present in the supplied document. Never invent,
infer, or fill missing values. Preserve dates as YYYY-MM-DD where unambiguous.
Classify the document as one of: po, delivery_note, invoice, quotation, grn,
rejection_note, supplier_message, unknown.

Capture purchase-order number, supplier name, promised/supplier-confirmed/actual
delivery dates, GSTIN, HSN code, e-way bill, IRN, currency, financial totals,
and every visible line item with description, quantity, unit, and unit price.

Set confidence from 0 to 1 for the extraction as a whole. Put fields that were
ambiguous, partially visible, or uncertain in low_confidence_fields. Put useful
non-fabricated observations in notes. Missing values must remain null/empty.
"""


def _extract_sync(path: str) -> dict:
    if not os.getenv("GEMINI_API_KEY"):
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "items": [],
            "low_confidence_fields": [],
            "notes": ["GEMINI_API_KEY is not configured"],
            "provider": "none",
        }

    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    file_path = Path(path)
    mime_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"

    # Gemini's multimodal document support is used directly for PDFs/images.
    # CSV/XLSX are converted to compact text so their tabular data is explicit.
    if file_path.suffix.lower() in {".csv", ".xlsx", ".xls"}:
        if file_path.suffix.lower() == ".csv":
            content = file_path.read_text(encoding="utf-8", errors="replace")
        else:
            from openpyxl import load_workbook

            workbook = load_workbook(file_path, read_only=True, data_only=True)
            chunks = []
            for sheet in workbook.worksheets:
                chunks.append(f"[SHEET: {sheet.title}]")
                for row in sheet.iter_rows(values_only=True):
                    values = ["" if value is None else str(value) for value in row]
                    chunks.append(" | ".join(values))
            content = "\n".join(chunks)

        response = client.models.generate_content(
            model=model,
            contents=[EXTRACTION_PROMPT, content],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedDocument.model_json_schema(),
            },
        )
    else:
        uploaded = client.files.upload(file=str(file_path), config={"mime_type": mime_type})
        response = client.models.generate_content(
            model=model,
            contents=[EXTRACTION_PROMPT, uploaded],
            config={
                "response_mime_type": "application/json",
                "response_schema": ExtractedDocument.model_json_schema(),
            },
        )

    result = ExtractedDocument.model_validate_json(response.text)
    payload = result.model_dump()
    payload["provider"] = "gemini"
    payload["model"] = model
    return payload


async def extract_with_provider(path: str) -> dict:
    # google-genai is synchronous; keep blocking SDK work off FastAPI's event loop.
    try:
        return await asyncio.to_thread(_extract_sync, path)
    except Exception as exc:
        return {
            "document_type": "unknown",
            "confidence": 0.0,
            "items": [],
            "low_confidence_fields": [],
            "notes": [f"Gemini extraction failed: {type(exc).__name__}: {exc}"],
            "provider": "gemini",
            "error": True,
        }
