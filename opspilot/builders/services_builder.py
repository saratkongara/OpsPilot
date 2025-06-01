from opspilot.models import Service, CertificationRequirement

class ServicesBuilder:
    def __init__(self, services_list: list[any]):
        self.services_list = services_list

    def build(self):
        services = []

        for service_data in self.services_list:
            service = Service(
                id=service_data.logId,
                name=service_data.equipmentType,
                certifications=service_data.certificates,
                certification_requirement=CertificationRequirement.ANY,
            )
            services.append(service)

        return services

    def __repr__(self):
        return f"ServicesBuilder(services_list={self.services_list})"