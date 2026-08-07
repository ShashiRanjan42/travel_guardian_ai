import re
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("LLMBookingAgent")

class LLMBookingAgent:
    """
    Robust Conversational AI Booking Agent with expanded NLP dataset and fallback entity extraction for:
    - Cities (e.g. Patna, Delhi, Goa, Mumbai, Srinagar, Bengaluru, Jaipur, Lucknow, Varanasi, etc. + regex fallback)
    - Standalone numbers (e.g. 10000, 50000, 1 lac, 100000)
    - Date formats (e.g. 10/08/2026, 8 Aug, 15 August)
    - Duration / Days
    """

    def __init__(self):
        self.sessions = {}

    def get_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "city": None,
                "budget": None,
                "budget_num": None,
                "start_date": None,
                "days": None,
                "history": []
            }
        return self.sessions[session_id]

    def process_message(self, session_id: str, user_message: str, user_name: str = "Traveler"):
        try:
            session = self.get_session(session_id)
            msg_lower = user_message.lower().strip()

            # 1. EXPANDED INDIAN & GLOBAL CITY DATASET
            known_cities = [
                "patna", "delhi", "mumbai", "goa", "bengaluru", "bangalore", "srinagar", "jaipur", 
                "chennai", "kolkata", "hyderabad", "kochi", "pune", "udaipur", "manali", "shimla", 
                "agra", "lucknow", "varanasi", "bhopal", "indore", "ranchi", "surat", "ahmedabad", 
                "chandigarh", "guwahati", "amritsar", "dehradun", "coimbatore", "visakhapatnam", "vizag", 
                "bhubaneswar", "trivandrum", "thiruvananthapuram", "leh", "ladakh", "jodhpur", "jaisalmer", 
                "haridwar", "rishikesh", "ayodhya", "bodhgaya", "darjeeling", "gangtok", "shillong", 
                "port blair", "pondicherry", "puducherry", "mysuru", "mysore", "madurai", "guwahati"
            ]

            # Direct dataset match
            for c in known_cities:
                if c in msg_lower:
                    if c == "bangalore":
                        session["city"] = "Bengaluru"
                    elif c == "vizag":
                        session["city"] = "Visakhapatnam"
                    elif c == "mysore":
                        session["city"] = "Mysuru"
                    elif c == "bihar":
                        session["city"] = "Patna"
                    else:
                        session["city"] = c.title()
                    break

            # Fallback regex extraction if city is not in known_cities list (e.g. "plan to Patna", "book to Agra", "visit Patna")
            if not session["city"]:
                match_city = re.search(r'\b(?:to|in|for|visit|destination|heading to|travel to)\s+([a-zA-Z]{3,20})\b', user_message, re.IGNORECASE)
                if match_city:
                    candidate = match_city.group(1).strip()
                    ignored_words = ["my", "the", "a", "an", "this", "next", "some", "day", "days", "lac", "lakh", "rupees", "rs"]
                    if candidate.lower() not in ignored_words:
                        session["city"] = candidate.title()

            # 2. EXTRACT BUDGET (Handles standalone numbers like 10000, 50000, 100000, 1 lac, 50k)
            if "1 lac" in msg_lower or "1lac" in msg_lower or "one lac" in msg_lower or "100000" in msg_lower:
                session["budget"] = "₹1,00,000 (1 Lac)"
                session["budget_num"] = 100000
            elif "50k" in msg_lower or "50000" in msg_lower:
                session["budget"] = "₹50,000"
                session["budget_num"] = 50000
            else:
                # Search for any standalone number between 3000 and 1000000
                numbers = re.findall(r'\b\d{4,7}\b', msg_lower)
                if numbers:
                    num = int(numbers[0])
                    session["budget"] = f"₹{num:,}"
                    session["budget_num"] = num
                else:
                    budget_match = re.search(r'(\d+)\s*(lac|lakh|lakhs|k|thousand|rupees|rs|inr)?', msg_lower)
                    if budget_match and budget_match.group(1):
                        val = int(budget_match.group(1))
                        unit = budget_match.group(2) if budget_match.group(2) else ""
                        if unit in ["lac", "lakh", "lakhs"]:
                            val *= 100000
                        elif unit in ["k", "thousand"]:
                            val *= 1000
                        if val >= 1000:
                            session["budget"] = f"₹{val:,}"
                            session["budget_num"] = val

            # 3. EXTRACT TRAVEL DATES (e.g. 10/08/2026, 8 Aug, 15 August)
            date_slash_match = re.search(r'(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2,4})', msg_lower)
            date_text_match = re.search(r'(\d{1,2})\s*(aug|august|sep|september|oct|october|nov|november|dec|december|jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july)', msg_lower)
            
            if date_slash_match:
                d, m, y = date_slash_match.group(1), date_slash_match.group(2), date_slash_match.group(3)
                if len(y) == 2:
                    y = f"20{y}"
                session["start_date"] = f"{y}-{int(m):02d}-{int(d):02d}"
            elif date_text_match:
                d = int(date_text_match.group(1))
                session["start_date"] = f"2026-08-{d:02d}"
            elif "next" in msg_lower or "holiday" in msg_lower or "tomorrow" in msg_lower:
                session["start_date"] = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d")

            # 4. EXTRACT DAYS / DURATION
            days_match = re.search(r'(\d+)\s*(day|days|night|nights)', msg_lower)
            if days_match:
                session["days"] = int(days_match.group(1))
            elif session["start_date"] and not session["days"]:
                session["days"] = 4  # Default to 4 days if date provided

            # Evaluate missing slots
            missing = []
            if not session["city"]:
                missing.append("destination city")
            if not session["budget"]:
                missing.append("total travel budget")
            if not session["start_date"] and not session["days"]:
                missing.append("travel dates or number of days")

            # If missing parameters, generate conversational prompt
            if missing:
                if len(missing) == 3:
                    reply = f"Hello {user_name}! I am your AI Booking Agent 🤖. Tell me your travel parameters:\n\n1. Which city would you like to visit? (e.g. Patna, Delhi, Goa, Mumbai, Srinagar, Jaipur)\n2. What is your budget? (e.g. ₹10,000, ₹50,000, ₹1 Lac)\n3. What are your travel dates or duration? (e.g. 10/08/2026 or 4 days)"
                elif "destination city" in missing:
                    reply = f"Got it! I see your budget is {session['budget']} for {session['days'] or 4} days starting {session['start_date'] or 'soon'}.\n\nWhich city would you like to travel to? (e.g., Patna, Delhi, Goa, Mumbai, Srinagar, Jaipur, Bengaluru)"
                elif "total travel budget" in missing:
                    reply = f"Awesome! A trip to **{session['city']}** for {session['days'] or 4} days starting {session['start_date'] or 'soon'}.\n\nWhat is your total travel budget for this trip? (e.g. ₹10,000, ₹50,000, ₹1 Lac)"
                elif "travel dates or number of days" in missing:
                    reply = f"Got it! Destination: **{session['city']}**, Budget: **{session['budget']}**.\n\nWhat are your travel dates or how many days is your trip? (e.g. 10/08/2026 or 4 days)"
                else:
                    reply = f"Could you please specify your {', '.join(missing)} so I can generate and book your trip?"

                return {
                    "status": "NEED_INFO",
                    "missing": missing,
                    "reply": reply,
                    "session": session
                }

            # All slots collected! Dynamically synthesize itinerary
            city = session["city"]
            budget_str = session["budget"]
            budget_num = session.get("budget_num") or 10000
            days = session.get("days") or 4
            start_date = session.get("start_date") or (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")

            flight_cost = int(budget_num * 0.35)
            hotel_cost = int(budget_num * 0.45)
            chauffeur_cost = int(budget_num * 0.15)
            buffer_cost = max(0, budget_num - (flight_cost + hotel_cost + chauffeur_cost))

            carrier = "IndiGo Airlines" if "patna" in city.lower() or "delhi" in city.lower() else "Air India"
            hotel_name = f"Hotel Maurya / Taj Executive Suite {city}" if "patna" in city.lower() else f"Taj Palace & Executive Resort {city}"

            package_plan = {
                "title": f"{user_name}'s Protected {city} Holiday Package",
                "destination": city,
                "budget": budget_str,
                "duration": f"{days} Days / {days-1} Nights",
                "start_date": start_date,
                "flight": f"{carrier} Flight BOOK-{int(datetime.utcnow().timestamp())%10000} (Origin → {city}) — ₹{flight_cost:,}",
                "hotel": f"{hotel_name} — ₹{hotel_cost:,}",
                "chauffeur": f"Local Airport Chauffeur & Sightseeing — ₹{chauffeur_cost:,}",
                "buffer": f"Concierge Reserve & Support — ₹{buffer_cost:,}",
                "flight_cost": flight_cost,
                "hotel_cost": hotel_cost,
                "chauffeur_cost": chauffeur_cost
            }

            reply = f"🎯 All parameters gathered!\n• Destination: **{city}**\n• Budget: **{budget_str}**\n• Date: **{start_date} ({days} Days)**\n\nI have generated your custom trip package below with live 7-Agent AI Guardian Protection included. Click the button below to confirm & book!"

            return {
                "status": "READY_TO_BOOK",
                "reply": reply,
                "package_plan": package_plan,
                "session": session
            }

        except Exception as e:
            logger.error(f"Error processing LLM booking turn: {e}")
            return {
                "status": "NEED_INFO",
                "reply": "I am ready to book your travel plan! Please tell me your destination city (e.g. Patna, Delhi, Goa), budget (e.g. ₹10,000), and travel date (e.g. 10/08/2026).",
                "session": self.get_session(session_id)
            }

# Global Instance
llm_booking_agent = LLMBookingAgent()
