Feature: CommonZone Service Assignment Overlap Detection

  Scenario: Service assignments have no overlap with sufficient travel gap
    Given the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | start_time | end_time | location_id |
        | 1  | 301        | 1             | 1           | 1.0      | 08:00      | 09:00    | 1           |
        | 2  | 302        | 1             | 1           | 1.0      | 09:15      | 10:00    | 2           |

    And the following travel times exist:
        | origin_location_id | destination_location_id | travel_minutes |
        | 1                  | 2                       | 15             |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                  |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |

  Scenario: Service assignments touch but don't overlap
    Given the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | start_time | end_time | location_id |
        | 1  | 305        | 1             | 1           | 1.0      | 08:00      | 09:00    | 1           |
        | 2  | 306        | 1             | 1           | 1.0      | 09:10      | 10:00    | 2           |

    And the following travel times exist:
        | origin_location_id | destination_location_id | travel_minutes |
        | 1                  | 2                       | 15             |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                  |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |

  Scenario: Service assignments overlap due to insufficient travel buffer
    Given the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | start_time | end_time | location_id |
        | 1  | 303        | 1             | 2           | 1.0      | 08:00      | 09:00    | 1           |
        | 2  | 304        | 1             | 1           | 1.0      | 09:05      | 10:00    | 2           |

    And the following travel times exist:
        | origin_location_id | destination_location_id | travel_minutes |
        | 1                  | 2                       | 15             |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                  |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | [2]                                |
        | 2                     | []                                 |

  Scenario: Overlap map records overlap dependencies in forward direction only
    Given the following service assignments exist:
        | id | service_id | department_id | staff_count | priority | start_time | end_time | location_id |
        | 1  | 307        | 1             | 1           | 1.0      | 08:00      | 09:00    | 1           |
        | 2  | 308        | 1             | 1           | 1.0      | 09:00      | 09:30    | 2           |
        | 3  | 309        | 1             | 1           | 1.0      | 09:30      | 10:15    | 3           |

    And the following travel times exist:
        | origin_location_id | destination_location_id | travel_minutes |
        | 1                  | 2                       | 15             |
        | 2                  | 1                       | 15             |
        | 2                  | 3                       | 15             |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | [2]                                |
        | 2                     | [3]                                |
        | 3                     | []                                 |
