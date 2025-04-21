from enum import Enum

class CertificationRequirement(str, Enum):
    ALL = "All"
    ANY = "Any"

class EquipmentType(str, Enum):
    GroundPowerUnit = "GPU"
    PushBackTractor = "PBT"
    BagggeLoader = "BFL"
    AirStarterUnit = "ASU"

class LocationType(str, Enum):
    BAY = "Bay"
    CHECK_IN_COUNTER = "Check-in Counter"
    BOARDING_GATE = "Boarding Gate"
    ZONE = "Zone"
    AREA = "Area"
    TERMINAL = "Terminal"

class ServiceType(str, Enum):
    MULTI_TASK = "M"
    SINGLE = "S"
    FIXED = "F"
