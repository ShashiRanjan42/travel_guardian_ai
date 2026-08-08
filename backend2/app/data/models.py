from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy import String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from app.domain.enums import (
    UserRole, LegMode, LegStatus, DisruptionType, Severity,
    AlertStatus, OptionStatus, AgentName, AgentStatus, DataFreshness
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String)  # Enum UserRole
    full_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Traveller(Base):
    __tablename__ = 'travellers'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('users.id'))
    full_name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    is_solo: Mapped[bool] = mapped_column(Boolean)
    vulnerability_flag: Mapped[str] = mapped_column(String(30))
    preferences: Mapped[Dict[str, Any]] = mapped_column(JSON)

class Booking(Base):
    __tablename__ = 'bookings'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    pnr: Mapped[str] = mapped_column(String(12), unique=True)
    traveller_id: Mapped[UUID] = mapped_column(ForeignKey('travellers.id'))
    ops_agent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('users.id'))
    destination: Mapped[str] = mapped_column(String(120))
    origin: Mapped[str] = mapped_column(String(120))
    start_date: Mapped[datetime] = mapped_column(DateTime) # DATE
    end_date: Mapped[datetime] = mapped_column(DateTime) # DATE
    total_value_inr: Mapped[int] = mapped_column(Integer)
    non_refundable_value_inr: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50)) # Added source (SEEDED/CUSTOMER_CREATED)
    
    itineraries: Mapped[List['Itinerary']] = relationship(back_populates='booking')
    traveller: Mapped['Traveller'] = relationship()

class Itinerary(Base):
    __tablename__ = 'itineraries'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    booking_id: Mapped[UUID] = mapped_column(ForeignKey('bookings.id'))
    current_version: Mapped[int] = mapped_column(Integer)
    
    booking: Mapped['Booking'] = relationship(back_populates='itineraries')
    versions: Mapped[List['ItineraryVersion']] = relationship(back_populates='itinerary')

class ItineraryVersion(Base):
    __tablename__ = 'itinerary_versions'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    itinerary_id: Mapped[UUID] = mapped_column(ForeignKey('itineraries.id'))
    version: Mapped[int] = mapped_column(Integer)
    created_by: Mapped[str] = mapped_column(String(40))
    reason: Mapped[str] = mapped_column(Text)
    triggered_by_alert_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('impact_assessments.id'))
    snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    
    itinerary: Mapped['Itinerary'] = relationship(back_populates='versions')
    legs: Mapped[List['Leg']] = relationship(back_populates='version')

class Leg(Base):
    __tablename__ = 'legs'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    itinerary_version_id: Mapped[UUID] = mapped_column(ForeignKey('itinerary_versions.id'))
    seq: Mapped[int] = mapped_column(Integer)
    day_index: Mapped[int] = mapped_column(Integer)
    mode: Mapped[str] = mapped_column(String) # ENUM LegMode
    status: Mapped[str] = mapped_column(String) # ENUM LegStatus
    title: Mapped[str] = mapped_column(String(160))
    vendor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('vendors.id'))
    origin_name: Mapped[str] = mapped_column(String(120))
    origin_lat: Mapped[float] = mapped_column(Float)
    origin_lon: Mapped[float] = mapped_column(Float)
    dest_name: Mapped[str] = mapped_column(String(120))
    dest_lat: Mapped[float] = mapped_column(Float)
    dest_lon: Mapped[float] = mapped_column(Float)
    waypoints: Mapped[List[Dict[str, Any]]] = mapped_column(JSON)
    depart_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    arrive_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    cost_inr: Mapped[int] = mapped_column(Integer)
    is_refundable: Mapped[bool] = mapped_column(Boolean)
    booking_ref: Mapped[str] = mapped_column(String(40))
    depends_on_leg_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('legs.id'))
    
    version: Mapped['ItineraryVersion'] = relationship(back_populates='legs')

