from opspilot.models import ServiceAssignment, ServiceType, Location
from .parser_util import ParserUtil

class ServiceAssignmentsBuilder:
    def __init__(self, flights_with_tasks: list[any], common_tasks: list[any]):
        self.flights_with_tasks = flights_with_tasks
        self.common_tasks = common_tasks

    def build(self):
        service_assignments = []
        locations = []
        service_id_counter = 1
        location_id_counter = 1

        for fwt in self.flights_with_tasks:
            if fwt.flight_splited_for == 'departure':
                flight_number = fwt.flight_departure_no 
            elif fwt.flight_splited_for == 'arrival':
                flight_number = fwt.flight_arrival_no
            else:
                flight_number = f'{fwt.flight_arrival_no}-{fwt.flight_departure_no}'

            location = Location(id=location_id_counter,
                                name=f'Location_{location_id_counter}')

            for task in fwt.tasks:
                service_assignment = ServiceAssignment(
                    id=service_id_counter,
                    service_id=task.GroundSupportEquipmentId,
                    priority=1.0,
                    staff_count=1,
                    location_id=location.id,
                    flight_number=flight_number,
                    relative_start=task.start_sla,
                    relative_end=task.end_sla,
                    service_type=ServiceType.SINGLE,  # Default type, can be changed based on task
                )

                service_assignments.append(service_assignment)
                service_id_counter += 1

                locations.append(location)
                location_id_counter += 1

        for common_task in self.common_tasks:
            for task in common_task.tasks:
                start_time = ParserUtil.extract_time(task.start_sla)
                end_time = ParserUtil.extract_time(task.end_sla)

                location = Location(id=location_id_counter,
                                    name=f'Location_{location_id_counter}')
                
                service_assignment = ServiceAssignment(
                    id=service_id_counter,
                    service_id=task.logId,
                    priority=1.0,
                    staff_count=1,
                    location_id=location.id,
                    start_time=start_time,
                    end_time=end_time,
                    service_type=ServiceType.SINGLE,
                )

                service_assignments.append(service_assignment)
                service_id_counter += 1

                locations.append(location)
                location_id_counter += 1

        return (service_assignments, locations)
    
    def __repr__(self):
        return f"ServiceAssignmentsBuilder(flights_with_tasks={self.flights_with_tasks}, common_tasks={self.common_tasks})"