from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False) # Plain/hashed for demo
    role = Column(String, default="CUSTOMER") # CUSTOMER, OPS
    tier = Column(String, default="VIP") # VIP, Platinum, Gold, Standard
    phone = Column(String, nullable=True)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    tier = Column(String, default="VIP") # VIP, Platinum, Gold, Standard
    home_city = Column(String, default="Mumbai")
    preferences = Column(Text, default="{}") # JSON string

    itineraries = relationship("Itinerary", back_populates="customer")

class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, ForeignKey("customers.id"))
    title = Column(String, nullable=False)
    status = Column(String, default="OK") # OK, WARNING, DISRUPTED, RECOVERING, RECOVERED
    risk_score = Column(Integer, default=10) # 0 - 100 Risk Score for sorting
    risk_level = Column(String, default="LOW") # CRITICAL, HIGH, ELEVATED, LOW
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="itineraries")
    legs = relationship("ItineraryLeg", back_populates="itinerary", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="itinerary", cascade="all, delete-orphan")

class ItineraryLeg(Base):
    __tablename__ = "itinerary_legs"

    id = Column(String, primary_key=True, index=True)
    itinerary_id = Column(String, ForeignKey("itineraries.id"))
    leg_type = Column(String, nullable=False) # FLIGHT, TRAIN, HOTEL, CAR, EVENT
    sequence_order = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    operator = Column(String, nullable=True) # IndiGo, Air India, Vistara, Vande Bharat, Taj, Marriott
    code = Column(String, nullable=True) # 6E-204, AI-801, UK-945, VB-2066
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    origin_lat = Column(Float, nullable=True)
    origin_lon = Column(Float, nullable=True)
    dest_lat = Column(Float, nullable=True)
    dest_lon = Column(Float, nullable=True)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    status = Column(String, default="SCHEDULED") # SCHEDULED, BOARDING, DELAYED, CANCELLED, REBOOKED
    details_json = Column(Text, default="{}")

    itinerary = relationship("Itinerary", back_populates="legs")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True, index=True)
    itinerary_id = Column(String, ForeignKey("itineraries.id"))
    leg_id = Column(String, ForeignKey("itinerary_legs.id"), nullable=True)
    title = Column(String, nullable=False)
    type = Column(String, nullable=False) # WEATHER, DELAY, CANCELLATION, TRAFFIC, DISASTER
    severity = Column(String, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String, default="OPEN") # OPEN, RECOVERY_PROPOSED, APPROVED, RECOVERED, CLOSED
    description = Column(Text, nullable=False)
    impact_summary = Column(Text, nullable=True)
    location_name = Column(String, nullable=True)
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    detected_at = Column(DateTime, default=datetime.utcnow)

    itinerary = relationship("Itinerary", back_populates="incidents")
    recovery_plans = relationship("RecoveryPlan", back_populates="incident", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="incident", cascade="all, delete-orphan")

class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id = Column(String, primary_key=True, index=True)
    incident_id = Column(String, ForeignKey("incidents.id"))
    option_code = Column(String, nullable=False) # OPTION_A, OPTION_B, OPTION_C
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    cost_delta = Column(Float, default=0.0)
    eta_delta_minutes = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.95)
    reasoning = Column(Text, nullable=False)
    tradeoffs = Column(Text, nullable=True)
    actions_json = Column(Text, default="[]")
    status = Column(String, default="PROPOSED") # PROPOSED, APPROVED, REJECTED, EXECUTED

    incident = relationship("Incident", back_populates="recovery_plans")

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String, ForeignKey("incidents.id"), nullable=True)
    agent_name = Column(String, nullable=False)
    status = Column(String, default="INFO")
    action = Column(String, nullable=False)
    details = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    incident = relationship("Incident", back_populates="agent_logs")

class SemanticVectorStore(Base):
    __tablename__ = "semantic_vector_store"

    id = Column(String, primary_key=True, index=True)
    category = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    vector_json = Column(Text, nullable=False)
    metadata_json = Column(Text, default="{}")
