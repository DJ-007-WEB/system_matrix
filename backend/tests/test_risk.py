from app.risk import classify_risk, financial_check, fuzzy_supplier_match, runway_days

class Supplier:
    def __init__(self, name):
        self.name = name

def test_runway():
    assert runway_days(450, 300, 100, 120) == 650 / 120

def test_production_critical():
    assert classify_risk(2, 3, 2) == "production-critical"

def test_financial_mismatch():
    result = financial_check({
        "subtotal": 100,
        "tax": 18,
        "total": 130,
        "items": [{"quantity": 1, "unit_price": 100}],
    })
    assert any(x["type"] == "total_mismatch" for x in result)

def test_supplier_fuzzy_match():
    supplier, score = fuzzy_supplier_match("ABC Metals Pvt. Ltd", [Supplier("ABC Metals Pvt Ltd")])
    assert supplier is not None
    assert score >= 78
