Feature: Assign a To-Do to a Project

  As a user, I want to assign a to-do to a project, so I can organize my tasks effectively.

  Background: Server is running with existing to-dos and projects
    Given the server is running
    And existing to-dos:
      | id | title            | completed |
      | 1  | "Finish Report"  | false     |
    And existing projects:
      | id | title            | active |
      | 10 | "Work Project"   | true  |

  Scenario Outline: Successfully assign a to-do to a project (Normal Flow)
    When assigning to-do "<todo_id>" to project "<project_id>"
    Then the system should respond with status code 201
    And the to-do should now belong to the project

    Examples:
      | todo_id | project_id |
      | 1       | 10         |

  Scenario Outline: Assign a non-existent to-do (Error Flow)
    When assigning to-do "<invalid_todo_id>" to project "10"
    Then the system should respond with status code 404
    And receive error message "To-Do not found"

    Examples:
      | invalid_todo_id |
      | 999             |
      | invalid         |

  Scenario Outline: Assign to a non-existent project (Error Flow)
    When assigning to-do "1" to project "<invalid_project_id>"
    Then the system should respond with status code 404
    And receive error message "Project not found"

    Examples:
      | invalid_project_id |
      | 999               |
      | invalid           |
