Feature: Staff Availability Constraints
  As a scheduler
  I want to ensure staff are only assigned when available
  So that shift schedules are respected

  Scenario: Flight zone service - Staff available
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |
    
    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Water cart | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL101  | 09:00        | 11:00          |
    
    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 1          | 1           | 1           | FL101         | A+15           | A+45         | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  Scenario: Flight zone service - Staff unavailable
    Given the following staff exists:
      | id | name | certifications | eligible_for_services | shifts          |
      | 1  | Bob  | [1]            | ['S']                 | ['13:00-17:00'] |
    
    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Water cart | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL102  | 09:00        | 11:00          |
    
    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 1          | 1           | 1           | FL102         | A+15           | A+45         | S            |
    
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

  @overnight
  Scenario: Flight zone overnight shift - Staff available
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Eve   | [3]            | ['S']                 | ['22:00-06:00'] |
  
    And the following services exist:
      | id | name       | certifications | requirement |
      | 3  | Overnight  | [3]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL201  | 01:00        | 03:00          |
    
    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 3          | 1           | 1           | FL201         | A+30           | A+90         | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  @overnight
  Scenario: Flight zone overnight flight - Staff available
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Olivia  | [5]            | ['S']                 | ['22:00-06:00'] |

    And the following services exist:
      | id | name        | certifications | requirement |
      | 5  | Late Loader | [5]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL301  | 23:30        | 01:30          |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 5          | 1           | 1           | FL301         | A+10           | D-10         | S            |
    
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  @overnight
  Scenario: Flight zone overnight shift - Staff unavailable  
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Frank | [3]            | ['S']                 | ['20:00-00:00'] |
  
    And the following services exist:
      | id | name       | certifications | requirement |
      | 3  | Overnight | [3]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL202  | 01:00        | 03:00          |
    
    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 3          | 1           | 1           | FL202         | A+30           | A+90         | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

  @overnight
  Scenario: Flight zone overnight flight - Staff unavailable
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Olivia  | [5]            | ['S']                 | ['18:00-00:30'] |

    And the following services exist:
      | id | name        | certifications | requirement |
      | 5  | Late Loader | [5]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL301  | 23:30         | 01:30         |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | flight_number | relative_start | relative_end | service_type |
      | 1  | 5          | 1           | 1           | FL301         | A+10           | D-10         | S            |
    
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      |     1    | []                   |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

  Scenario: Common zone service - Staff available
    Given the following staff exists:
      | id | name   | certifications | eligible_for_services | shifts          |
      | 1  | Carol  | [2]            | ['S']                 | ['08:00-10:00'] |
    
    And the following services exist:
      | id | name       | certifications | requirement |
      | 2  | Wheelchair | [2]            | All         |

    And the following locations exist:
      | id | name       | location_type |
      | 1  | Terminal A | Terminal      |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 2          | 1           | 1           | 09:50      | 09:55    | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  Scenario: Common zone service - Staff unavailable
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Dave  | [2]            | ['S']                 | ['10:00-12:00'] |
    
    And the following services exist:
      | id | name       | certifications | requirement |
      | 2  | Wheelchair | [2]            | All         |
      
    And the following locations exist:
      | id | name       | location_type |
      | 1  | Terminal A | Terminal      |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 2          | 1           | 1           | 08:40      | 08:45    | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |


  @overnight
  Scenario: Common zone overnight shift - Staff available
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Grace | [4]            | ['S']                 | ['23:00-07:00'] |
    
    And the following services exist:
      | id | name          | certifications | requirement |
      | 4  | Night Patrol  | [4]            | All         |
    
    And the following locations exist:
      | id | name       | location_type |
      | 1  | Zone A     | Zone          |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 4          | 1           | 1           | 02:00      | 04:00    | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  @overnight
  Scenario: Common zone overnight service - Staff available
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Noah    | [6]            | ['S']                 | ['21:00-05:00'] |

    And the following services exist:
      | id | name            | certifications | requirement |
      | 6  | Night Refueling | [6]            | All         |

    And the following locations exist:
      | id | name     | location_type |
      | 1  | Zone A   | Zone          |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 6          | 1           | 1           | 23:45      | 00:30    | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |

  @overnight
  Scenario: Common zone overnight shift - Staff unavailable
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Henry | [4]            | ['S']                 | ['18:00-00:00'] |
    
    And the following services exist:
      | id | name          | certifications | requirement |
      | 4  | Night Patrol  | [4]            | All         |
    
    And the following locations exist:
      | id | name       | location_type |
      | 1  | Zone A     | Zone          |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 4          | 1           | 1           | 01:00      | 05:00    | S            |
    
    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

  @overnight
  Scenario: Common zone overnight service - Staff unavailable
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Noah    | [6]            | ['S']                 | ['18:00-01:30'] |

    And the following services exist:
      | id | name            | certifications | requirement |
      | 6  | Night Refueling | [6]            | All         |

    And the following locations exist:
      | id | name       | location_type |
      | 1  | Zone A     | Zone          |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 6          | 1           | 1           | 23:45      | 02:30    | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
