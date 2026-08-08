from typing import Dict, Any, List

def evaluate_compliance(option: Dict[str, Any], interpreted_risk: str, rule_id: str) -> Dict[str, Any]:
    # In a full engine, we'd iterate over all rules and apply them.
    # Here, we specifically mock the rule interpretation from the LLM.
    
    if interpreted_risk == "HIGH" and rule_id == "C-01":
        return {
            "approved": False,
            "rejection_reason": "C-01: active weather advisory zone",
            "rule_id": "C-01"
        }
        
    # Example logic for other rules
    # C-02: Exceeds cost limit
    # C-03: ...
    
    return {
        "approved": True,
        "rejection_reason": None,
        "rule_id": None
    }
