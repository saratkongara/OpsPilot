from enum import Enum

class ServiceType(str, Enum):
    MULTI_TASK = "M"
    SINGLE = "S"
    FIXED = "F"

class CertificationRequirement(str, Enum):
    ALL = "All"
    ANY = "Any"

class LocationType(str, Enum):
    BAY = "Bay"
    CHECK_IN_COUNTER = "Check-in Counter"
    BOARDING_GATE = "Boarding Gate"
    ZONE = "Zone"
    AREA = "Area"
    TERMINAL = "Terminal"
