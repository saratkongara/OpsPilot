from behave import given, when, then
from opspilot.models import Staff, Service, ServiceType, ServiceAssignment
from opspilot.models import EquipmentType, Shift, CertificationRequirement, Settings
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

def setup_service_assignments(context, assignments_table):
    context.service_assignments = []

    for row in assignments_table:
        context.service_assignments.append(
            ServiceAssignment(
                id=int(row['id']),
                service_id=int(row['service_id']),
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

@given('the following staff exists')
def step_impl(context):
    setup_staff(context, context.table)

@given('the following services exist')
def step_impl(context):
    setup_services(context, context.table)

@given('the following service assignments exist')
def step_impl(context):
    setup_service_assignments(context, context.table)

@when('the scheduler runs')
def step_impl(context):
    settings = Settings()
    context.scheduler = Scheduler(
        roster=context.staff,
        service_assignments=context.service_assignments,
        services=context.services,
        settings=settings
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