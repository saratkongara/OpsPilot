from opspilot.models import Shift, ServiceType, Staff
from .parser_util import ParserUtil

class RosterBuilder:
    def __init__(self, resources: list[any]):
        self.resources = resources

    def build(self):
        roster = []

        for resource in self.resources:
            id = resource.resource_id
            name = resource.member_name
            department_id = resource.department_id
            certifications = resource.qualification_certificates
            role_code = resource.role_code

            start_time = ParserUtil.extract_time(resource.shift_start_time)
            end_time = ParserUtil.extract_time(resource.shift_end_time)
            shifts = [Shift(start_time=start_time, end_time=end_time)]

            staff = Staff(
                id=id,
                name=name,
                department_id=department_id,
                shifts=shifts,
                certifications=certifications,
                eligible_for_services=[ServiceType.SINGLE, ServiceType.FIXED, ServiceType.MULTI_TASK],
                role_code=role_code,
            )

            roster.append(staff)

        return roster

    def __repr__(self):
        return f"RosterBuilder(resources={self.resources})"