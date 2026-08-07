import urllib.request
import json

def test_api():
    print("Testing Backend API on http://127.0.0.1:8008...")
    
    # 1. Health
    req = urllib.request.urlopen("http://127.0.0.1:8008/health")
    health = json.loads(req.read().decode())
    print("Health:", health)
    
    # 2. Itineraries
    req = urllib.request.urlopen("http://127.0.0.1:8008/api/itineraries")
    itineraries = json.loads(req.read().decode())
    print("Itineraries count:", len(itineraries))
    
    # 3. Trigger Simulation
    sim_data = json.dumps({"preset": "FLIGHT_CANCELLED_JFK", "itinerary_id": "itinerary-1"}).encode('utf-8')
    sim_req = urllib.request.Request("http://127.0.0.1:8008/api/simulate", data=sim_data, headers={"Content-Type": "application/json"})
    sim_res = json.loads(urllib.request.urlopen(sim_req).read().decode())
    print("Simulation result:", sim_res["status"], "| Incident ID:", sim_res["incident_id"], "| Plans:", sim_res["recovery_options_count"])
    
    # 4. Approve plan
    inc_id = sim_res["incident_id"]
    plan_id = f"PLAN-{inc_id}-1"
    app_data = json.dumps({"plan_id": plan_id}).encode('utf-8')
    app_req = urllib.request.Request(f"http://127.0.0.1:8008/api/incidents/{inc_id}/approve_plan", data=app_data, headers={"Content-Type": "application/json"})
    app_res = json.loads(urllib.request.urlopen(app_req).read().decode())
    print("Approval result:", app_res["status"], "| Message:", app_res["message"])

if __name__ == "__main__":
    test_api()