class DisruptionEvent(Base):
    __tablename__ = 'disruption_events'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    type: Mapped[str] = mapped_column(String) # ENUM DisruptionType
    source_name: Mapped[str] = mapped_column(String(80))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_reliability: Mapped[float] = mapped_column(Float)
    raw_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    headline: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    geo_center_lat: Mapped[float] = mapped_column(Float)
    geo_center_lon: Mapped[float] = mapped_column(Float)
    radius_km: Mapped[float] = mapped_column(Float)
    affected_modes: Mapped[List[str]] = mapped_column(JSON)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    severity_hint: Mapped[str] = mapped_column(String) # ENUM Severity
    freshness: Mapped[str] = mapped_column(String) # ENUM DataFreshness
    injection_flagged: Mapped[bool] = mapped_column(Boolean)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class ImpactAssessment(Base):
    __tablename__ = 'impact_assessments'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    event_id: Mapped[UUID] = mapped_column(ForeignKey('disruption_events.id'))
    booking_id: Mapped[UUID] = mapped_column(ForeignKey('bookings.id'))
    itinerary_id: Mapped[UUID] = mapped_column(ForeignKey('itineraries.id'))
    status: Mapped[str] = mapped_column(String) # ENUM AlertStatus
    severity: Mapped[str] = mapped_column(String) # ENUM Severity
    severity_score: Mapped[float] = mapped_column(Float)
    severity_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON)
    affected_leg_ids: Mapped[List[str]] = mapped_column(JSON)
    cascade_leg_ids: Mapped[List[str]] = mapped_column(JSON)
    impact_summary: Mapped[str] = mapped_column(Text)
    hours_to_departure: Mapped[float] = mapped_column(Float)
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    correlation_confidence: Mapped[float] = mapped_column(Float)
    run_id: Mapped[UUID] = mapped_column(String) # UUID but stored as string mostly? No, UUID is UUID
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class ReplanOption(Base):
    __tablename__ = 'replan_options'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey('impact_assessments.id'))
    rank: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(80))
    summary: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String) # ENUM OptionStatus
    cost_delta_inr: Mapped[int] = mapped_column(Integer)
    time_delta_minutes: Mapped[int] = mapped_column(Integer)
    risk_score: Mapped[float] = mapped_column(Float)
    confidence: Mapped[float] = mapped_column(Float)
    evidence: Mapped[List[Dict[str, Any]]] = mapped_column(JSON)
    assumptions: Mapped[List[str]] = mapped_column(JSON)
    tradeoffs: Mapped[str] = mapped_column(Text)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text)
    rejected_by_rule: Mapped[Optional[str]] = mapped_column(String(10))
    override_reason: Mapped[Optional[str]] = mapped_column(Text)
    overridden_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey('users.id'))
    overridden_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    approved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey('users.id'))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

class OptionLeg(Base):
    __tablename__ = 'option_legs'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    option_id: Mapped[UUID] = mapped_column(ForeignKey('replan_options.id'))
    change_type: Mapped[str] = mapped_column(String) # ADDED, MODIFIED, REMOVED, UNCHANGED
    seq: Mapped[int] = mapped_column(Integer)
    day_index: Mapped[int] = mapped_column(Integer)
    mode: Mapped[Optional[str]] = mapped_column(String) # ENUM LegMode
    status: Mapped[Optional[str]] = mapped_column(String) # ENUM LegStatus
    title: Mapped[Optional[str]] = mapped_column(String(160))
    vendor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('vendors.id'))
    origin_name: Mapped[Optional[str]] = mapped_column(String(120))
    origin_lat: Mapped[Optional[float]] = mapped_column(Float)
    origin_lon: Mapped[Optional[float]] = mapped_column(Float)
    dest_name: Mapped[Optional[str]] = mapped_column(String(120))
    dest_lat: Mapped[Optional[float]] = mapped_column(Float)
    dest_lon: Mapped[Optional[float]] = mapped_column(Float)
    waypoints: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)
    depart_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    arrive_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    cost_inr: Mapped[Optional[int]] = mapped_column(Integer)
    is_refundable: Mapped[Optional[bool]] = mapped_column(Boolean)
    booking_ref: Mapped[Optional[str]] = mapped_column(String(40))

class Notification(Base):
    __tablename__ = 'notifications'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    traveller_id: Mapped[UUID] = mapped_column(ForeignKey('travellers.id'))
    assessment_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('impact_assessments.id'))
    channel: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(120))
    body: Mapped[str] = mapped_column(Text)
    requires_action: Mapped[bool] = mapped_column(Boolean)
    sla_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class TravellerResponse(Base):
    __tablename__ = 'traveller_responses'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey('impact_assessments.id'))
    selected_option_id: Mapped[UUID] = mapped_column(ForeignKey('replan_options.id'))
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    response_latency_seconds: Mapped[int] = mapped_column(Integer)
    channel: Mapped[str] = mapped_column(String(20))

class AgentTrace(Base):
    __tablename__ = 'agent_traces'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    run_id: Mapped[UUID] = mapped_column(String) # logically UUID
    assessment_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('impact_assessments.id'))
    agent: Mapped[str] = mapped_column(String) # ENUM AgentName
    seq: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String) # ENUM AgentStatus
    input_summary: Mapped[str] = mapped_column(Text)
    output_summary: Mapped[str] = mapped_column(Text)
    reasoning: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float)
    duration_ms: Mapped[int] = mapped_column(Integer)
    tokens_in: Mapped[int] = mapped_column(Integer)
    tokens_out: Mapped[int] = mapped_column(Integer)
    attempt: Mapped[int] = mapped_column(Integer)
    error: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    actor_type: Mapped[str] = mapped_column(String(20))
    actor_id: Mapped[str] = mapped_column(String(60))
    action: Mapped[str] = mapped_column(String(60))
    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[str] = mapped_column(String)
    before: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    after: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    metadata_col: Mapped[Dict[str, Any]] = mapped_column('metadata', JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

class Vendor(Base):
    __tablename__ = 'vendors'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(120))
    type: Mapped[str] = mapped_column(String) # ENUM LegMode
    reliability_score: Mapped[float] = mapped_column(Float)
    supports_modes: Mapped[List[str]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
