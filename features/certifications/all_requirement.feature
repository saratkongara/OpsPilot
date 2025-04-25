Feature: All Certification Requirement Check
  As a scheduler
  I want to verify staff assignment with All certification requirement
  So that only staff with all required certifications are assigned

  Scenario: Staff with all required certifications gets assigned
    Given the following staff exists:
      | id | name | certifications | eligible_for_services | shifts          |
      | 1  | John | [1, 2, 3]      | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Security | [1, 2]         | All         |
    
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

  Scenario: Staff missing one certification not assigned
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Sarah | [1, 3]         | ['S']                 | ['08:00-16:00'] |
    
    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Security | [1, 2]         | All         |
    
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