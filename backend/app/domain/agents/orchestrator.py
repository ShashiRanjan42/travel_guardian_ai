import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.domain.agents.base import AgentContext
from app.domain.agents.correlator import Correlator
from app.domain.agents.scorer import Scorer
from app.domain.agents.replanner import Replanner
from app.domain.agents.compliance import Compliance
from app.domain.agents.communicator import Communicator
from app.integrations.llm.openai_responses import OpenAIResponsesClient
from app.api.v1.ws import manager
from app.data.session import AsyncSessionLocal
from app.data.models import AgentTrace, ImpactAssessment, ReplanOption, Leg, DisruptionEvent
from sqlalchemy import select

class Orchestrator:
    def __init__(self):
        self.llm = OpenAIResponsesClient()
        self.correlator = Correlator(self.llm)
        self.scorer = Scorer(self.llm)
        self.replanner = Replanner(self.llm)
        self.compliance = Compliance(self.llm)
        self.communicator = Communicator(self.llm)

    async def log_trace(self, session, run_id, assessment_id, agent_name, seq, result):
        now = datetime.now(timezone.utc)
        trace = AgentTrace(
            run_id=str(run_id),
            assessment_id=assessment_id,
            agent=agent_name,
            seq=seq,
            status=result.status,
            input_summary="...",
            output_summary=str(result.output)[:500],
            reasoning=result.reasoning,
            confidence=result.confidence,
            duration_ms=result.duration_ms,
            tokens_in=0,
            tokens_out=0,
            attempt=1,
            error=result.error,
            started_at=now,
            ended_at=now
        )
        session.add(trace)
        await session.commit()
        
        # Broadcast trace event
        await manager.broadcast({
            "type": "agent.trace",
            "payload": {
                "run_id": str(run_id),
                "assessment_id": str(assessment_id),
                "agent": agent_name,
                "status": result.status,
                "duration_ms": result.duration_ms
            }
        })

    async def process_event(self, event_id: str):
        # We need a DB session
        async with AsyncSessionLocal() as session:
            # 1. Fetch event
            _event_id_obj = uuid.UUID(event_id) if isinstance(event_id, str) else event_id
            result = await session.execute(select(DisruptionEvent).where(DisruptionEvent.id == _event_id_obj))
            event = result.scalar_one_or_none()
            if not event:
                return
            
            run_id = uuid.uuid4()
            
            # 2. Fetch active legs
            result = await session.execute(select(Leg))
            legs = result.scalars().all()
            
            # Run Correlator
            correlator_res = self.correlator.evaluate(event, legs)
            # Log trace manually for correlator since it doesn't use AgentContext directly yet in our mock, 
            # actually we can mock the result structure
            class MockRes: pass
            res = MockRes()
            res.status = correlator_res["status"]
            res.output = {"direct": len(correlator_res["direct_match_ids"]), "cascade": len(correlator_res["cascade_match_ids"])}
            res.reasoning = await self.correlator.explain(event, correlator_res)
            res.confidence = 1.0
            res.duration_ms = correlator_res["duration_ms"]
            res.error = None
            
            await self.log_trace(session, run_id, None, "CORRELATOR", 2, res)
            
            if not correlator_res["direct_match_ids"]:
                return # No matches

            # In a real system, we'd group matched legs by booking.
            # We'll assume one booking for the demo path.
            matched_leg_id = correlator_res["direct_match_ids"][0]
            from app.data.models import Booking, Itinerary, ItineraryVersion
            stmt = select(Booking.id, Itinerary.id).join(Itinerary).join(ItineraryVersion).join(Leg).where(Leg.id == matched_leg_id)
            booking_result = await session.execute(stmt)
            booking_and_itinerary = booking_result.one_or_none()
            if not booking_and_itinerary:
                return
            booking_id, itinerary_id = booking_and_itinerary
            
            # 3. Create Assessment
            assessment = ImpactAssessment(
                event_id=event.id,
                booking_id=booking_id,
                itinerary_id=itinerary_id,
                status="ASSESSING",
                severity="UNKNOWN",
                severity_score=0.0,
                severity_breakdown={},
                affected_leg_ids=[str(i) for i in correlator_res["direct_match_ids"]],
                cascade_leg_ids=[str(i) for i in correlator_res["cascade_match_ids"]],
                impact_summary="Assessing impact...",
                hours_to_departure=14.2, # Hardcoded for demo
                correlation_confidence=1.0,
                run_id=str(run_id)
            )
            session.add(assessment)
            await session.commit()
            
            ctx = AgentContext(
                run_id=str(run_id),
                event=event,
                assessment=assessment,
                options=[],
                itinerary=None,
                traveller_profile={},
                prior_results={}
            )

            # Scorer
            score_res = await self.scorer.run(ctx)
            await self.log_trace(session, run_id, assessment.id, "SCORER", 3, score_res)
            
            assessment.severity = score_res.output["label"]
            assessment.severity_score = score_res.output["score"]
            assessment.severity_breakdown = score_res.output["breakdown"]
            await session.commit()

            # Replanner
            replan_res = await self.replanner.run(ctx)
            await self.log_trace(session, run_id, assessment.id, "REPLANNER", 4, replan_res)
            ctx.options = replan_res.output

            # Compliance
            comp_res = await self.compliance.run(ctx)
            await self.log_trace(session, run_id, assessment.id, "COMPLIANCE", 5, comp_res)
            ctx.options = comp_res.output
            
            # Write options to DB
            for idx, opt_data in enumerate(ctx.options):
                opt = ReplanOption(
                    assessment_id=assessment.id,
                    rank=opt_data.get("rank", idx+1),
                    label=opt_data.get("label", ""),
                    summary=opt_data.get("summary", ""),
                    status=opt_data.get("status", "DRAFT"),
                    cost_delta_inr=opt_data.get("cost_delta_inr", 0),
                    time_delta_minutes=opt_data.get("time_delta_minutes", 0),
                    risk_score=opt_data.get("risk_score", 0.0),
                    confidence=opt_data.get("confidence", 0.0),
                    evidence=opt_data.get("evidence", []),
                    assumptions=opt_data.get("assumptions", []),
                    tradeoffs=opt_data.get("tradeoffs", ""),
                    rejection_reason=opt_data.get("rejection_reason"),
                    rejected_by_rule=opt_data.get("rejected_by_rule")
                )
                session.add(opt)
            await session.commit()

            # Communicator
            comm_res = await self.communicator.run(ctx)
            await self.log_trace(session, run_id, assessment.id, "COMMUNICATOR", 6, comm_res)
            
            # Update assessment status
            assessment.status = "PENDING_OPS_REVIEW" if assessment.severity in ["HIGH", "CRITICAL"] else "OPTIONS_READY"
            await session.commit()
            
            # Broadcast alert created
            await manager.broadcast({
                "type": "alert.created",
                "payload": {
                    "alert_id": str(assessment.id),
                    "event_headline": event.headline,
                    "severity": assessment.severity,
                    "score": assessment.severity_score
                }
            })
