# SupplyChain Sentinel — Frontend design system

## Aesthetic direction

**Warm-industrial control room:** paper-like off-white surfaces, ink-dark typography, one deep ink-green primary, and semantic risk colors used only for operational meaning.  
**Calm precision:** generous whitespace, hairline borders, soft layered shadows, blueprint-grid texture, and restrained 150–300ms motion.

## Design tokens

- Warm neutral: paper #F5F2EA, panel #FAF8F3, ink #272F2B, muted #676F69, line #D6D3C9
- Primary: deep ink-green #2C4C43
- Critical: brick red #A64339
- At risk: amber #B27727
- On track: muted green #4F715B
- Info: slate #5B6971
- Typography: Georgia/display face for headlines and large numbers; system sans for UI/body; tabular numerals for operational data
- Spacing: 8px base grid
- Radius: 12px controls, 16px cards, full pills
- Motion: 150–300ms eased transitions; reduced-motion media query disables animation
- Accessibility: visible focus rings, semantic labels, 44px minimum interactive targets, risk meaning is paired with labels/icons

## Frontend structure

- app/page.tsx — public landing page
- app/login, signup, forgot-password, reset-success — authentication journeys
- app/onboarding — 3-step first-run setup
- app/dashboard — owner control room
- app/alerts/[id] — evidence-backed alert decision
- app/review — low-confidence human review
- app/orders — PO/document reconciliation
- app/suppliers — scorecards and duplicate merge
- app/stock — runway and what-if simulation
- app/capture — mobile-first delivery-note capture
- app/settings — notification, integration and AI/privacy controls
- components/ui.tsx — Button, Input, Card, AlertCard, EvidenceChain, RunwayBar, ConfidenceBadge, StatusPill, Modal, Toast, EmptyState, DataTable, AppShell
- components/performance-chart.tsx — Recharts operational trend
- lib/fixtures.ts — typed mock data, intentionally easy to replace with FastAPI calls
- lib/utils.ts — class merging helper

## Five premium design decisions

1. Criticality controls visual volume. Only production-critical alerts get the strongest border, icon treatment and brick-red signal. Quiet issues remain readable without shouting.
2. Evidence is a first-class object. Alert cards lead into a numbered evidence chain rather than a generic AI explanation, making every recommendation traceable.
3. Factory language replaces startup language. Copy uses runway, PO, GRN, dispatch, supplier history and line impact rather than abstract AI terminology.
4. One control surface, many depths. The owner sees the answer first; drilling into an alert reveals the document, confidence, supplier history, calculation and audit log without changing mental context.
5. Warm material system + restrained geometry. Paper tones, hairline borders, blueprint texture and a single primary color create an industrial instrument feel without gradients or glassmorphism.
