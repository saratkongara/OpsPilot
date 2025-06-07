from typing import Optional, List
from opspilot.core import Scheduler, SchedulerResult
from opspilot.models import Department, Service, Flight, TravelTime, Settings

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class MultiScheduler:
    def __init__(
        self,
        departments: List[Department],
        services: List[Service],
        flights: List[Flight],
        travel_times: Optional[List[TravelTime]] = [],
        settings: Optional[Settings] = Settings(),
    ):
        """
        Initialize the scheduler with input data.
        
        Args:
            departments: The list of departments containing staff, service assignments, and travel times
            services: List of services with their certification requirements
            flights: List of flights to consider in scheduling
            travel_times: Optional list of travel times between departments
            settings: Configuration parameters for scheduling
        """
        self.departments = departments
        self.services = services
        self.flights = flights

        self.travel_times = travel_times
        self.settings = settings
    

    def run(self) -> SchedulerResult:
        """Run the scheduler for each department."""
        for department in self.departments:
            logging.info(f"Running scheduler for department: {department.name}")
            result = self._run_for_department(department)
            
            if result != SchedulerResult.FOUND:
                logging.warning(f"Scheduling failed for department: {department.name}")
                return result
        
        logging.info("All departments scheduled successfully.")
        return SchedulerResult.FOUND
    
    def _run_for_department(self, department: Department) -> SchedulerResult:
        scheduler = Scheduler(
            department=department,
            services=self.services,
            flights=self.flights,
            settings=self.settings,
        )

        return scheduler.run()

        