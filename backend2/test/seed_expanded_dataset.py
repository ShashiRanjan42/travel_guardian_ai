"""Expand wayfare.db with believable, linked test data.

This script is deliberately dependency-free and safe to run more than once: each
table has a fixed target, so it only inserts records that are still missing.

Run from the project root:
    python backend/test/seed_expanded_dataset.py
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4


DB_PATH = Path(__file__).resolve().parents[1] / "wayfare.db"
TARGETS = {
    "users": 30, "travellers": 10, "vendors": 30, "bookings": 470,
    "itineraries": 470, "itinerary_versions": 470, "legs": 520,
    "disruption_events": 50, "impact_assessments": 10, "replan_options": 30,
    "option_legs": 54, "notifications": 10, "traveller_responses": 10,
    "agent_traces": 70, "audit_log": 10,
}

PEOPLE = [
    ("Ananya Mukherjee", "ananya.mukherjee@journeysphere.co", "+91-98310-48219"),
    ("Kabir Malhotra", "kabir.malhotra@journeysphere.co", "+91-98718-30564"),
    ("Nandini Rao", "nandini.rao@journeysphere.co", "+91-98450-77126"),
    ("Vikram Sethi", "vikram.sethi@journeysphere.co", "+91-98103-61482"),
    ("Ishita Banerjee", "ishita.banerjee@journeysphere.co", "+91-99038-19577"),
    ("Arjun Menon", "arjun.menon@journeysphere.co", "+91-98951-42603"),
    ("Tara Khanna", "tara.khanna@journeysphere.co", "+91-98187-53942"),
    ("Dev Patel", "dev.patel@journeysphere.co", "+91-98251-68014"),
    ("Sana Qureshi", "sana.qureshi@journeysphere.co", "+91-98711-24765"),
    ("Neel Joshi", "neel.joshi@journeysphere.co", "+91-99250-31896"),
    ("Rhea Kapoor", "rhea.kapoor@wayfare.in", "+91-98114-75208"),
    ("Siddharth Nair", "siddharth.nair@wayfare.in", "+91-98957-20413"),
    ("Pooja Kulkarni", "pooja.kulkarni@wayfare.in", "+91-98230-61859"),
    ("Farhan Ali", "farhan.ali@wayfare.in", "+91-98734-16520"),
    ("Mitali Shah", "mitali.shah@wayfare.in", "+91-99090-43871"),
    ("Karan Bedi", "karan.bedi@wayfare.in", "+91-98180-97246"),
    ("Leela Krishnan", "leela.krishnan@wayfare.in", "+91-98401-58139"),
    ("Aditya Chawla", "aditya.chawla@wayfare.in", "+91-99996-23085"),
    ("Maya Thomas", "maya.thomas@wayfare.in", "+91-97472-86410"),
    ("Ritesh Bansal", "ritesh.bansal@wayfare.in", "+91-98730-59162"),
    ("Shalini Dutta", "shalini.dutta@wayfare.in", "+91-98306-12548"),
    ("Omar Siddiqui", "omar.siddiqui@wayfare.in", "+91-98192-47630"),
    ("Kavya Iyer", "kavya.iyer@wayfare.in", "+91-98842-36017"),
    ("Manav Arora", "manav.arora@wayfare.in", "+91-98998-75421"),
    ("Priyanka Bose", "priyanka.bose@wayfare.in", "+91-99031-69275"),
    ("Rohit Bhatia", "rohit.bhatia@wayfare.in", "+91-98715-84293"),
    ("Ayesha Mirza", "ayesha.mirza@wayfare.in", "+91-98106-31758"),
]

VENDORS = [
    ("Vistara", "FLIGHT"), ("Air India Express", "FLIGHT"), ("Akasa Air", "FLIGHT"),
    ("SpiceJet", "FLIGHT"), ("Indian Railways", "TRAIN"), ("Vande Bharat Express", "TRAIN"),
    ("Konkan Railway", "TRAIN"), ("KSRTC Airavat", "BUS"), ("RedBus Select", "BUS"),
    ("Zingbus", "BUS"), ("Goa Miles", "CAB"), ("Meru Cabs", "CAB"), ("Savaari", "CAB"),
    ("The Fern Residency", "HOTEL"), ("Lemon Tree Hotels", "HOTEL"),
    ("Taj Fort Aguada Resort", "HOTEL"), ("Zostel", "HOTEL"), ("Jalesh Cruises", "FERRY"),
    ("Mandovi River Cruises", "FERRY"), ("Thrillophilia Experiences", "ACTIVITY"),
    ("Indus Experiences", "ACTIVITY"), ("Nature Trails India", "ACTIVITY"),
    ("Maharashtra State Road Transport", "BUS"), ("Ola Outstation", "CAB"),
    ("MakeMyTrip Activities", "ACTIVITY"), ("Neemrana Hotels", "HOTEL"),
    ("Blue Dart Travel Desk", "CAB"),
]

ROUTES = [
    ("Bengaluru", "Kochi", 12.9716, 77.5946, 9.9312, 76.2673),
    ("Mumbai", "Goa", 19.0760, 72.8777, 15.2993, 74.1240),
    ("Delhi", "Jaipur", 28.6139, 77.2090, 26.9124, 75.7873),
    ("Hyderabad", "Chennai", 17.3850, 78.4867, 13.0827, 80.2707),
    ("Kolkata", "Darjeeling", 22.5726, 88.3639, 27.0410, 88.2663),
    ("Pune", "Udaipur", 18.5204, 73.8567, 24.5854, 73.7125),
    ("Ahmedabad", "Jodhpur", 23.0225, 72.5714, 26.2389, 73.0243),
    ("Chandigarh", "Manali", 30.7333, 76.7794, 32.2432, 77.1892),
]


def uid() -> str:
    return uuid4().hex


def now_text(offset_days: int = 0) -> str:
    return (datetime(2026, 8, 8, 9, 0) + timedelta(days=offset_days)).isoformat(sep=" ")


def add(connection: sqlite3.Connection, table: str, **values: object) -> None:
    columns = ", ".join(f'"{column}"' for column in values)
    placeholders = ", ".join("?" for _ in values)
    connection.execute(f'INSERT INTO "{table}" ({columns}) VALUES ({placeholders})', tuple(values.values()))


def count(connection: sqlite3.Connection, table: str) -> int:
    return connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]


def ids(connection: sqlite3.Connection, table: str) -> list[str]:
    return [row[0] for row in connection.execute(f'SELECT id FROM "{table}"')]


def repair_legacy_seed_data(connection: sqlite3.Connection) -> None:
    """Replace the original placeholder records and repair their one bad relation."""
    connection.execute("UPDATE users SET email = ?, full_name = ? WHERE email = ?", ("rohan.desai@journeysphere.co", "Rohan Desai", "rohan@example.com"))
    connection.execute("UPDATE users SET email = ?, full_name = ? WHERE email = ?", ("aravind.prakash@journeysphere.co", "Aravind Prakash", "noise@example.com"))
    connection.execute("UPDATE travellers SET email = ?, phone = ? WHERE email = ?", ("rohan.desai@journeysphere.co", "+91-98204-61735", "rohan@example.com"))

    placeholder_bookings = connection.execute("SELECT id FROM bookings WHERE pnr LIKE 'NOISE%' ORDER BY pnr").fetchall()
    for index, (booking_id,) in enumerate(placeholder_bookings):
        origin, destination, *_ = ROUTES[index % len(ROUTES)]
        departure = datetime(2025, 2, 3, 9, 0) + timedelta(days=index * 5)
        connection.execute(
            """UPDATE bookings
               SET pnr = ?, origin = ?, destination = ?, start_date = ?, end_date = ?,
                   total_value_inr = ?, non_refundable_value_inr = ?, status = ?
               WHERE id = ?""",
            (f"TG{index + 700000:07d}", origin, destination, departure.isoformat(sep=" "),
             (departure + timedelta(days=4)).isoformat(sep=" "), 16800 + index * 315,
             6100 + (index % 5) * 550, "completed", booking_id),
        )

    # The original assessment references a booking whose itinerary was regenerated.
    connection.execute(
        """UPDATE impact_assessments
           SET itinerary_id = (SELECT id FROM itineraries WHERE booking_id = impact_assessments.booking_id LIMIT 1)
           WHERE itinerary_id NOT IN (SELECT id FROM itineraries)"""
    )


def main() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        repair_legacy_seed_data(conn)

        # Add people first: travel coordinators and customer accounts.
        for index in range(TARGETS["users"] - count(conn, "users")):
            name, email, _ = PEOPLE[index]
            add(conn, "users", id=uid(), email=email, password_hash="demo_password_hash", 
                role="ops_agent" if index % 3 == 0 else "traveller", full_name=name, created_at=now_text(-30 + index))

        user_rows = conn.execute("SELECT id, full_name FROM users WHERE role = 'traveller'").fetchall()
        for index in range(TARGETS["travellers"] - count(conn, "travellers")):
            user_id, user_name = user_rows[index % len(user_rows)]
            person = PEOPLE[index]
            add(conn, "travellers", id=uid(), user_id=user_id, full_name=person[0], phone=person[2], email=person[1],
                is_solo=index % 3 != 0, vulnerability_flag=("mobility_support" if index == 3 else "none"),
                preferences=json.dumps({"seat_preference": "aisle" if index % 2 else "window", "avoid_red_eye": bool(index % 2), "max_cost_delta_inr": 3500 + index * 250}))

        for index in range(TARGETS["vendors"] - count(conn, "vendors")):
            name, mode = VENDORS[index]
            add(conn, "vendors", id=uid(), name=name, type=mode, reliability_score=round(0.79 + (index % 18) / 100, 2),
                supports_modes=json.dumps([mode]), status="operational")

        travellers, operators, flight_vendors = ids(conn, "travellers"), [r[0] for r in conn.execute("SELECT id FROM users WHERE role = 'ops_agent'")], [r[0] for r in conn.execute("SELECT id FROM vendors WHERE type = 'FLIGHT'")]
        new_booking_ids: list[str] = []
        needed_bookings = TARGETS["bookings"] - count(conn, "bookings")
        for index in range(needed_bookings):
            origin, destination, olat, olon, dlat, dlon = ROUTES[index % len(ROUTES)]
            booking_id, itinerary_id, version_id = uid(), uid(), uid()
            departure = datetime(2026, 1, 5, 8, 30) + timedelta(days=index * 2)
            pnr = f"WF{index + 1000000:07d}"
            add(conn, "bookings", id=booking_id, pnr=pnr, traveller_id=travellers[index % len(travellers)], ops_agent_id=operators[index % len(operators)], origin=origin, destination=destination, start_date=departure.isoformat(sep=" "), end_date=(departure + timedelta(days=3 + index % 4)).isoformat(sep=" "), total_value_inr=14500 + (index % 9) * 2800, non_refundable_value_inr=5500 + (index % 6) * 900, status="active" if departure > datetime(2026, 8, 8) else "completed", source="SEEDED")
            add(conn, "itineraries", id=itinerary_id, booking_id=booking_id, current_version=1)
            add(conn, "itinerary_versions", id=version_id, itinerary_id=itinerary_id, version=1, created_by="ops_console", reason="Original confirmed itinerary", triggered_by_alert_id=None, snapshot=json.dumps({"origin": origin, "destination": destination, "pnr": pnr}), created_at=(departure - timedelta(days=14)).isoformat(sep=" "))
            add(conn, "legs", id=uid(), itinerary_version_id=version_id, seq=1, day_index=1, mode="FLIGHT", status="CONFIRMED", title=f"Flight from {origin} to {destination}", vendor_id=flight_vendors[index % len(flight_vendors)], origin_name=origin, origin_lat=olat, origin_lon=olon, dest_name=destination, dest_lat=dlat, dest_lon=dlon, waypoints=json.dumps([]), depart_at=departure.isoformat(sep=" "), arrive_at=(departure + timedelta(hours=2, minutes=15)).isoformat(sep=" "), cost_inr=6200 + (index % 5) * 650, is_refundable=index % 4 != 0, booking_ref=pnr, depends_on_leg_id=None)
            new_booking_ids.append(booking_id)

        # Bring legs to their exact 10x target with hotel stays attached to real itineraries.
        version_ids = ids(conn, "itinerary_versions")
        hotel_vendors = [r[0] for r in conn.execute("SELECT id FROM vendors WHERE type = 'HOTEL'")]
        for index in range(TARGETS["legs"] - count(conn, "legs")):
            version_id = version_ids[index % len(version_ids)]
            add(conn, "legs", id=uid(), itinerary_version_id=version_id, seq=2, day_index=1, mode="HOTEL", status="CONFIRMED", title="Confirmed hotel stay", vendor_id=hotel_vendors[index % len(hotel_vendors)], origin_name="City centre", origin_lat=19.076, origin_lon=72.8777, dest_name="Hotel reception", dest_lat=19.082, dest_lon=72.882, waypoints=json.dumps([]), depart_at=now_text(index), arrive_at=now_text(index + 1), cost_inr=4800 + index * 150, is_refundable=True, booking_ref=f"HTL-{4000 + index}", depends_on_leg_id=None)

        event_specs = [("WEATHER", "Indian Meteorological Department", "Heavy rain advisory affecting airport operations", ["FLIGHT", "CAB"]), ("DELAY", "Airport Operations Control", "Morning departure delays reported at the terminal", ["FLIGHT"]), ("TRAFFIC", "City Traffic Police", "Diversion in place near the intercity approach road", ["BUS", "CAB"]), ("CANCELLATION", "Railway Enquiry Service", "Selected service cancelled for operational reasons", ["TRAIN"]), ("STRIKE", "Port Authority Notice", "Ferry services operating on a reduced timetable", ["FERRY"])]
        for index in range(TARGETS["disruption_events"] - count(conn, "disruption_events")):
            kind, source, headline, modes = event_specs[index % len(event_specs)]
            add(conn, "disruption_events", id=uid(), type=kind, source_name=source, source_url=None, source_reliability=0.82 + (index % 12) / 100, raw_payload=json.dumps({"advisory_id": f"ADV-2026-{index + 501}", "affected_modes": modes}), headline=headline, description=f"{headline}. Operations teams are monitoring updates and will confirm alternatives where needed.", geo_center_lat=19.076 + index / 100, geo_center_lon=72.8777 + index / 100, radius_km=12 + index % 20, affected_modes=json.dumps(modes), start_time=now_text(index), end_time=now_text(index + 1), severity_hint=("HIGH" if index % 5 == 0 else "MEDIUM"), freshness="SYNTHETIC", injection_flagged=False, detected_at=now_text(index))

        event_ids, booking_ids, itinerary_ids, leg_ids = ids(conn, "disruption_events"), ids(conn, "bookings"), ids(conn, "itineraries"), ids(conn, "legs")
        assessment_ids: list[str] = []
        for index in range(TARGETS["impact_assessments"] - count(conn, "impact_assessments")):
            assessment_id, run_id = uid(), str(uuid4())
            add(conn, "impact_assessments", id=assessment_id, event_id=event_ids[index % len(event_ids)], booking_id=booking_ids[-(index + 1)], itinerary_id=itinerary_ids[-(index + 1)], status="OPTIONS_READY", severity="MEDIUM" if index % 2 else "HIGH", severity_score=51.0 + index * 3, severity_breakdown=json.dumps({"impact": 28, "urgency": 16, "vulnerability": 4, "financial": 9}), affected_leg_ids=json.dumps([leg_ids[-(index + 1)]]), cascade_leg_ids=json.dumps([]), impact_summary="A confirmed disruption may affect the planned connection; alternative options have been prepared.", hours_to_departure=18.0 + index, sla_deadline=now_text(index + 1), correlation_confidence=0.84 + index / 100, run_id=run_id, created_at=now_text(index), updated_at=now_text(index))
            assessment_ids.append(assessment_id)

        all_assessments = ids(conn, "impact_assessments")
        option_ids: list[str] = []
        labels = ["Earlier departure", "Alternative carrier", "Flexible next-day route"]
        for index in range(TARGETS["replan_options"] - count(conn, "replan_options")):
            option_id = uid()
            add(conn, "replan_options", id=option_id, assessment_id=all_assessments[index % len(all_assessments)], rank=index % 3 + 1, label=labels[index % 3], summary="A verified alternative with confirmed capacity and a clear arrival estimate.", status="APPROVED" if index % 3 != 2 else "DRAFT", cost_delta_inr=(index % 3) * 950, time_delta_minutes=45 + (index % 3) * 55, risk_score=round(0.16 + (index % 4) * 0.09, 2), confidence=round(0.91 - (index % 4) * 0.04, 2), evidence=json.dumps([{"source": "operations desk", "claim": "capacity confirmed"}]), assumptions=json.dumps(["inventory remains available until the stated expiry"]), tradeoffs="May require an earlier hotel check-out or a modest fare difference.", rejection_reason=None, rejected_by_rule=None, override_reason=None, overridden_by=None, overridden_at=None, approved_by=operators[index % len(operators)], expires_at=now_text(index + 2))
            option_ids.append(option_id)

        for index, option_id in enumerate(option_ids):
            for seq, mode in enumerate(("FLIGHT", "CAB"), start=1):
                add(conn, "option_legs", id=uid(), option_id=option_id, change_type="MODIFIED" if seq == 1 else "ADDED", seq=seq, day_index=1, mode=mode, status="CONFIRMED", title=("Rebooked flight segment" if seq == 1 else "Airport transfer"), vendor_id=flight_vendors[index % len(flight_vendors)], origin_name="Departure terminal", origin_lat=19.076, origin_lon=72.8777, dest_name="Arrival terminal", dest_lat=15.2993, dest_lon=74.124, waypoints=json.dumps([]), depart_at=now_text(index), arrive_at=now_text(index + 1), cost_inr=6400 + seq * 700, is_refundable=True, booking_ref=f"ALT-{7000 + index}")

        all_options = ids(conn, "replan_options")
        all_travellers = ids(conn, "travellers")
        for index in range(TARGETS["notifications"] - count(conn, "notifications")):
            add(conn, "notifications", id=uid(), traveller_id=all_travellers[index % len(all_travellers)], assessment_id=all_assessments[index % len(all_assessments)], channel="whatsapp" if index % 2 else "email", title="Your travel options are ready", body="We identified a possible change to your itinerary and prepared confirmed alternatives for your review.", requires_action=True, sla_deadline=now_text(index + 1), read_at=None, sent_at=now_text(index))
        for index in range(TARGETS["traveller_responses"] - count(conn, "traveller_responses")):
            add(conn, "traveller_responses", id=uid(), assessment_id=all_assessments[index % len(all_assessments)], selected_option_id=all_options[index % len(all_options)], responded_at=now_text(index), response_latency_seconds=240 + index * 37, channel="whatsapp")
        agent_names = ["WATCHER", "CORRELATOR", "SCORER", "REPLANNER", "COMPLIANCE", "COMMUNICATOR", "ORCHESTRATOR"]
        for index in range(TARGETS["agent_traces"] - count(conn, "agent_traces")):
            agent = agent_names[index % len(agent_names)]
            add(conn, "agent_traces", id=uid(), run_id=str(uuid4()), assessment_id=all_assessments[index % len(all_assessments)], agent=agent, seq=index % 7 + 1, status="success", input_summary="Validated disruption and itinerary context.", output_summary=f"{agent.title()} completed its assigned travel-safety check.", reasoning="Used current booking details, supplier availability, and the recorded disruption scope.", confidence=0.89, duration_ms=180 + index * 11, tokens_in=320 + index * 4, tokens_out=140 + index * 3, attempt=1, error=None, started_at=now_text(index), ended_at=now_text(index))
        for index in range(TARGETS["audit_log"] - count(conn, "audit_log")):
            add(conn, "audit_log", id=uid(), actor_type="ops_agent", actor_id=operators[index % len(operators)], action="reviewed_replan", entity_type="impact_assessment", entity_id=all_assessments[index % len(all_assessments)], before=json.dumps({"status": "OPTIONS_READY"}), after=json.dumps({"status": "PENDING_TRAVELLER_RESPONSE"}), metadata=json.dumps({"channel": "ops_console", "reviewer_note": "Options verified against supplier inventory."}), created_at=now_text(index))

        conn.commit()
        print("Dataset expansion complete.")
        for table, target in TARGETS.items():
            print(f"{table}: {count(conn, table)} / target {target}")


if __name__ == "__main__":
    main()
