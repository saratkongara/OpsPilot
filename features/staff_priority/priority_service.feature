Feature: Staff Priority Service ID Based Assignment
  As a scheduler
  I want to assign staff based on priority_service_id
  So that staff with a strong preference for a service (based on priority_service_id) are assigned first

  Scenario: Staff with higher priority_service_id is assigned first
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          | priority_service_id |
      | 1  | John  | [1, 2]         | ['S']                 | ['08:00-16:00'] | 2                   |
      | 2  | Alice | [1, 2, 3]      | ['S']                 | ['08:00-16:00'] | 1                   |
    
    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Baggage  | [1]            | Any         |

    And the following locations exist:
      | id | name       | location_type |
      | 1  | Terminal A | Terminal      |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1           | 1           | 08:30      | 09:30    | S            |
    
    And the following settings exist:
      | assignment_strategy |
      | Balance Workload    |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | [1]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  Scenario: Staff with lower priority_service_id not assigned first
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          | priority_service_id |
      | 1  | John  | [1, 2]         | ['S']                 | ['08:00-16:00'] | 2                   |
      | 2  | Alice | [1, 2]         | ['S']                 | ['08:00-16:00'] | 1                   |
    
    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Refueling| [2]            | Any         |

    And the following locations exist:
      | id | name       | location_type |
      | 1  | Terminal A | Terminal      |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1           | 1           | 08:30      | 09:30    | S            |
    
    And the following settings exist:
      | assignment_strategy |
      | Balance Workload    |
      
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | [1]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
