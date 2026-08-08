from typing import Any, Dict, List, Literal, Optional, Protocol
from pydantic import BaseModel
from dataclasses import dataclass

class Evidence(BaseModel):
    source: str
    claim: str
    url: Optional[str] = None

@dataclass
class AgentContext:
    run_id: str
    event: Any
    assessment: Any
    options: list[Any]
    itinerary: Any
    traveller_profile: dict
    prior_results: dict[str, 'AgentResult']
    attempt: int = 1

@dataclass
class AgentResult:
    agent: str
    status: Literal["success", "partial", "failed", "skipped"]
    output: Any
    confidence: float
    duration_ms: int
    reasoning: str
    evidence: list[Evidence]
    error: Optional[str] = None

class Agent(Protocol):
    name: str

    async def run(self, ctx: AgentContext) -> AgentResult: ...
