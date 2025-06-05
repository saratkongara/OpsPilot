from opspilot.core import MultiScheduler, SchedulerResult
from opspilot.models import Settings, Department
from helpers.data_loader import DataLoader

def run():
    data_loader = DataLoader()
    flights = data_loader.load_flights("data/flights.json")
    services = data_loader.load_services("data/services.json")
    department_travel_times = data_loader.load_travel_times("data/department_travel_times.json")

    # Load department_1 data
    dep1_roster = data_loader.load_roster("data/department_1/roster.json")
    dep1_service_assignments = data_loader.load_service_assignments("data/department_1/service_assignments.json")
    dep1_travel_times = data_loader.load_travel_times("data/department_1/travel_times.json") 
    
    # Load department_2 data
    dep2_roster = data_loader.load_roster("data/department_2/roster.json")
    dep2_service_assignments = data_loader.load_service_assignments("data/department_2/service_assignments.json")
    dep2_travel_times = data_loader.load_travel_times("data/department_2/travel_times.json") 

    settings = Settings()
   
    department_1 = Department(
        id=1,
        name="Department 1",
        roster=dep1_roster,
        service_assignments=dep1_service_assignments,
        travel_times=dep1_travel_times
    )

    department_2 = Department(
        id=2,
        name="Department 2",
        roster=dep2_roster,
        service_assignments=dep2_service_assignments,
        travel_times=dep2_travel_times
    )

    multi_scheduler = MultiScheduler(
        departments=[department_1, department_2],
        services=services,
        flights=flights,
        travel_times=department_travel_times,
        settings=settings
    )

    result = multi_scheduler.run()

    if result == SchedulerResult.FOUND:
        print("All departments scheduled successfully.")
    else:
        print("No feasible schedule found.")

if __name__ == "__main__":
    run()
