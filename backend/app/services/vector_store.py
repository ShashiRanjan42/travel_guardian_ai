import json
import math
import random
from typing import List, Dict, Any

class SimpleVectorStore:
    """
    Simulates pgvector semantic retrieval using cosine similarity over local embeddings.
    In production, this maps directly to PostgreSQL + pgvector extension.
    """
    def __init__(self):
        self.documents = [
            {
                "id": "policy_weather_delay",
                "category": "DISRUPTION_POLICY",
                "content": "For flight delays exceeding 2 hours due to weather, customer is entitled to fast-track meal vouchers ($45), priority rebooking on partner airlines, or complimentary lounge access.",
                "vector": [0.12, 0.85, 0.33, 0.91, 0.04]
            },
            {
                "id": "policy_missed_connection",
                "category": "DISRUPTION_POLICY",
                "content": "When a flight delay causes a missed downstream rail or flight connection, the system must evaluate: (1) Next direct flight, (2) High-speed train + taxi combo, (3) Hotel night stay if departure is >6 hours away.",
                "vector": [0.45, 0.72, 0.81, 0.15, 0.63]
            },
            {
                "id": "policy_vip_protection",
                "category": "VIP_BENEFITS",
                "content": "VIP Tier Customers get zero-cost delta rebooking on premium carriers, instant private chauffeur dispatch for airport transfers, and auto-extended 5-star hotel check-ins.",
                "vector": [0.90, 0.10, 0.88, 0.76, 0.52]
            },
            {
                "id": "strategy_rail_strike",
                "category": "RECOVERY_PATTERNS",
                "content": "In rail strike scenarios, immediately pivot to rental car dispatch or regional flight shuttle, notifying hotel of late arrival cutoff.",
                "vector": [0.31, 0.65, 0.44, 0.89, 0.20]
            }
        ]

    def search(self, query_text: str, top_k: int = 2) -> List[Dict[str, Any]]:
        # Calculate a pseudo embedding vector for the query text based on term presence
        q_vec = [0.2, 0.7, 0.5, 0.6, 0.4]
        if "weather" in query_text.lower():
            q_vec = [0.15, 0.88, 0.30, 0.90, 0.05]
        elif "connection" in query_text.lower() or "missed" in query_text.lower():
            q_vec = [0.42, 0.70, 0.83, 0.18, 0.60]
        elif "vip" in query_text.lower():
            q_vec = [0.88, 0.12, 0.85, 0.70, 0.50]

        scored = []
        for doc in self.documents:
            sim = self._cosine_similarity(q_vec, doc["vector"])
            scored.append({**doc, "similarity_score": round(sim, 3)})

        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)

vector_store = SimpleVectorStore()
