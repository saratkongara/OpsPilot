Feature: Fixed Service Assignment in CommonZone
  As a scheduler
  I want staff assigned to only one Fixed (F) service per CommonZone time slot
  And prevent them from being assigned to other services in overlapping time slots

  Scenario: Staff is eligible for multiple fixed services, but can only be assigned to one with highest priority
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1, 2]         | ['F']                 | ['08:00-11:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Escort   | [1]            | All         |
      | 2  | Cleaning | [2]            | All         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type | priority |
      | 1  | 1          | 1             | 1           | 1           | 08:30      | 09:30    | F            | 2.0      |
      | 2  | 2          | 1             | 1           | 1           | 09:45      | 10:45    | F            | 1.0      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [2]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 0                    |
      | 2                     | 1                    |

  Scenario: Staff is eligible for fixed and non-fixed services, but Fixed has higher priority
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services  | shifts          |
      | 1  | Alice | 1             | [1, 2, 3]      | ['F', 'S']             | ['08:00-11:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Escort   | [1]            | All         |
      | 2  | Cleaning | [2]            | All         |
      | 3  | Guide    | [3]            | All         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type | priority |
      | 1  | 1          | 1             | 1           | 1           | 08:30      | 09:30    | F            | 1.5      |
      | 2  | 2          | 1             | 1           | 1           | 09:45      | 10:45    | F            | 2.0      |
      | 3  | 3          | 1             | 1           | 1           | 10:00      | 10:30    | S            | 2.5      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
      | 3                     | 0                    |

  Scenario: Staff is assigned to same fixed service across two non-overlapping slots
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1]            | ['F']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name     | certifications | requirement |
      | 1  | Escort   | [1]            | All         |
      | 2  | Cleaning | [1]            | All         |

    And the following locations exist:
      | id | name       |
      | 1  | Terminal A |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | start_time | end_time | service_type | priority |
      | 1  | 1          | 1             | 1           | 1           | 08:15      | 09:15    | F            | 1.0      |
      | 2  | 2          | 1             | 1           | 1           | 09:25      | 10:15    | F            | 4.0      |
      | 3  | 1          | 1             | 1           | 1           | 10:30      | 11:30    | F            | 1.5      |
      | 4  | 2          | 1             | 1           | 1           | 11:45      | 12:00    | F            | 2.5      |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1, 3]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |
      | 3                     | 1                    |
      | 4                     | 0                    |
