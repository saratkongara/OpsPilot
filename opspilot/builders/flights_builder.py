from opspilot.models import Flight
from datetime import datetime
from .parser_util import ParserUtil

class FlightsBuilder:
    def __init__(self, flights_with_tasks: list[any]):
        self.flights_with_tasks = flights_with_tasks

    def build(self):
        flights = []

        for flight_with_tasks in self.flights_with_tasks:
            arrival_time = flight_with_tasks.final_sta
            departure_time = flight_with_tasks.final_std

            if flight_with_tasks.flight_splited_for == 'departure':
                flight_number = flight_with_tasks.flight_departure_no 
            elif flight_with_tasks.flight_splited_for == 'arrival':
                flight_number = flight_with_tasks.flight_arrival_no
            else:
                flight_number = f'{flight_with_tasks.flight_arrival_no}-{flight_with_tasks.flight_departure_no}'

            flight = Flight(number=flight_number,
                            arrival_time=ParserUtil.extract_time(arrival_time),
                            departure_time=ParserUtil.extract_time(departure_time))

            flights.append(flight)
        
        return flights

    def __repr__(self):
        return f"FlightsBuilder(flights_with_tasks={self.flights_with_tasks})"