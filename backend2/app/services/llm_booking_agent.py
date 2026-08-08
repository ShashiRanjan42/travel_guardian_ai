import json
import logging
from datetime import datetime, timedelta
from app.integrations.llm.openai_responses import OpenAIResponsesClient

logger = logging.getLogger("LLMBookingAgent")

class LLMBookingAgent:
    """
    Real Conversational AI Booking Agent powered by OpenAI.
    Extracts slots (city, budget, date/duration) and returns strictly formatted JSON.
    """

    def __init__(self):
        self.sessions = {}
        self.llm = OpenAIResponsesClient()

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

    async def process_message(self, session_id: str, user_message: str, user_name: str = "Traveler"):
        try:
            session = self.get_session(session_id)
            
            # Keep history short to avoid context explosion
            session["history"].append({"role": "user", "content": user_message})
            if len(session["history"]) > 6:
                session["history"] = session["history"][-6:]

            history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in session["history"]])

            prompt = f"""You are a helpful travel booking AI agent. Your goal is to gather the following parameters from the user to book a trip:
1. Destination City
2. Travel Budget
3. Travel Dates or Number of days

Current Known Parameters for this session:
- City: {session.get('city')}
- Budget: {session.get('budget')}
- Dates/Days: {session.get('start_date')} / {session.get('days')}

Conversation History:
{history_str}

Instructions:
1. Extract any new parameters from the user's latest message and update them.
2. If ANY parameters (City, Budget, Dates/Days) are missing, ask a conversational question to get them. Set status to "NEED_INFO".
3. If ALL parameters are collected, set status to "READY_TO_BOOK". Do not ask any more questions.
4. Output your response STRICTLY as a JSON object with the following schema, and NOTHING else (no markdown wrappers):

{{
    "status": "NEED_INFO" or "READY_TO_BOOK",
    "reply": "Your conversational reply to the user",
    "extracted_slots": {{
        "city": "extracted city or null",
        "budget": "extracted budget string (e.g. ₹50,000) or null",
        "budget_num": integer budget amount or null,
        "start_date": "YYYY-MM-DD or null",
        "days": integer number of days or null
    }}
}}"""
            
            # Generate response from LLM
            # We don't use the JSON schema param yet since it might fail if the model version doesn't support structured outputs, so we prompt for raw JSON.
            llm_response = await self.llm.generate(prompt)
            
            # Clean response (remove markdown if any)
            clean_json = llm_response.replace('```json', '').replace('```', '').strip()
            
            parsed = json.loads(clean_json)
            
            # Update session with extracted slots
            slots = parsed.get("extracted_slots", {})
            if slots.get("city"): session["city"] = slots["city"]
            if slots.get("budget"): session["budget"] = slots["budget"]
            if slots.get("budget_num"): session["budget_num"] = slots["budget_num"]
            if slots.get("start_date"): session["start_date"] = slots["start_date"]
            if slots.get("days"): session["days"] = slots["days"]

            session["history"].append({"role": "assistant", "content": parsed.get("reply", "")})

            if parsed.get("status") == "READY_TO_BOOK":
                # Generate package plan
                city = session["city"] or "Unknown Destination"
                budget_str = session["budget"] or "₹50,000"
                budget_num = session.get("budget_num") or 50000
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
                    "duration": f"{days} Days / {max(1, days-1)} Nights",
                    "start_date": start_date,
                    "flight": f"{carrier} Flight BOOK-{int(datetime.utcnow().timestamp())%10000} (Origin → {city}) — ₹{flight_cost:,}",
                    "hotel": f"{hotel_name} — ₹{hotel_cost:,}",
                    "chauffeur": f"Local Airport Chauffeur & Sightseeing — ₹{chauffeur_cost:,}",
                    "buffer": f"Concierge Reserve & Support — ₹{buffer_cost:,}",
                    "flight_cost": flight_cost,
                    "hotel_cost": hotel_cost,
                    "chauffeur_cost": chauffeur_cost
                }

                return {
                    "status": "READY_TO_BOOK",
                    "reply": parsed.get("reply", "I have generated your custom trip package below!"),
                    "package_plan": package_plan,
                    "session": session
                }

            return {
                "status": "NEED_INFO",
                "reply": parsed.get("reply", "Can you provide more details?"),
                "session": session
            }

        except Exception as e:
            logger.error(f"Error processing LLM booking turn: {e}")
            return {
                "status": "NEED_INFO",
                "reply": "I am experiencing network issues connecting to my AI brain. Please try again.",
                "session": self.get_session(session_id)
            }

# Global Instance
llm_booking_agent = LLMBookingAgent()
