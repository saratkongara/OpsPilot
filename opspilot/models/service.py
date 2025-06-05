from pydantic import BaseModel
from typing import List
from .enums import CertificationRequirement

class Service(BaseModel):
    id: int
    name: str
    certifications: List[int]  # List of certification IDs
    certification_requirement: CertificationRequirement
