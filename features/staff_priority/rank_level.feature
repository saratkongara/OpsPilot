Feature: Staff Rank Level Based Assignment
  As a scheduler
  I want to assign staff based on their rank_level
  So that staff with a lower rank_level (higher priority) are assigned before others when eligible

  Scenario: Staff with lower rank_level is prioritized for assignment
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          | rank_level |
      | 1  | John  | [1]            | ['S']                 | ['08:00-16:00'] | 2          |
      | 2  | Alice | [1]            | ['S']                 | ['08:00-16:00'] | 1          |

    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 1           | 1           | 09:00      | 10:00    | S            |

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

  Scenario: Staff with same rank_level are both assigned when slots are available
    Given the following staff exists:
      | id | name   | certifications | eligible_for_services | shifts          | rank_level |
      | 1  | John   | [1]            | ['S']                 | ['08:00-16:00'] | 1          |
      | 2  | Alice  | [1]            | ['S']                 | ['08:00-16:00'] | 1          |

    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 2           | 1           | 09:00      | 10:00    | S            |

    And the following settings exist:
      | assignment_strategy |
      | Balance Workload    |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |
      | 2        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 2                    |

  Scenario: Staff with higher rank_level is skipped if a lower-ranked eligible staff exists
    Given the following staff exists:
      | id | name   | certifications | eligible_for_services | shifts          | rank_level |
      | 1  | John   | [1]            | ['S']                 | ['08:00-16:00'] | 3          |
      | 2  | Alice  | [1]            | ['S']                 | ['08:00-16:00'] | 1          |
      | 3  | Bob    | [1]            | ['S']                 | ['08:00-16:00'] | 2          |

    And the following services exist:
      | id | name    | certifications | requirement |
      | 1  | Baggage | [1]            | Any         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | staff_count | location_id | start_time | end_time | service_type |
      | 1  | 1          | 2           | 1           | 09:00      | 10:00    | S            |

    And the following settings exist:
      | assignment_strategy |
      | Balance Workload    |
      
    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | []                   |
      | 2        | [1]                  |
      | 3        | [1]                  |
      
    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 2                    |
