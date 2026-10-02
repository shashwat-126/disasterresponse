from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    RESPONDER = "RESPONDER"  # legacy generic role, kept for backward compatibility
    DEPARTMENT_STAFF = "DEPARTMENT_STAFF"
    CITIZEN = "CITIZEN"


class IncidentStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    TRIAGED = "TRIAGED"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DepartmentCategory(str, Enum):
    FIRE = "FIRE"
    MEDICAL = "MEDICAL"
    POLICE = "POLICE"
    EMERGENCY_RESPONSE = "EMERGENCY_RESPONSE"
    FOOD_RELIEF = "FOOD_RELIEF"
    ELECTRICITY = "ELECTRICITY"
    WATER_SUPPLY = "WATER_SUPPLY"
    MUNICIPAL = "MUNICIPAL"
    DISASTER_MANAGEMENT_AUTHORITY = "DISASTER_MANAGEMENT_AUTHORITY"
    NGO_VOLUNTEERS = "NGO_VOLUNTEERS"


class AssignmentStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ResourceRequestStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FULFILLED = "FULFILLED"
