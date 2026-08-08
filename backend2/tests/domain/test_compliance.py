from app.domain.compliance_rules import evaluate_compliance

def test_compliance_rule_c01_rejection():
    # Mocking Option 3 (Jalori pass)
    option = {
        "label": "Via Jalori",
        "tradeoffs": "High risk due to weather",
    }
    
    result = evaluate_compliance(option, interpreted_risk="HIGH", rule_id="C-01")
    
    assert result["approved"] == False
    assert result["rejection_reason"] == "C-01: active weather advisory zone"
    assert result["rule_id"] == "C-01"

def test_compliance_rule_pass():
    option = {
        "label": "Via Manali"
    }
    
    result = evaluate_compliance(option, interpreted_risk="LOW", rule_id=None)
    
    assert result["approved"] == True
    assert result["rejection_reason"] is None
