@wip
Feature: Flight Priority-Based Assignment
  As a scheduler
  I want to assign staff to higher priority flights first
  So that operationally critical flights are serviced before others
 
  Scenario: Staff assigned to lower-number flight priority (Flight A over Flight B)
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | Water cart | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL100  | 09:00        | 11:00          |
      | FL200  | 09:00        | 11:00          |

    And the following service assignments exist:
      | id | service_id | staff_count | relative_start | relative_end | service_type | flight_number | priority |
      | 1  | 1          | 1           | A+10           | A+40         | S            | FL100         | 22.1     |
      | 2  | 1          | 1           | A+10           | A+40         | S            | FL200         | 44.3     |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [1]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 1                     | 1                    |
      | 2                     | 0                    |

  Scenario: Staff assigned to lower-number flight priority (Flight B over Flight A)
    Given the following staff exists:
      | id | name  | certifications | eligible_for_services | shifts          |
      | 1  | Alice | [1]            | ['S']                 | ['08:00-12:00'] |

    And the following services exist:
      | id | name       | certifications | requirement |
      | 1  | GPU        | [1]            | All         |

    And the following flights exist:
      | number | arrival_time | departure_time |
      | FL300  | 09:00        | 11:00          |
      | FL400  | 09:00        | 11:00          |

    And the following service assignments exist:
      | id | service_id | staff_count | relative_start | relative_end | service_type | flight_number | priority |
      | 3  | 1          | 1           | A+10           | A+40         | S            | FL300         | 88.2     |
      | 4  | 1          | 1           | A+10           | A+40         | S            | FL400         | 11.4     |

    When the scheduler runs

    Then the assignments should be:
      | staff_id | assigned_service_ids |
      | 1        | [4]                  |

    And the service coverage should be:
      | service_assignment_id | assigned_staff_count |
      | 3                     | 0                    |
      | 4                     | 1                    |
