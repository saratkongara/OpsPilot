Feature: Single Service Assignment with Priorities
  As a scheduler
  I want to assign staff to only one Single (S) service per flight
  And ensure that the highest priority service is selected

  Scenario: Staff is eligible for multiple Single (S) services on a flight but only the highest priority is assigned
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | GPU        | [1]            | All         |
      | 2  | Toilet     | [1]            | All         |
      | 3  | Water cart | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL100  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 44 |

    And the following service assignments exist:
      | id | service_id | staff_count |location_id | flight_number | relative_start | relative_end | service_type | priority |
      | 1  | 1          | 1           | 1          | FL100         | A+10           | A+40         | S            | 7.2      |
      | 2  | 2          | 1           | 1          | FL100         | A+20           | A+50         | S            | 7.1      |
      | 3  | 3          | 1           | 1          | FL100         | A+30           | A+60         | S            | 7.3      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |
      | 3                     | 0                    |
