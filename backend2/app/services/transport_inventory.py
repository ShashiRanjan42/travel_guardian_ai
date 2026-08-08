import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "travel_guardian.db")

FLIGHTS_DATA = [
    {"id": "f101", "carrier": "IndiGo Airlines", "code": "6E-204", "origin": "Delhi (DEL)", "destination": "Mumbai (BOM)", "departure": "08:00 AM", "arrival": "10:15 AM", "duration": "2h 15m", "price": 4500, "seats": 14},
    {"id": "f102", "carrier": "Air India", "code": "AI-802", "origin": "Delhi (DEL)", "destination": "Mumbai (BOM)", "departure": "11:30 AM", "arrival": "01:45 PM", "duration": "2h 15m", "price": 5200, "seats": 8},
    {"id": "f103", "carrier": "Vistara", "code": "UK-945", "origin": "Delhi (DEL)", "destination": "Mumbai (BOM)", "departure": "05:40 PM", "arrival": "08:00 PM", "duration": "2h 20m", "price": 6100, "seats": 5},
    {"id": "f104", "carrier": "Akasa Air", "code": "QP-1102", "origin": "Delhi (DEL)", "destination": "Mumbai (BOM)", "departure": "09:15 PM", "arrival": "11:30 PM", "duration": "2h 15m", "price": 4100, "seats": 22},
    {"id": "f105", "carrier": "IndiGo Airlines", "code": "6E-551", "origin": "Delhi (DEL)", "destination": "Goa (GOI)", "departure": "07:10 AM", "arrival": "09:40 AM", "duration": "2h 30m", "price": 5800, "seats": 18},
    {"id": "f106", "carrier": "Air India", "code": "AI-702", "origin": "Delhi (DEL)", "destination": "Goa (GOI)", "departure": "10:20 AM", "arrival": "01:00 PM", "duration": "2h 40m", "price": 7200, "seats": 9},
    {"id": "f107", "carrier": "IndiGo Airlines", "code": "6E-308", "origin": "Mumbai (BOM)", "destination": "Bengaluru (BLR)", "departure": "06:30 AM", "arrival": "08:15 AM", "duration": "1h 45m", "price": 3900, "seats": 30},
    {"id": "f108", "carrier": "Vistara", "code": "UK-815", "origin": "Mumbai (BOM)", "destination": "Bengaluru (BLR)", "departure": "02:00 PM", "arrival": "03:45 PM", "duration": "1h 45m", "price": 4800, "seats": 12},
    {"id": "f109", "carrier": "Air India", "code": "AI-540", "origin": "Chennai (MAA)", "destination": "Delhi (DEL)", "departure": "06:00 AM", "arrival": "08:45 AM", "duration": "2h 45m", "price": 5400, "seats": 16},
    {"id": "f110", "carrier": "IndiGo Airlines", "code": "6E-902", "origin": "Kolkata (CCU)", "destination": "Delhi (DEL)", "departure": "08:30 AM", "arrival": "11:00 AM", "duration": "2h 30m", "price": 4900, "seats": 25},
    # PATNA FLIGHTS DATASET
    {"id": "f111", "carrier": "IndiGo Airlines", "code": "6E-618", "origin": "Delhi (DEL)", "destination": "Patna (PAT)", "departure": "07:30 AM", "arrival": "09:10 AM", "duration": "1h 40m", "price": 4200, "seats": 20},
    {"id": "f112", "carrier": "Air India", "code": "AI-409", "origin": "Delhi (DEL)", "destination": "Patna (PAT)", "departure": "01:15 PM", "arrival": "02:55 PM", "duration": "1h 40m", "price": 4900, "seats": 15},
    {"id": "f113", "carrier": "IndiGo Airlines", "code": "6E-212", "origin": "Mumbai (BOM)", "destination": "Patna (PAT)", "departure": "10:00 AM", "arrival": "12:35 PM", "duration": "2h 35m", "price": 5600, "seats": 12},
    {"id": "f114", "carrier": "Vistara", "code": "UK-715", "origin": "Bengaluru (BLR)", "destination": "Patna (PAT)", "departure": "04:30 PM", "arrival": "07:05 PM", "duration": "2h 35m", "price": 6300, "seats": 10}
]

HOTELS_DATA = [
    {"id": "h201", "name": "Taj Mahal Palace & Resort", "city": "Mumbai (Taj Mahal Palace)", "room": "Deluxe Sea View Suite", "price": 14500, "rating": "5.0 ★", "amenities": ["Free Breakfast", "Airport Shuttle", "Sea View Pool"]},
    {"id": "h202", "name": "The Leela Executive Palace", "city": "Mumbai (Taj Mahal Palace)", "room": "Premier Executive King", "price": 12800, "rating": "4.9 ★", "amenities": ["Spa Access", "Club Lounge", "High Speed Wifi"]},
    {"id": "h203", "name": "Marriott Grand Hotel", "city": "Mumbai (Taj Mahal Palace)", "room": "Club Suite with Breakfast", "price": 9500, "rating": "4.8 ★", "amenities": ["Fitness Center", "Infinity Pool"]},
    {"id": "h204", "name": "The Leela Palace Bengaluru", "city": "Bengaluru (Leela Palace)", "room": "Royal Garden Suite", "price": 16200, "rating": "5.0 ★", "amenities": ["Butler Service", "Golf Course", "Airport Limousine"]},
    {"id": "h205", "name": "ITC Grand Chola Luxury Collection", "city": "Chennai (ITC Grand Chola)", "room": "Executive Club Suite", "price": 11500, "rating": "4.9 ★", "amenities": ["10 Dining Outlets", "Royal Spa"]},
    {"id": "h206", "name": "Rambagh Heritage Palace", "city": "Jaipur (Rambagh Palace)", "room": "Maharaja Royal Suite", "price": 28000, "rating": "5.0 ★", "amenities": ["Vintage Car Transfer", "Royal Banquet"]},
    {"id": "h207", "name": "The Oberoi Grand Heritage", "city": "Kolkata (The Oberoi Grand)", "room": "Luxury Colonial Suite", "price": 13500, "rating": "4.9 ★", "amenities": ["Colonial Tea Lounge", "Poolside Bistro"]},
    # PATNA HOTELS DATASET
    {"id": "h208", "name": "Hotel Maurya Patna Heritage", "city": "Patna (Hotel Maurya)", "room": "Presidential Luxury Suite", "price": 8500, "rating": "4.9 ★", "amenities": ["Ganges Garden Lounge", "Free Airport Transfer", "Buffet Breakfast"]},
    {"id": "h209", "name": "Lemon Tree Premier Patna", "city": "Patna (Lemon Tree)", "room": "Executive Premier Room", "price": 6800, "rating": "4.8 ★", "amenities": ["Rooftop Pool", "Fitness Center"]},
    {"id": "h210", "name": "Taj City Resort Patna", "city": "Patna (Taj City)", "room": "Royal Deluxe King", "price": 11200, "rating": "5.0 ★", "amenities": ["VIP Butler", "Spa & Wellness"]}
]

