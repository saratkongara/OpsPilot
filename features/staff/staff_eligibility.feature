Feature: Staff Eligibility Constraint
  As a scheduler
  I want to ensure that staff are only assigned to services they are eligible for
  So that service type restrictions are respected

  Scenario: Only eligible staff are assigned to service types
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Alice   | [1]            | ['S']                 | ['08:00-12:00'] |
      | 2  | Bob     | [1]            | ['F']                 | ['08:00-12:00'] |
      | 3  | Charlie | [1]            | ['M']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Cleaning | [1]            | All         |

    And the following locations exist:
      | id | name       | location_type |
      | 1  | Terminal A | Terminal      |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1           | 1           | 08:30      | 09:30    | S            |
      | 2  | 1          | 1           | 1           | 09:45      | 10:30    | F            |   

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | [2]                  |
      | 3        | []                   |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |


  Scenario: No staff assigned when none are eligible for the service type
    Given the following staff exists:
      | id | name    | certifications | eligible_for_services | shifts          |
      | 1  | Alice   | [1]            | ['F']                 | ['08:00-12:00'] |
      | 2  | Bob     | [1]            | ['M']                 | ['08:00-12:00'] |
      | 3  | Charlie | [1]            | ['F', 'M']            | ['08:00-12:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Cleaning | [1]            | All         |

    And the following locations exist:
      | id | name   | location_type |
      | 1  | Bay 10 | Bay           |

    And the following service assignments exist:
      | id | service_id | location_id | staff_count | start_time | end_time | service_type |
      | 1  | 1          | 1           | 1           | 08:30      | 09:30    | S            |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | []                   |
      | 3        | []                   |
