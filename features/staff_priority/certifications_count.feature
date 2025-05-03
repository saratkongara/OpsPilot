Feature: Favor Staff with Fewer Certifications
  As a scheduler
  I want to ensure staff with fewer certifications are prioritized for assignment
  So that the solver favors assigning staff with fewer certifications to services

  Scenario: Staff with fewer certifications assigned first
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | John  | [1, 3, 5]      | ['S']                 | ['08:00-16:00'] |
      | 2  | Alice | [2, 4]         | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1, 2]         | Any         |

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

  Scenario: Staff with more certifications are only assigned if no one with fewer certifications is available
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | John  | [1]            | ['S']                 | ['10:00-16:00'] |
      | 2  | Alice | [1, 2]         | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1, 2]         | Any         |

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
      | 1        | []                  |
      | 2        | [1]                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
