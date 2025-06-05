from opspilot.core import Scheduler, SchedulerResult
from opspilot.models import Settings, Department
from helpers.data_loader import DataLoader

def run():
    data_loader = DataLoader()
    flights = data_loader.load_flights("data/flights.json")
    services = data_loader.load_services("data/services.json")
    roster = data_loader.load_roster("data/roster.json")
    service_assignments = data_loader.load_service_assignments("data/service_assignments.json")
    travel_times = data_loader.load_travel_times("data/travel_times.json")
    locations = data_loader.load_locations("data/locations.json")
    
    settings = Settings()
   
    department = Department(
        id=1,
        name="Ground Operations",
        roster=roster,
        service_assignments=service_assignments,
        travel_times=travel_times
    )

    scheduler = Scheduler(
        department=department,
        services=services,
        flights=flights,
        settings=settings
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
