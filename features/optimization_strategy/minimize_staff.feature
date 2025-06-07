Feature: Multi Staff Assignment
  As a scheduler
  I want to assign staff to service assignments
  So that all services are properly staffed based on the assignment strategy

  Scenario: Staff overlap should lead to optimal assignment (minimize staff utilization)
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [2]            | ['S']                 | ['08:00-16:00'] |
      | 2  | Bob   | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name         | certifications | requirement |
      | 1  | Check-In     | [1]            | Any         |
      | 2  | Boarding     | [2]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |
      
    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 1           | 08:30      | 09:30    | S            |
      | 2  | 2          | 1             | 1           | 1           | 10:00      | 10:45    | S            |

    And the following settings exist:
      | assignment_strategy |
      | Minimize Staff      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | [1, 2]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |