Feature: Multi Department Staff Assignment
  As a scheduler
  I want to assign staff to service assignments from multiple departments
  So that all services are properly staffed based on the assignment strategy

  Scenario: Staff allocation should happen from multiple departments (maximize staff utilization)
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1]            | ['S']                 | ['08:00-10:00'] |
      | 2  | Bob   | 1             | [2]            | ['S']                 | ['14:00-18:00'] |
      | 3  | John  | 2             | [1]            | ['S']                 | ['10:00-14:00'] |
      | 4  | Mary  | 2             | [2]            | ['S']                 | ['09:00-12:00'] |
    
    And the following services exist:
      | id | name         | certifications | requirement |
      | 1  | Check-In     | [1]            | Any         |
      | 2  | Boarding     | [2]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |
      | 2  | Terminal B |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 1           | 08:30      | 09:30    | S            |
      | 2  | 2          | 1             | 1           | 1           | 09:45      | 10:45    | S            |
      | 3  | 1          | 2             | 1           | 2           | 10:30      | 11:30    | S            |
      | 4  | 2          | 2             | 1           | 2           | 14:45      | 15:45    | S            |

    And the following settings exist:
      | assignment_strategy |
      | Turnaround Workload |

    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | [4]                  |
      | 3        | [3]                  |
      | 4        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |
      | 3                     | 1                    |
      | 4                     | 1                    |

  Scenario: Staff allocation across three departments forced by availability
    Given the following staff exists:
      | id | name   | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice  | 1             | [1]            | ['S']                 | ['08:00-09:30'] |
      | 2  | Bob    | 1             | [2]            | ['S']                 | ['13:00-14:30'] |
      | 3  | John   | 2             | [1]            | ['S']                 | ['10:00-12:00'] |
      | 4  | Mary   | 2             | [2]            | ['S']                 | ['15:00-17:00'] |
      | 5  | Henry  | 3             | [1]            | ['S']                 | ['08:00-09:00'] |
      | 6  | Lisa   | 3             | [2]            | ['S']                 | ['16:00-18:00'] |
    
    And the following services exist:
      | id | name         | certifications | requirement |
      | 1  | Check-In     | [1]            | Any         |
      | 2  | Boarding     | [2]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |
      | 2  | Terminal B |
      | 3  | Terminal C |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 1           | 08:15      | 09:15    | S            |
      | 2  | 1          | 1             | 1           | 1           | 10:30      | 11:30    | S            |
      | 3  | 1          | 2             | 1           | 2           | 08:00      | 09:00    | S            |
      | 4  | 2          | 2             | 1           | 2           | 15:30      | 16:30    | S            |
      | 5  | 2          | 3             | 1           | 3           | 13:30      | 14:30    | S            |
      | 6  | 2          | 3             | 1           | 3           | 16:30      | 17:30    | S            |

    And the following settings exist:
      | assignment_strategy |
      | Turnaround Workload |

    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | [5]                  |
      | 3        | [2]                  |
      | 4        | [4]                  |
      | 5        | [3]                  |
      | 6        | [6]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |
      | 3                     | 1                    |
      | 4                     | 1                    |
      | 5                     | 1                    |
      | 6                     | 1                    |