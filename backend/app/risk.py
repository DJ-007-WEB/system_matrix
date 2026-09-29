import math
import re
from rapidfuzz import fuzz

def runway_days(on_hand, in_transit, reserved, daily_consumption):
    if daily_consumption <= 0:
        return math.inf
    return max(0, on_hand + in_transit - reserved) / daily_consumption

def supplier_score(on_time_rate, order_accuracy, quality_issues):
    quality = max(0, 1 - min(quality_issues, 10) / 10)
    return round(100 * (0.5 * on_time_rate + 0.3 * order_accuracy + 0.2 * quality), 1)

def classify_risk(runway, days_until_promised, predicted_delay):
    if runway < days_until_promised + predicted_delay:
        return "production-critical"
    if predicted_delay > 0:
        return "warning"
    return "normal"

def normalize_unit(unit):
    value = (unit or "").strip().lower()
    aliases = {
        "kgs": "kg", "kilograms": "kg", "kilogram": "kg",
        "pieces": "pcs", "piece": "pcs", "pc": "pcs",
        "nos": "pcs", "number": "pcs",
        "litres": "l", "liter": "l", "litre": "l",
    }
    return aliases.get(value, value)

def normalize_text(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()

def fuzzy_supplier_match(extracted_name, suppliers, threshold=78):
    if not extracted_name:
        return None, 0
    target = normalize_text(extracted_name)
    best = None
    best_score = 0
    for supplier in suppliers:
        score = fuzz.token_set_ratio(target, normalize_text(supplier.name))
        if score > best_score:
            best, best_score = supplier, score
    return (best, best_score) if best_score >= threshold else (None, best_score)

def financial_check(extracted):
    issues = []
    subtotal = extracted.get("subtotal")
    tax = extracted.get("tax")
    total = extracted.get("total")
    if subtotal is not None and tax is not None and total is not None:
        expected = round(float(subtotal) + float(tax), 2)
        if abs(expected - float(total)) > 0.02:
            issues.append({
                "type": "total_mismatch",
                "expected": expected,
                "document_total": float(total),
            })

    line_total = 0.0
    has_line_prices = False
    for item in extracted.get("items", []):
        if item.get("quantity") is not None and item.get("unit_price") is not None:
            has_line_prices = True
            line_total += float(item.get("quantity") or 0) * float(item.get("unit_price") or 0)
    if has_line_prices and subtotal is not None and abs(line_total - float(subtotal)) > 0.05:
        issues.append({
            "type": "line_subtotal_mismatch",
            "expected": round(line_total, 2),
            "document_subtotal": float(subtotal),
        })
    return issues
