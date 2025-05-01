Feature: Multi-task Service Constraints on a Flight
  As a scheduler
  I want to ensure that multi-task service constraints are enforced on a flight
  So that staff are not overloaded or assigned to incompatible services

  Scenario: Staff is eligible for all multi-task services, but only non-conflicting ones are selected within limit
    Given the following staff exists:
      | id | name  | certifications   | eligible_for_services | shifts          |
      | 1  | Alice | [1,2,3]          | ['M']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | GPU        | [1]            | All         |
      | 2  | Toilet     | [2]            | All         |
      | 3  | Water cart | [3]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL200  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority | multi_task_limit | exclude_services |
      | 1  | 1          | 1           | 1           | FL200         | A+10           | A+30         | M            | 7.0      | 2                | [2]              |
      | 2  | 2          | 1           | 1           | FL200         | A+20           | A+40         | M            | 6.9      | 2                | [1]              |
      | 3  | 3          | 1           | 1           | FL200         | A+30           | A+50         | M            | 7.1      | 2                | []               |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2, 3]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |
      | 3                     | 1                    |

  Scenario: Staff cannot take two services together due to mutual exclusion
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Bob   | [1,2]          | ['M']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | GPU        | [1]            | All         |
      | 2  | Toilet     | [2]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL300  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 45 | Bay           |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority | multi_task_limit | exclude_services |
      | 1  | 1          | 1           | 1           | FL300         | A+10           | A+40         | M            | 5.0      | 2                | [2]              |
      | 2  | 2          | 1           | 1           | FL300         | A+15           | A+45         | M            | 5.1      | 2                | [1]              |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |

  Scenario: Staff is eligible for 3 Multi-task (M) services on the same flight but can only take 2 due to multi_task_limit
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1,2,3]        | ['M']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name        | certifications | requirement |
      | 1  | GPU         | [1]            | All         |
      | 2  | Toilet      | [2]            | All         |
      | 3  | Water cart  | [2]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL200  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 44 | Bay           |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority | multi_task_limit | exclude_services |
      | 1  | 1          | 1           | 1           | FL200         | A+10           | A+40         | M            | 6.0      | 2                | []               |
      | 2  | 2          | 1           | 1           | FL200         | A+20           | A+50         | M            | 6.3      | 2                | []               |
      | 3  | 3          | 1           | 1           | FL200         | A+30           | A+60         | M            | 6.2      | 2                | []               |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1, 3]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
      | 3                     | 1                    |


  Scenario: Staff is limited to only one Multi-task (M) service due to multi_task_limit = 1
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Carol | [1,2]          | ['M']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name      | certifications | requirement |
      | 1  | Toilet    | [1]            | All         |
      | 2  | Water     | [2]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL400  | 09:00        | 11:00          |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 46 | Bay           |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type | priority | multi_task_limit | exclude_services |
      | 1  | 1          | 1           | 1           | FL400         | A+10           | A+40         | M            | 6.0      | 1                | []               |
      | 2  | 2          | 1           | 1           | FL400         | A+20           | A+50         | M            | 5.9      | 1                | []               |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |
