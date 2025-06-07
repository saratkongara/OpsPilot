Feature: Staff Count Constraint
  As a scheduler
  I want to ensure that no more than the required number of staff are assigned to a service
  So that the staff_count constraint is respected

  Scenario: Only limited staff assigned even when multiple are eligible
    Given the following staff exists:
      | id | name   | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice  | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |
      | 2  | Bob    | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |
      | 3  | Charlie| 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Security | [1, 2]         | All         |
  
    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | location_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 2           | 08:30      | 09:30    | S            |

    When the scheduler runs

    Then the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 2                    |

  Scenario: No staff assigned when staff_count is zero
    Given the following staff exists:
      | id | name   | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice  | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |
      | 2  | Bob    | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Security | [1, 2]         | All         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | location_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 0           | 08:30      | 09:30    | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | []                   |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |

  Scenario: Service remains understaffed when not enough fully qualified staff are available
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1, 2]         | ['S']                 | ['08:00-16:00'] |
      | 2  | Bob   | 1             | [2]            | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Cleaning| [1, 2]         | All         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | location_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1             | 1           | 2           | 08:30      | 09:30    | S            |

    When the scheduler runs
    
    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | []                   |
    
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
