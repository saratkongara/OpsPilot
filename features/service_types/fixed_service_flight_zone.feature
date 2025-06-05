Feature: Fixed Service Assignment in FlightZone
  As a scheduler
  I want staff assigned to only one Fixed (F) service per flight
  And prevent them from being assigned to other services on the same flight

  Scenario: Staff is eligible for multiple fixed services on a flight, but can only be assigned to one Fixed (F) service
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1, 2]         | ['F']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Refuel   | [1]            | All         |
      | 2  | Baggage  | [2]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL101  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 12 |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority |
      | 1  | 1          | 1           | 1           | FL101         | A+10           | A+40         | F            | 8.0      |
      | 2  | 2          | 1           | 1           | FL101         | D-40           | D-20         | F            | 7.5      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |

  Scenario: Staff is eligible for multiple service types, and Fixed service has higher priority
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1, 2, 3]       | ['F', 'S']             | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Refuel     | [1]            | All         |
      | 2  | GPU        | [2]            | All         |
      | 3  | Water cart | [3]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL200  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 44 |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority |
      | 1  | 1          | 1           | 1           | FL200         | A+10           | A+30         | F            | 6.5      |
      | 2  | 2          | 1           | 1           | FL200         | A+50           | A+60         | F            | 7.0      |
      | 3  | 3          | 1           | 1           | FL200         | D-40           | D-20         | S            | 6.8      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
      | 3                     | 0                    |

  Scenario: Staff is assigned to a Fixed service on the first flight, and is assigned the same service on the second flight
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['F']                 | ['08:00-14:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Refuel   | [1]            | All         |
      | 2  | Baggage  | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL300  | 09:00        | 10:00          |
      | FL301  | 11:00        | 12:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 10 |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority |
      | 1  | 1          | 1           | 1           | FL300         | A+10           | A+30         | F            | 1.0      |
      | 2  | 2          | 1           | 1           | FL300         | D-40           | D-10         | F            | 2.0      |
      | 3  | 1          | 1           | 1           | FL301         | A+10           | A+30         | F            | 3.0      |
      | 4  | 2          | 1           | 1           | FL301         | D-40           | D-10         | F            | 4.0      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1, 3]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
      | 3                     | 1                    |
      | 4                     | 0                    |
