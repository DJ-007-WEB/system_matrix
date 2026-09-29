export type Risk = "critical" | "at-risk" | "on-track" | "info";
export type AlertStatus = "pending" | "approved" | "modified" | "rejected";

export const suppliers = [
  { id: "s1", name: "Bharat Fasteners Pvt Ltd", onTime: 72, variance: 2.8, quality: 2, segment: "Bottleneck", score: 68 },
  { id: "s2", name: "Precision Components", onTime: 91, variance: 1.1, quality: 0, segment: "Strategic", score: 89 },
  { id: "s3", name: "Western Steel Works", onTime: 84, variance: 1.7, quality: 1, segment: "Leverage", score: 81 }
];

export const orders = [
  { id: "o1", po: "PO-2291", supplier: "Bharat Fasteners Pvt Ltd", material: "MS Sheet 2mm", promised: "28 Sep", predicted: "04 Oct", runway: 3, delay: 6, risk: "critical" as Risk, value: 184000, status: "Open" },
  { id: "o2", po: "PO-2284", supplier: "Precision Components", material: "Bearing 6204", promised: "30 Sep", predicted: "01 Oct", runway: 9, delay: 1, risk: "at-risk" as Risk, value: 72000, status: "Open" },
  { id: "o3", po: "PO-2278", supplier: "Western Steel Works", material: "CRCA Coil 1.6mm", promised: "02 Oct", predicted: "03 Oct", runway: 14, delay: 1, risk: "on-track" as Risk, value: 312000, status: "Open" },
  { id: "o4", po: "PO-2269", supplier: "Bharat Fasteners Pvt Ltd", material: "Hex Bolt M8", promised: "05 Oct", predicted: "07 Oct", runway: 11, delay: 2, risk: "at-risk" as Risk, value: 46000, status: "Open" }
];

export const alerts = [
  { id: "a1", risk: "critical" as Risk, title: "PO-2291 can stop the sheet-metal line", supplier: "Bharat Fasteners Pvt Ltd", message: "Runway is 3 days while the predicted supplier delay is 6 days.", next: "Ask the supplier for a partial dispatch today and confirm the balance date.", time: "12 min ago" },
  { id: "a2", risk: "at-risk" as Risk, title: "Bearing 6204 is entering the watch window", supplier: "Precision Components", message: "Runway is 9 days against a predicted 1-day delay.", next: "Keep the order under watch; no supplier escalation needed yet.", time: "48 min ago" },
  { id: "a3", risk: "info" as Risk, title: "Invoice received before GRN", supplier: "Western Steel Works", message: "Invoice INV-8842 has no matched goods receipt.", next: "Match the delivery note and GRN before approving payment.", time: "Today" }
];

export const stock = [
  { material: "MS Sheet 2mm", unit: "kg", onHand: 360, transit: 180, reserved: 90, daily: 120, runway: 3.75 },
  { material: "Bearing 6204", unit: "pcs", onHand: 35, transit: 100, reserved: 10, daily: 8, runway: 15.6 },
  { material: "CRCA Coil 1.6mm", unit: "kg", onHand: 820, transit: 500, reserved: 120, daily: 90, runway: 13.3 }
];

export const evidence = [
  { label: "Raw document", detail: "Delivery_Note_PO2291.jpg", confidence: 99 },
  { label: "Extracted field", detail: "Promised date: 28 Sep 2026", confidence: 94 },
  { label: "Supplier history", detail: "72% on-time · 2.8d variance", confidence: 96 },
  { label: "Runway calculation", detail: "3 days vs predicted delay +6 days", confidence: 100 },
  { label: "Recommended action", detail: "Request partial dispatch today", confidence: 91 }
];

export const dashboard = {
  ordersAtRisk: 2,
  productionCritical: 1,
  awaitingApproval: 2,
  onTimeRate: 82,
  weeklyValue: "₹6.14L"
};