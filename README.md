# SupplyChain Sentinel

SupplyChain Sentinel is a lightweight procurement-to-production risk system for small manufacturers. It ingests purchase-order and operational documents, extracts structured fields with Gemini, reconciles documents against the purchase-order master, calculates inventory runway and supplier risk, and presents evidence-backed alerts for human review.

## Run locally

1. Create a local `.env` from `.env.example`.
2. Set only the Gemini credential: `GEMINI_API_KEY=...`
3. Start the stack: `docker compose up --build`
4. Open the dashboard at http://localhost:3000
5. API documentation is at http://localhost:8000/docs

No Gemini key is committed to the repository.

## Implemented workflow

- PDF/image/CSV/XLSX upload
- Gemini structured document classification and extraction
- PO number, supplier, delivery dates, GSTIN, HSN, e-way bill, IRN, financial totals and line-item extraction
- Fuzzy supplier entity matching
- PO quantity, unit, price and promised-date reconciliation
- Invoice arithmetic checks
- Low-confidence human-review alerts
- Supplier scorecards
- Inventory runway calculation
- Rules-first delivery-delay estimation from supplier history
- Production-critical risk detection
- Evidence chain attached to every generated alert
- Human approve/modify/reject workflow with decision audit records
- PostgreSQL persistence and Docker Compose deployment

## Architecture

FastAPI + PostgreSQL backend, Gemini document intelligence, React/Next.js dashboard, and Docker Compose for local deployment.
