Feature: CommonZone Service Assignment Overlap Detection

  Scenario: Detect overlapping service assignments in CommonZone
    Given the following service assignments exist:
      | id  | service_id | staff_count | priority | start_time | end_time | location_id |
      | 1   | 101        | 2           | 1.0      | 08:00      | 10:00    | 1           |
      | 2   | 102        | 1           | 1.0      | 09:00      | 11:00    | 2           |
    
    And the following travel times exist:
      | origin_location_id | destination_location_id | travel_minutes |
      | 1                  | 2                       | 10             |
      | 2                  | 1                       | 10             |
    
    And the following settings exist:
      | overlap_buffer_minutes | default_travel_time | assignment_strategy |
      | 15                     | 5                   | Balance Workload    |
    
    When the overlap detection service runs
    
    Then the following overlaps should be detected:
      | service_assignment_id | overlapping_service_assignment_ids |
      | 1                      | [2]                               |
      | 2                      | []                                |

