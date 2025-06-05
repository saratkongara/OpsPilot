Feature: Flight Priority-Based Assignment
  As a scheduler
  I want to assign staff to higher priority flights first
  So that operationally critical flights are serviced before others
 
  Scenario: Staff assigned to lower-number flight priority (Flight A over Flight B)
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1,2]          | ['S']            | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Water cart | [1]            | All         |
      | 2  | Toilet     | [2]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL100  | 09:00        | 11:00          |
      | FL200  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 44 |
      | 2  | Bay 47 |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | priority | relative_start | relative_end | service_type |
      | 1  | 1          | 1           | 1           | FL100         | 2.1     | A+10           | A+40         | S            |
      | 2  | 2          | 1           | 2           | FL200         | 1.3     | A+10           | A+40         | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |

