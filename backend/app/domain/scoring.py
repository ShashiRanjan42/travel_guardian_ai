from typing import Dict, Any

def calculate_severity(
    impact_score: float, # 0 to 35
    hours_to_departure: float,
    vulnerability_flag: str,
    financial_exposure_inr: float
) -> Dict[str, Any]:
    
    # Impact (0-35)
    impact = min(35.0, max(0.0, impact_score))
    
    # Urgency (0-30)
    # < 12h = 30, 12-24h = 24, 24-48h = 15, >48h = 5
    if hours_to_departure < 12:
        urgency = 30.0
    elif hours_to_departure <= 24:
        urgency = 24.0
    elif hours_to_departure <= 48:
        urgency = 15.0
    else:
        urgency = 5.0
        
    # Vulnerability (0-20)
    # e.g., 'none': 0, 'solo': 5, 'elderly': 15, 'medical': 20
    vulnerability_flag = vulnerability_flag.lower()
    if vulnerability_flag == 'medical':
        vulnerability = 20.0
    elif vulnerability_flag == 'elderly':
        vulnerability = 15.0
    elif 'solo' in vulnerability_flag:
        vulnerability = 5.0
    else:
        vulnerability = 0.0
        
    # Financial (0-15)
    # > 20000 = 15, > 10000 = 10, > 5000 = 5, else 0
    if financial_exposure_inr > 20000:
        financial = 15.0
    elif financial_exposure_inr > 10000:
        financial = 10.0
    elif financial_exposure_inr > 5000:
        financial = 5.0
    else:
        financial = 0.0
        
    total_score = impact + urgency + vulnerability + financial
    
    if total_score >= 80:
        label = "CRITICAL"
    elif total_score >= 60:
        label = "HIGH"
    elif total_score >= 30:
        label = "MEDIUM"
    else:
        label = "LOW"
        
    return {
        "score": total_score,
        "label": label,
        "breakdown": {
            "impact": impact,
            "urgency": urgency,
            "vulnerability": vulnerability,
            "financial": financial
        }
    }