TRAINS_DATA = [
    {"id": "t301", "name": "Vande Bharat Express", "code": "20902", "origin": "New Delhi (NDLS)", "destination": "Mumbai CSMT", "departure": "06:00 AM", "arrival": "01:25 PM", "duration": "7h 25m", "price": 1950, "class_name": "Executive EC"},
    {"id": "t302", "name": "Tejas Rajdhani Express", "code": "12952", "origin": "New Delhi (NDLS)", "destination": "Mumbai CSMT", "departure": "04:55 PM", "arrival": "08:35 AM (+1)", "duration": "15h 40m", "price": 2850, "class_name": "1st AC (1A)"},
    {"id": "t303", "name": "August Kranti Rajdhani", "code": "12954", "origin": "New Delhi (NDLS)", "destination": "Mumbai CSMT", "departure": "05:15 PM", "arrival": "10:05 AM (+1)", "duration": "16h 50m", "price": 2400, "class_name": "2nd AC (2A)"},
    {"id": "t304", "name": "Kacheguda Express", "code": "12786", "origin": "Bengaluru City (SBC)", "destination": "Hyderabad Deccan", "departure": "06:20 PM", "arrival": "05:40 AM (+1)", "duration": "11h 20m", "price": 1650, "class_name": "3rd AC (3A)"},
    {"id": "t305", "name": "Shatabdi Express", "code": "12008", "origin": "Bengaluru City (SBC)", "destination": "Chennai Central (MAS)", "departure": "04:20 PM", "arrival": "09:30 PM", "duration": "5h 10m", "price": 1250, "class_name": "Chair Car (CC)"},
    # PATNA TRAINS DATASET
    {"id": "t306", "name": "Patna Tejas Rajdhani Express", "code": "12310", "origin": "New Delhi (NDLS)", "destination": "Patna Junction (PNBE)", "departure": "05:10 PM", "arrival": "05:15 AM (+1)", "duration": "12h 05m", "price": 2450, "class_name": "1st AC (1A)"},
    {"id": "t307", "name": "Patna Vande Bharat Express", "code": "22348", "origin": "Patna Junction (PNBE)", "destination": "Howrah / New Delhi", "departure": "05:30 AM", "arrival": "01:00 PM", "duration": "7h 30m", "price": 1750, "class_name": "Executive EC"}
]

BUSES_DATA = [
    {"id": "b401", "operator": "Volvo Multi-Axle AC Sleeper", "code": "VB-101", "origin": "Delhi (ISBT Kashmiri Gate)", "destination": "Jaipur (Sindhi Camp)", "departure": "09:00 PM", "arrival": "05:30 AM (+1)", "duration": "8h 30m", "price": 1250},
    {"id": "b402", "operator": "IntrCity SmartBus EV Premium", "code": "EV-808", "origin": "Delhi (ISBT Kashmiri Gate)", "destination": "Jaipur (Sindhi Camp)", "departure": "10:30 PM", "arrival": "06:45 AM (+1)", "duration": "8h 15m", "price": 1450},
    {"id": "b403", "operator": "Zingbus Luxury AC Sleeper", "code": "ZB-303", "origin": "Delhi (ISBT Kashmiri Gate)", "destination": "Manali (Mall Road Stand)", "departure": "07:30 PM", "arrival": "08:00 AM (+1)", "duration": "12h 30m", "price": 1850},
    {"id": "b404", "operator": "Neeta Travels Volvo B11R", "code": "NT-505", "origin": "Mumbai (Dadar Volvo Bus Stand)", "destination": "Goa (Panjim Bus Terminal)", "departure": "06:00 PM", "arrival": "07:00 AM (+1)", "duration": "13h 00m", "price": 1650},
    # PATNA BUSES DATASET
    {"id": "b405", "operator": "Bihar State Volvo AC Sleeper", "code": "BS-909", "origin": "Delhi (ISBT Kashmiri Gate)", "destination": "Patna (Bairiya Bus Stand)", "departure": "04:00 PM", "arrival": "08:30 AM (+1)", "duration": "16h 30m", "price": 1550}
]

