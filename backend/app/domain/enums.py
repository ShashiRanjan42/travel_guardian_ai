from enum import StrEnum

class UserRole(StrEnum):
    OPS_AGENT = 'ops_agent'
    TRAVELLER = 'traveller'

class LegMode(StrEnum):
    FLIGHT = 'FLIGHT'
    TRAIN = 'TRAIN'
    BUS = 'BUS'
    CAB = 'CAB'
    FERRY = 'FERRY'
    HOTEL = 'HOTEL'
    ACTIVITY = 'ACTIVITY'

class LegStatus(StrEnum):
    CONFIRMED = 'CONFIRMED'
    AT_RISK = 'AT_RISK'
    DISRUPTED = 'DISRUPTED'
    REBOOKED = 'REBOOKED'
    CANCELLED = 'CANCELLED'
    COMPLETED = 'COMPLETED'

class DisruptionType(StrEnum):
    WEATHER = 'WEATHER'
    LANDSLIDE = 'LANDSLIDE'
    TRAFFIC = 'TRAFFIC'
    STRIKE = 'STRIKE'
    CANCELLATION = 'CANCELLATION'
    DELAY = 'DELAY'
    REGULATORY = 'REGULATORY'
    VENDOR_FAILURE = 'VENDOR_FAILURE'

class Severity(StrEnum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'
    CRITICAL = 'CRITICAL'

class AlertStatus(StrEnum):
    DETECTED = 'DETECTED'
    ASSESSING = 'ASSESSING'
    OPTIONS_READY = 'OPTIONS_READY'
    PENDING_OPS_REVIEW = 'PENDING_OPS_REVIEW'
    DISPATCHED = 'DISPATCHED'
    AWAITING_RESPONSE = 'AWAITING_RESPONSE'
    RESOLVED = 'RESOLVED'
    ESCALATED = 'ESCALATED'
    NEEDS_MANUAL = 'NEEDS_MANUAL'
    DISMISSED = 'DISMISSED'

class OptionStatus(StrEnum):
    DRAFT = 'DRAFT'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    SELECTED = 'SELECTED'
    EXPIRED = 'EXPIRED'
    OVERRIDDEN = 'OVERRIDDEN'

class AgentName(StrEnum):
    WATCHER = 'WATCHER'
    CORRELATOR = 'CORRELATOR'
    SCORER = 'SCORER'
    REPLANNER = 'REPLANNER'
    COMPLIANCE = 'COMPLIANCE'
    COMMUNICATOR = 'COMMUNICATOR'
    ORCHESTRATOR = 'ORCHESTRATOR'

class AgentStatus(StrEnum):
    SUCCESS = 'success'
    PARTIAL = 'partial'
    FAILED = 'failed'
    SKIPPED = 'skipped'
    RUNNING = 'running'

class DataFreshness(StrEnum):
    LIVE = 'live'
    CACHED = 'cached'
    DEGRADED = 'degraded'
    SYNTHETIC = 'synthetic'
