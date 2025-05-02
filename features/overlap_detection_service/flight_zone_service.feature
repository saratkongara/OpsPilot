Feature: FlightZone Service Assignment Overlap Detection

  Scenario: FlightZone - No overlap with enough travel gap
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 09:00        | 11:00          |
        | FL200  | 12:00        | 14:00          |

    And the following service assignments exist:
        | id | service_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 101        | 2           | 1.0      | FL100         | A+10           | D-60         | 1           |
        | 2  | 102        | 1           | 1.0      | FL200         | A-15           | A+30         | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |


  Scenario: FlightZone - Overlap with insufficient gap
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 09:00        | 11:00          |
        | FL200  | 10:35        | 12:30          |

    And the following service assignments exist:
        | id | service_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 101        | 2           | 1.0      | FL100         | A+20           | D-30         | 1           |
        | 2  | 102        | 1           | 1.0      | FL200         | A-10           | A+30         | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | [2]                                |
        | 2                     | []                                 |

  Scenario: FlightZone - Tight flight schedule but no overlap
    Given the following flights exist:
        | number | arrival_time | departure_time |
        | FL100  | 08:00        | 09:30          |
        | FL200  | 09:35        | 11:00          |

    And the following service assignments exist:
        | id | service_id | staff_count | priority | flight_number | relative_start | relative_end | location_id |
        | 1  | 201        | 1           | 1.0      | FL100         | A+15           | D-10         | 1           |
        | 2  | 202        | 2           | 1.0      | FL200         | A-5            | A+20         | 2           |

    And the following settings exist:
        | overlap_buffer_minutes | default_travel_time |
        | 5                      | 15                   |

    When the overlap detection service runs

    Then the following overlaps should be detected:
        | service_assignment_id | overlapping_service_assignment_ids |
        | 1                     | []                                 |
        | 2                     | []                                 |
