from typing import Optional, List, Tuple
from opspilot.core import Scheduler, SchedulerResult
from opspilot.models import Department, Service, Flight, TravelTime, Settings, Shift
from datetime import time

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
        # First pass: Schedule each department with its own staff
        for department in self.departments:
            logging.info(f"Running scheduler for department: {department.name}")
            result = self._run_for_department(department)
            
            if result != SchedulerResult.FOUND:
                logging.warning(f"Scheduling failed for department: {department.name}")
                return result
        
        if len(self.departments) == 2:
            # Special case for two departments: try to cross-schedule if one has pending assignments
            dept1, dept2 = self.departments

            if dept1.pending_assignments:
                logging.info(f"Department {dept1.name} has pending assignments")
                available_staff = dept2.available_staff
                if available_staff:
                    dept1.roster = available_staff
                    dept1.service_assignments = dept1.pending_assignments
                    dept1.pending_assignments = []

                    scheduler = Scheduler(
                    department=dept1,
                        services=self.services,
                        flights=self.flights,
                        settings=self.settings,
                    )

                    result = scheduler.run()
            if dept2.pending_assignments:
                logging.info(f"Department {dept2.name} has pending assignments")
                available_staff = dept1.available_staff
                if available_staff:
                    dept2.roster = available_staff
                    dept2.service_assignments = dept2.pending_assignments
                    dept2.pending_assignments = []

                    scheduler = Scheduler(
                        department=dept2,
                        services=self.services,
                        flights=self.flights,
                        settings=self.settings,
                    )

                    result = scheduler.run()
        
        logging.info("All departments scheduled successfully.")
        return SchedulerResult.FOUND
    
    def _run_for_department(self, department: Department) -> SchedulerResult:
        """
        Run the scheduler for a specific department and update its pending_assignments
        and available_staff properties.
        
        Args:
            department: The department to schedule
            
        Returns:
            SchedulerResult: The result of scheduling
        """
        scheduler = Scheduler(
            department=department,
            services=self.services,
            flights=self.flights,
            settings=self.settings,
        )

        result = scheduler.run()

        if result == SchedulerResult.FOUND:
            # Get pending assignments and available staff
            pending_service_assignments = scheduler.get_pending_service_assignments()
            available_staff = scheduler.get_available_staff(travel_time=30)
            logging.info(f"Department: {department.name}, Pending Assignments: {len(pending_service_assignments)}, Available Staff: {len(available_staff)}")
            
            # Update staff shifts with available time intervals
            self._update_staff_shifts_with_available_intervals(available_staff)
            
            # Extract just the staff objects
            available_staff_list = [staff for staff, _ in available_staff]
            
            # Update department properties
            department.allocation_plan = scheduler.get_allocation_plan(location_map=self.settings.location_map)
            department.pending_assignments = pending_service_assignments
            department.available_staff = available_staff_list

        return result
    
    def _update_staff_shifts_with_available_intervals(self, available_staff_data):
        """
        Update staff shifts with their available time intervals.
        
        Args:
            available_staff_data: List of tuples (staff, available_time_intervals)
        """
        for staff, intervals in available_staff_data:
            new_shifts = self._create_shifts_from_intervals(intervals)
            
            # Replace the staff's shifts with the new ones
            staff.shifts = new_shifts
            logging.info(f"Updated shifts for staff {staff.name} with {len(new_shifts)} available time intervals")

    def _create_shifts_from_intervals(self, intervals: List[Tuple[int, int]]) -> List[Shift]:
        """
        Convert time intervals (in minutes) to Shift objects.
        
        Args:
            intervals: List of tuples (start_minute, end_minute) representing available time
            
        Returns:
            List of Shift objects
        """
        shifts = []
        for start_minute, end_minute in intervals:
            # Convert minutes to hours and minutes
            start_hour, start_min = divmod(start_minute, 60)
            end_hour, end_min = divmod(end_minute, 60)
            
            # Handle day overflow (minutes > 1440)
            start_hour %= 24
            end_hour %= 24
            
            # Create new shift
            shift = Shift(
                start_time=time(hour=start_hour, minute=start_min),
                end_time=time(hour=end_hour, minute=end_min)
            )
            shifts.append(shift)
        
        return shifts