def init_inventory_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS inventory_flights")
    cursor.execute("DROP TABLE IF EXISTS inventory_hotels")
    cursor.execute("DROP TABLE IF EXISTS inventory_trains")
    cursor.execute("DROP TABLE IF EXISTS inventory_buses")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_flights (
            id TEXT PRIMARY KEY,
            carrier TEXT,
            code TEXT,
            origin TEXT,
            destination TEXT,
            departure TEXT,
            arrival TEXT,
            duration TEXT,
            price INTEGER,
            seats INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_hotels (
            id TEXT PRIMARY KEY,
            name TEXT,
            city TEXT,
            room TEXT,
            price INTEGER,
            rating TEXT,
            amenities TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_trains (
            id TEXT PRIMARY KEY,
            name TEXT,
            code TEXT,
            origin TEXT,
            destination TEXT,
            departure TEXT,
            arrival TEXT,
            duration TEXT,
            price INTEGER,
            class_name TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory_buses (
            id TEXT PRIMARY KEY,
            operator TEXT,
            code TEXT,
            origin TEXT,
            destination TEXT,
            departure TEXT,
            arrival TEXT,
            duration TEXT,
            price INTEGER
        )
    ''')

    # Seed data
    for f in FLIGHTS_DATA:
        cursor.execute("INSERT INTO inventory_flights VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (f["id"], f["carrier"], f["code"], f["origin"], f["destination"], f["departure"], f["arrival"], f["duration"], f["price"], f["seats"]))

    for h in HOTELS_DATA:
        cursor.execute("INSERT INTO inventory_hotels VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (h["id"], h["name"], h["city"], h["room"], h["price"], h["rating"], json.dumps(h["amenities"])))

    for t in TRAINS_DATA:
        cursor.execute("INSERT INTO inventory_trains VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (t["id"], t["name"], t["code"], t["origin"], t["destination"], t["departure"], t["arrival"], t["duration"], t["price"], t["class_name"]))

    for b in BUSES_DATA:
        cursor.execute("INSERT INTO inventory_buses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (b["id"], b["operator"], b["code"], b["origin"], b["destination"], b["departure"], b["arrival"], b["duration"], b["price"]))

    conn.commit()
    conn.close()

def search_flights(origin: str = None, destination: str = None):
    init_inventory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT id, carrier, code, origin, destination, departure, arrival, duration, price, seats FROM inventory_flights"
    params = []
    conditions = []
    
    if origin:
        conditions.append("origin LIKE ?")
        params.append(f"%{origin.split('(')[0].strip()}%")
    if destination:
        conditions.append("destination LIKE ?")
        params.append(f"%{destination.split('(')[0].strip()}%")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Fallback to all flights if no exact match
    if not rows:
        cursor.execute("SELECT id, carrier, code, origin, destination, departure, arrival, duration, price, seats FROM inventory_flights")
        rows = cursor.fetchall()

    conn.close()
    
    return [
        {
            "id": r[0],
            "carrier": r[1],
            "code": r[2],
            "origin": r[3],
            "destination": r[4],
            "departure": r[5],
            "arrival": r[6],
            "duration": r[7],
            "price": f"₹{r[8]:,}",
            "seats": r[9]
        }
        for r in rows
    ]

def search_hotels(city: str = None):
    init_inventory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT id, name, city, room, price, rating, amenities FROM inventory_hotels"
    params = []
    
    if city:
        query += " WHERE city LIKE ?"
        params.append(f"%{city.split('(')[0].strip()}%")
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    if not rows:
        cursor.execute("SELECT id, name, city, room, price, rating, amenities FROM inventory_hotels")
        rows = cursor.fetchall()

    conn.close()
    
    return [
        {
            "id": r[0],
            "name": r[1],
            "city": r[2],
            "room": r[3],
            "price": f"₹{r[4]:,} / night",
            "rating": r[5],
            "amenities": json.loads(r[6]) if r[6] else []
        }
        for r in rows
    ]

def search_trains(origin: str = None, destination: str = None):
    init_inventory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, code, origin, destination, departure, arrival, duration, price, class_name FROM inventory_trains")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "name": r[1],
            "code": r[2],
            "origin": r[3],
            "destination": r[4],
            "departure": r[5],
            "arrival": r[6],
            "duration": r[7],
            "price": f"₹{r[8]:,}",
            "class": r[9]
        }
        for r in rows
    ]

def search_buses(origin: str = None, destination: str = None):
    init_inventory_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, operator, code, origin, destination, departure, arrival, duration, price FROM inventory_buses")
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": r[0],
            "operator": r[1],
            "code": r[2],
            "origin": r[3],
            "destination": r[4],
            "departure": r[5],
            "arrival": r[6],
            "duration": r[7],
            "price": f"₹{r[8]:,}"
        }
        for r in rows
    ]
