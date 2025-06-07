Feature: FlightZone Service Assignment Overlap Detection

  Scenario: Service assignments have no overlap with enough travel gap
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 09:00        | 11:00          |
        | FL200  | 11:00        | 14:00          |

    And the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 101        | 1             | 2           | 1.0      | FL100         | A+10           | D-20         | 1           |
        | 2  | 102        | 1             | 1           | 1.0      | FL200         | A              | A+30         | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                  |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |

  Scenario: Service assignments overlap due to insufficient travel buffer
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 09:00        | 10:30          |
        | FL200  | 10:40        | 12:00          |

    And the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 103        | 1             | 1             | 1.0         | FL100    | A+15          | D-5            | 1           |
        | 2  | 104        | 1             | 1             | 1.0         | FL200    | A-10          | A+20           | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | [2]                                |
        | 2                     | []                                 |

  Scenario: Service assignments tight schedule due to exact buffer
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 08:00        | 09:00          |
        | FL200  | 09:10        | 10:30          |

    And the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 105        | 1             | 1           | 1.0      | FL100         | A+15           | D-5          | 1           |
        | 2  | 106        | 1             | 1           | 1.0      | FL200         | A-5            | A+15         | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |

  Scenario: Overlap map records overlap dependencies in forward direction only
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 08:00        | 09:30          |
        | FL200  | 09:35        | 11:00          |
        | FL300  | 09:20        | 11:15          |

    And the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 109        | 1             | 1           | 1.0      | FL100         | A+15           | D-5          | 1           |
        | 2  | 110        | 1             | 1           | 1.0      | FL200         | A-10           | A+20         | 2           |
        | 3  | 111        | 1             | 1           | 1.0      | FL300         | A-5            | A+15         | 3           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                  |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | [2,3]                              |
        | 2                     | []                                 |
        | 3                     | [2]                                |
