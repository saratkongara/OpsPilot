Feature: Service Transition Constraints
  As a scheduler
  I want to prevent staff from being assigned to overlapping services
  So that they have enough time to travel and prepare between assignments

  Scenario: Staff can be assigned to two non-overlapping services
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1]            | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Water cart | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL101  | 08:00        | 09:00          |
      | FL102  | 09:45        | 10:45          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay A  |
      | 2  | Bay B  |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type |
      | 1  | 1          | 1             | 1           | 1           | FL101         | A+10           | D            | S            |
      | 2  | 1          | 1             | 1           | 2           | FL102         | A+10           | A+30         | S            |

    And the following travel times exist:
      | origin_location_id | destination_location_id | travel_minutes |
      | 1                  | 2                       | 10             |

    And the following settings exist:
      | overlap_buffer_minutes | default_travel_time |
      | 5                      | 15                  |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1, 2]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |

  Scenario: Staff cannot be assigned to two overlapping services
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1]            | ['S']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | GPU        | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL201  | 08:00        | 09:00          |
      | FL202  | 09:00        | 10:45          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay X  |
      | 2  | Bay Y  |

    And the following travel times exist:
      | origin_location_id | destination_location_id | travel_minutes |
      | 1                  | 2                       | 30             |
      | 2                  | 1                       | 30             |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | priority | flight_number | relative_start | relative_end | service_type |
      | 1  | 1          | 1             | 1           | 1           | 1.0      | FL201         | A+10           | D-10         | S            |
      | 2  | 1          | 1             | 1           | 2           | 2.0      | FL202         | A+10           | A+40         | S            |

    And the following settings exist:
      | overlap_buffer_minutes | default_travel_time |
      | 5                      | 15                  |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |


  Scenario: Assignments exactly respect travel buffer and are both allowed
    Given the following staff exists:
      | id | name  | department_id | certifications | eligible_for_services | shifts          |
      | 1  | Alice | 1             | [1]            | ['F']                 | ['08:00-16:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Refueling  | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL301  | 08:00        | 09:00          |
      | FL302  | 09:00        | 10:15          |

    And the following locations exist:
      | id | name   |
      | 1  | Bay 1  |
      | 2  | Bay 2  |

    And the following travel times exist:
      | origin_location_id | destination_location_id | travel_minutes |
      | 1                  | 2                       | 25             |
      | 2                  | 1                       | 25             |

    And the following service assignments exist:
      | id | service_id | department_id | staff_count | location_id | flight_number | relative_start | relative_end | service_type |
      | 1  | 1          | 1             | 1           | 1           | FL301         | A+10           | A+40         | F            |
      | 2  | 1          | 1             | 1           | 2           | FL302         | A              | A+40         | F            |

    And the following settings exist:
      | overlap_buffer_minutes | default_travel_time |
      | 5                      | 15                  |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1, 2]               |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 1                    |