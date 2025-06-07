from opspilot.core import Scheduler, SchedulerResult
from opspilot.models import (
    Flight, Service, Staff, Shift, ServiceAssignment, TravelTime, Settings,
    CertificationRequirement, ServiceType, Location
)
from typing import List
import json

def load_json(file_path: str):
    with open(file_path, "r") as f:
        return json.load(f)

def load_flights(file_path: str) -> List[Flight]:
    return [Flight(**f) for f in load_json(file_path)]

def load_services(file_path: str) -> List[Service]:
    services = load_json(file_path)
    return [
        Service(
            **{
                **s,
                "certification_requirement": CertificationRequirement(s["certification_requirement"])
            }
        )
        for s in services
    ]

def load_roster(file_path: str) -> List[Staff]:
    roster_data = load_json(file_path)
    return [
        Staff(
            **{
                **staff,
                "shifts": [Shift(**shift) for shift in staff["shifts"]]
            }
        )
        for staff in roster_data
    ]

def load_service_assignments(file_path: str) -> List[ServiceAssignment]:
    assignments = load_json(file_path)
    return [
        ServiceAssignment(
            **{
                **a,
                "service_type": ServiceType(a["service_type"])
            }
        )
        for a in assignments
    ]

def load_travel_times(file_path: str) -> List[TravelTime]:
    return [TravelTime(**t) for t in load_json(file_path)]

def load_locations(file_path: str) -> List[Location]:
    return [Location(**l) for l in load_json(file_path)] 

def run():
    flights = load_flights("data/flights.json")
    services = load_services("data/services.json")
    roster = load_roster("data/roster.json")
    service_assignments = load_service_assignments("data/service_assignments.json")
    travel_times = load_travel_times("data/travel_times.json")
    locations = load_locations("data/locations.json")
    settings = Settings()

    scheduler = Scheduler(
        roster=roster,
        services=services,
        flights=flights,
        service_assignments=service_assignments,
        settings=settings,
        travel_times=travel_times
    )

    result = scheduler.run()

    if result == SchedulerResult.FOUND:
        assignments = scheduler.get_assignments()
        for staff_id, assignment_id in assignments.items():
            print(f"Staff ID {staff_id} assigned to Service Assignment ID {assignment_id}") 
    
        location_map = {location.id: location for location in locations}
        
        staff_schedule = scheduler.get_allocation_plan(location_map).staff_schedule()
        print(f"Staff schedule: #{staff_schedule}")

        flight_zone_services_schedule = scheduler.get_allocation_plan(location_map).flight_zone_services_schedule()
        print(f"Flight zone services schedule: #{flight_zone_services_schedule}")

        common_zone_services_schedule = scheduler.get_allocation_plan(location_map).common_zone_services_schedule()
        print(f"Common zone services schedule: #{common_zone_services_schedule}")
    else:
        print("No feasible schedule found.")

if __name__ == "__main__":
    run()
