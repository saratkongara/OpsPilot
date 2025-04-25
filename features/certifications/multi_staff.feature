Feature: Multi Staff Assignment
  As a scheduler
  I want to assign staff to service assignments
  So that all services are properly staffed

  Scenario: Assign staff when enough qualified staff are available
    Given the following staff exists:
      | id | name   | certifications | eligible_for_services | shifts            | priority_service_id | rank_level |
      | 1  | John   | [1, 2]         | ['S', 'M']            | ['08:00-16:00']   | 1                   | 1          |
      | 2  | Sarah  | [2, 3]         | ['S', 'F']            | ['12:00-20:00']   | 2                   | 2          |
    
    And the following services exist:
      | id | name          | certifications | requirement |
      | 1  | Baggage       | [1, 2]         | All         |
      | 2  | Boarding      | [2, 3]         | All         |
    
    And the following service assignments exist:
      | id | service_id | staff_count | priority | location_id | flight_number | relative_start | relative_end | start_time    | end_time     | service_type | multi_task_limit | exclude_services | needs_equipment | equipment_type | equipment_id |
      | 1  | 1          | 1           | 1.0      | 101         | AA123         | A+30           | D-45         | 08:30         | 09:30        | S            |                  |        []        |    false        |                |              |
      | 2  | 2          | 1           | 2.0      | 205         | AA123         | A+45           | D-30         | 09:45         | 10:45        | S            |                  |        []        |    false        |                |              | 
    
    When the scheduler runs
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | [2]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |