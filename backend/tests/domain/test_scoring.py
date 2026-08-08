from app.domain.scoring import calculate_severity

def test_scoring_high_severity():
    result = calculate_severity(
        impact_score=28,
        hours_to_departure=14.2,  # urgency = 24
        vulnerability_flag="solo", # vulnerability = 5
        financial_exposure_inr=16400 # financial = 10
    )
    
    assert result["score"] == 67.0
    assert result["label"] == "HIGH"
    assert result["breakdown"]["impact"] == 28.0
    assert result["breakdown"]["urgency"] == 24.0
    assert result["breakdown"]["vulnerability"] == 5.0
    assert result["breakdown"]["financial"] == 10.0

def test_scoring_critical_severity():
    result = calculate_severity(
        impact_score=35,
        hours_to_departure=5,  # urgency = 30
        vulnerability_flag="medical", # vulnerability = 20
        financial_exposure_inr=25000 # financial = 15
    )
    
    assert result["score"] == 100.0
    assert result["label"] == "CRITICAL"
