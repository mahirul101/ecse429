Feature: Update To-Do Status

  As a user, I want to update the completion status of a to-do, so I can track my progress.

  Background: Server is running with existing to-dos
    Given the server is running
    And existing to-dos:
      | id | title            | completed |
      | 1  | "Write Report"   | false     |
      | 2  | "Submit Proposal" | true      |

  Scenario Outline: Successfully update to-do status (Normal Flow)
    When updating to-do "<todo_id>" status to "<new_status>"
    Then the system should respond with status code 200
    And the to-do status should now be "<new_status>"

    Examples:
      | todo_id | new_status |
      | 1       | true       |
      | 2       | false      |

  Scenario Outline: Update non-existent to-do (Error Flow)
    When updating to-do "<invalid_todo_id>" status to "true"
    Then the system should respond with status code 404
    And receive error message "To-Do not found"

    Examples:
      | invalid_todo_id |
      | 999             |
      | invalid         |

  Scenario Outline: Invalid status value (Error Flow)
    When updating to-do "1" status to "<invalid_status>"
    Then the system should respond with status code 400
    And receive error message "Invalid status value"

    Examples:
      | invalid_status |
      | "completed"    |
      | "done"         |
