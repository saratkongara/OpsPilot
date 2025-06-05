Feature: Service Priority-Based Assignment Within a Flight
  As a scheduler
  I want to assign staff to higher priority services first within the same flight
  So that the most critical ground operations are prioritized

  Scenario: Staff assigned to higher-priority service (lower decimal)
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name          | certifications | requirement |
      | 1  | Water cart    | [1]            | All         |
      | 2  | GPU           | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL500  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 44 |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | priority | relative_start | relative_end | service_type |
      | 1  | 1          | 1           | 1           | FL500         | 55.1     | A+10           | A+40         | S            |
      | 2  | 2          | 1           | 1           | FL500         | 55.9     | A+10           | A+40         | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
