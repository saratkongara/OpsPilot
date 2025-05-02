from opspilot.models import Settings

def before_scenario(context, scenario):
    #print(f"\nRunning scenario: {scenario.name}")

    context.staff = []
    context.services = []
    context.flights = []
    context.locations = []
    context.travel_times = []
    context.service_assignments = []
    context.settings = Settings()

    context.flight_map = {}
    context.travel_time_map = {}
    context.overlap_map = {}
    context.scheduler = None

    if 'wip' in scenario.effective_tags:
        scenario.skip("Skipping WIP scenario")
    
def before_feature(context, feature):
    if 'wip' in feature.tags:
        feature.skip("Skipping WIP feature")
