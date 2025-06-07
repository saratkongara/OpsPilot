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
                flight_task_priority_roles = task.priority_roles
                priority_roles = [flight_task_priority_roles[k] for k in sorted(flight_task_priority_roles.keys())]
                
                service_assignment = ServiceAssignment(
                    id=service_id_counter,
                    service_id=task.GroundSupportEquipmentId,
                    priority=task.auto_allocation_priority,
                    staff_count=1,
                    location_id=location.id,
                    flight_number=flight_number,
                    relative_start=task.relative_start_sla,
                    relative_end=task.relative_end_sla,
                    service_type=ServiceType.SINGLE,
                    priority_roles=priority_roles,
                )
                # Set the task's service assignment ID
                task.service_assignment_id = service_assignment.id

                service_assignments.append(service_assignment)
                service_id_counter += 1

                locations.append(location)
                location_id_counter += 1

        for common_task in self.common_tasks:
            department_id = common_task.departmentId

            for task in common_task.tasks:
                start_time = ParserUtil.extract_time(task.start_sla)
                end_time = ParserUtil.extract_time(task.end_sla)

                location = Location(id=location_id_counter,
                                    name=f'Location_{location_id_counter}')
                
                common_task_priority_roles = task.priority_roles
                priority_roles = [common_task_priority_roles[k] for k in sorted(common_task_priority_roles.keys())]
                
                service_assignment = ServiceAssignment(
                    id=service_id_counter,
                    service_id=task.logId,
                    department_id=department_id,
                    priority=task.auto_allocation_priority,
                    staff_count=1,
                    location_id=location.id,
                    start_time=start_time,
                    end_time=end_time,
                    service_type=ServiceType.SINGLE,
                    priority_roles=priority_roles,
                )
                # Set the task's service assignment ID
                task.service_assignment_id = service_assignment.id

                service_assignments.append(service_assignment)
                service_id_counter += 1

                locations.append(location)
                location_id_counter += 1

        return (service_assignments, locations)
    
    def __repr__(self):
        return f"ServiceAssignmentsBuilder(flights_with_tasks={self.flights_with_tasks}, common_tasks={self.common_tasks})"