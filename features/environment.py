def before_scenario(context, scenario):
    #print(f"\nRunning scenario: {scenario.name}")

    context.staff = []
    context.services = []
    context.flights = []
    context.locations = []
    context.service_assignments = []

    if 'wip' in scenario.effective_tags:
        scenario.skip("Skipping WIP scenario")
    
def before_feature(context, feature):
    if 'wip' in feature.tags:
        feature.skip("Skipping WIP feature")
