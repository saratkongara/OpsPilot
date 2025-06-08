from behave import given, when, then
from opspilot.models import Staff, Service, Flight, Location, ServiceAssignment, ServiceType
from opspilot.models import EquipmentType, Shift, CertificationRequirement, Settings, TravelTime
from opspilot.services import OverlapDetectionService
from opspilot.core.scheduler import Scheduler
import ast

def parse_human_friendly_shifts(shift_strings):
    shifts = []
    # Parse each shift string
    # Example: '08:00-12:00', '13:00-04:00'
    for shift_str in shift_strings:
        shift_str = shift_str.replace(" ", "")
        start_str, end_str = shift_str.split("-")

        # No need to manually convert the strings to time objects since the Shift class does it
        shifts.append(Shift(start_time=start_str, end_time=end_str))

    return shifts

def setup_staff(context, staff_table):
    context.staff = []

    for row in staff_table:
        certifications = ast.literal_eval(row['certifications'])
        eligible_services = [
            ServiceType(service_type)
            for service_type in ast.literal_eval(row['eligible_for_services'])
        ]

        # Parse human-friendly shift strings
        shift_strings = ast.literal_eval(row.get('shifts', "['08:00-12:00', '13:00-04:00']"))  # e.g., ['08:00-16:00', '19:00-03:00']
        shifts = parse_human_friendly_shifts(shift_strings)

        staff = Staff(
            id=int(row['id']),
            name=row['name'],
            department_id=int(row['department_id']),
            certifications=certifications,
            eligible_for_services=eligible_services,
            shifts=shifts,
            priority_service_id=int(row['priority_service_id']) if row.get('priority_service_id') else None,
            rank_level=int(row.get('rank_level', 10))
        )

        context.staff.append(staff)

def setup_services(context, services_table):
    context.services = []

    for row in services_table:
        context.services.append(
            Service(
                id=int(row['id']),
                name=row['name'],
                certifications=ast.literal_eval(row['certifications']),
                certification_requirement=CertificationRequirement(row['requirement'])
            )
        )

def setup_flights(context, flights_table):
    context.flights = []

    for row in flights_table:
        context.flights.append(
            Flight(
                number=row['number'],
                arrival_time=row.get('arrival_time'),
                departure_time=row.get('departure_time')
            )
        )

def setup_locations(context, locations_table):
    context.locations = []
    
    for row in locations_table:
        context.locations.append(
            Location(
                id=int(row['id']),
                name=row['name'],
                parent_id=int(row['parent_id']) if row.get('parent_id') else None,
            )
        )

def setup_travel_times(context, travel_times_table):
    context.travel_times = []

    for row in travel_times_table:
        context.travel_times.append(
            TravelTime(
                origin_location_id=int(row['origin_location_id']),
                destination_location_id=int(row['destination_location_id']),
                travel_minutes=int(row['travel_minutes'])
            )
        )

def setup_service_assignments(context, assignments_table):
    context.service_assignments = []

    for row in assignments_table:
        context.service_assignments.append(
            ServiceAssignment(
                id=int(row['id']),
                service_id=int(row['service_id']),
                department_id=int(row['department_id']),
                staff_count=int(row['staff_count']),
                priority=float(row.get('priority', 1.0)),
                location_id=int(row.get('location_id')) if row.get('location_id') else None,

                flight_number=row.get('flight_number'),
                relative_start=row.get('relative_start'),
                relative_end=row.get('relative_end'),

                # start_time and end_time are strings here, and the field validators will convert them
                start_time=row['start_time'] if row.get('start_time') else None,
                end_time=row['end_time'] if row.get('end_time') else None,

                service_type=ServiceType(row.get('service_type', 'S')),

                multi_task_limit=int(row.get('multi_task_limit')) if row.get('multi_task_limit') else None,
                exclude_services=ast.literal_eval(row.get('exclude_services', '[]')),

                needs_equipment=row.get('needs_equipment', 'False').lower() == 'true',
                equipment_type=EquipmentType(row['equipment_type']) if row.get('equipment_type') else None,
                equipment_id=int(row['equipment_id']) if row.get('equipment_id') else None
            )
        )

def setup_settings(context, settings_table):
    settings_row = settings_table[0] if settings_table else {}
    context.settings = Settings(
        overlap_buffer_minutes=int(settings_row.get('overlap_buffer_minutes', 10)),
        default_travel_time=int(settings_row.get('default_travel_time', 10)),
        assignment_strategy=settings_row.get('assignment_strategy', 'Balance Workload')
    )

def setup_flight_map(context):
    context.flight_map = {}
    for flight in context.flights:
        context.flight_map[flight.number] = flight

def setup_location_map(context):
    context.location_map = {}
    for location in context.locations:
        context.location_map[location.id] = location

def setup_travel_time_map(context):
    context.travel_time_map = {}
    for travel_time in context.travel_times:
        context.travel_time_map[(travel_time.origin_location_id, travel_time.destination_location_id)] = travel_time.travel_minutes

@given('the following staff exists')
def step_impl(context):
    setup_staff(context, context.table)

@given('the following services exist')
def step_impl(context):
    setup_services(context, context.table)

@given('the following flights exist')
def step_impl(context):
    setup_flights(context, context.table)

@given('the following locations exist')
def step_impl(context):
    setup_locations(context, context.table)

@given('the following travel times exist')
def step_impl(context):
    setup_travel_times(context, context.table)

@given('the following service assignments exist')
def step_impl(context):
    setup_service_assignments(context, context.table)

@given('the following settings exist')
def step_impl(context):
    setup_settings(context, context.table)

@when('the overlap detection service runs')
def step_impl(context):
    setup_flight_map(context)
    setup_location_map(context)
    setup_travel_time_map(context)

    overlap_service = OverlapDetectionService(
        service_assignments=context.service_assignments,
        flight_map=context.flight_map,
        location_map=context.location_map,
        travel_time_map=context.travel_time_map,
        settings=context.settings
    )
    context.overlap_map = overlap_service.detect_overlaps()

@then('the following overlaps should be detected')
def step_impl(context):
    for row in context.table:
        sa_id = int(row['service_assignment_id'])
        expected_overlaps = ast.literal_eval(row['overlapping_service_assignment_ids'])
        actual_overlaps = context.overlap_map.get(sa_id, [])
        assert set(actual_overlaps) == set(expected_overlaps), (
            f"Service {sa_id} overlap mismatch. "
            f"Expected: {expected_overlaps}, Actual: {actual_overlaps}"
        )

@when('the scheduler runs')
def step_impl(context):
    context.scheduler = Scheduler(
        roster=context.staff,
        services=context.services,
        flights=context.flights,
        service_assignments=context.service_assignments,
        locations=context.locations,
        travel_times=context.travel_times,
        settings=context.settings
    )
    context.scheduler.run()

@then('the assignments should be')
def step_impl(context):
    actual_assignments = context.scheduler.get_assignments()
    for row in context.table:
        staff_id = int(row['staff_id'])
        expected = ast.literal_eval(row['assigned_service_ids'])
        actual = actual_assignments.get(staff_id, [])
        assert set(actual) == set(expected), (
            f"Staff {staff_id} assignment mismatch. "
            f"Expected: {expected}, Actual: {actual}"
        )

@then('the service coverage should be')
def step_impl(context):
    actual_coverage = context.scheduler.get_service_coverage()
    for row in context.table:
        sa_id = int(row['service_assignment_id'])
        expected = int(row['assigned_staff_count'])
        actual = actual_coverage[sa_id]
        assert actual == expected, (
            f"Service {sa_id} coverage mismatch. "
            f"Expected: {expected}, Actual: {actual}"
        )