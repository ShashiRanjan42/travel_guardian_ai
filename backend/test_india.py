import urllib.request
import json

def test_india_app():
    print("Testing Travel Guardian AI India API...")
    
    # 1. Login test
    login_data = json.dumps({"email": "ops@guardian.ai", "password": "admin"}).encode('utf-8')
    req = urllib.request.Request("http://127.0.0.1:8008/api/auth/login", data=login_data, headers={"Content-Type": "application/json"})
    user_res = json.loads(urllib.request.urlopen(req).read().decode())
    print("Ops Login Success:", user_res["user"]["name"], "| Role:", user_res["user"]["role"])
    
    # 2. Get sorted itineraries
    req = urllib.request.urlopen("http://127.0.0.1:8008/api/itineraries")
    itineraries = json.loads(req.read().decode())
    print(f"Fetched {len(itineraries)} Indian customer itineraries.")
    print("Top 3 High Risk Customers:")
    for it in itineraries[:3]:
        print(f"  - [{it['risk_level']} {it['risk_score']}%] {it['customer']['name']} ({it['title']})")
        
    # 3. Simulate Monsoon in Mumbai
    sim_data = json.dumps({"preset": "MONSOON_MUMBAI_BOM", "itinerary_id": itineraries[0]["id"]}).encode('utf-8')
    sim_req = urllib.request.Request("http://127.0.0.1:8008/api/simulate", data=sim_data, headers={"Content-Type": "application/json"})
    sim_res = json.loads(urllib.request.urlopen(sim_req).read().decode())
    print("\nSimulation Trigger:", sim_res["preset_applied"], "| Incident:", sim_res["incident_id"])

if __name__ == "__main__":
    test_india_app()
