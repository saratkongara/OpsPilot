Feature: Any Certification Requirement Check
  As a scheduler
  I want to verify staff assignment with Any certification requirement
  So that staff with at least one matching certification are assigned

  Scenario: Staff with one matching certification gets assigned
    Given the following staff exists:
      | id | name | certifications | eligible_for_services | shifts          |
      | 1  | John | [1, 3]         | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1, 2]         | Any         |
    
    And the following flights exist:
      | number   | arrival_time | departure_time |
      | AA123    | 08:30        | 10:00          |

    And the following service assignments exist:
      | id | service_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1           | 08:30      | 09:30    | S            |
    
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  Scenario: Staff with no matching certifications not assigned
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Sarah | [3, 4]         | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1, 2]         | Any         |
    
    And the following flights exist:
      | number   | arrival_time | departure_time |
      | AA123    | 08:30        | 10:00          |
      
    And the following service assignments exist:
      | id | service_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1           | 08:30      | 09:30    | S            |
    
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

