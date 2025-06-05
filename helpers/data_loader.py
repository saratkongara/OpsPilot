from opspilot.models import Flight, Service, Staff, Shift, ServiceAssignment, TravelTime, CertificationRequirement, ServiceType, Location
from typing import List
import json

class DataLoader:
    def load_json(self, file_path: str):
        with open(file_path, "r") as f:
            return json.load(f)

    def load_flights(self, file_path: str) -> List[Flight]:
        return [Flight(**f) for f in self.load_json(file_path)]

    def load_services(self, file_path: str) -> List[Service]:
        services = self.load_json(file_path)
        return [
            Service(
                **{
                    **s,
                    "certification_requirement": CertificationRequirement(s["certification_requirement"])
                }
            )
            for s in services
        ]

    def load_roster(self, file_path: str) -> List[Staff]:
        roster_data = self.load_json(file_path)
        return [
            Staff(
                **{
                    **staff,
                    "shifts": [Shift(**shift) for shift in staff["shifts"]]
                }
            )
            for staff in roster_data
        ]

    def load_service_assignments(self, file_path: str) -> List[ServiceAssignment]:
        assignments = self.load_json(file_path)
        return [
            ServiceAssignment(
                **{
                    **a,
                    "service_type": ServiceType(a["service_type"])
                }
            )
            for a in assignments
        ]

    def load_travel_times(self, file_path: str) -> List[TravelTime]:
        return [TravelTime(**t) for t in self.load_json(file_path)]

    def load_locations(self, file_path: str) -> List[Location]:
        return [Location(**l) for l in self.load_json(file_path)] 