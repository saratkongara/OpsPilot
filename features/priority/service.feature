Feature: Service Priority-Based Assignment Within a Flight
  As a scheduler
  I want to assign staff to higher priority services first within the same flight
  So that the most critical ground operations are prioritized

  Scenario: Staff assigned to higher-priority service (lower decimal)
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name          | certifications | requirement |
      | 1  | Water cart    | [1]            | All         |
      | 2  | GPU           | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL500  | 09:00        | 11:00          |

    And the following service assignments exist:
      | id | service_id | staff_count | relative_start | relative_end | service_type | flight_number | priority |
      | 1  | 1          | 1           | A+10           | A+40         | S            | FL500         | 55.1     |
      | 2  | 2          | 1           | A+10           | A+40         | S            | FL500         | 55.9     |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |

  Scenario: Staff assigned to highest priority even if service name is different
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Refueling  | [1]            | All         |
      | 2  | Lavatory   | [1]            | All         |
      | 3  | GPU        | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL600  | 09:00        | 11:00          |

    And the following service assignments exist:
      | id | service_id | staff_count | relative_start | relative_end | service_type | flight_number | priority |
      | 3  | 1          | 1           | A+10           | A+40         | S            | FL600         | 66.5     |
      | 4  | 2          | 1           | A+10           | A+40         | S            | FL600         | 66.2     |
      | 5  | 3          | 1           | A+10           | A+40         | S            | FL600         | 66.8     |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [4]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 3                     | 0                    |
      | 4                     | 1                    |
      | 5                     | 0                    |
