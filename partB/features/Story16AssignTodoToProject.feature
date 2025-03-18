Feature: Assign a To-Do to a Project

  As a user, I want to assign a to-do to a project, so I can organize my tasks effectively.

  Background: Server is running with existing to-dos and projects
    Given the server is running
    And existing to-dos:
      | id | title           | doneStatus |
      | 1  | "Finish Report" | false      |
    And existing projects assigned to todo:
      | project_title  | active | todo_title      |
      | "Work Project" | true   | "Finish Report" |

  Scenario Outline: Successfully assign a to-do to a project (Normal Flow)
    When assigning to-do "<todo_title>" to project "<project_title>"
    Then the system should respond with status code 201
    And the to-do "<todo_title>" should now belong to the project "<project_title>"

    Examples:
      | todo_title    | project_title |
      | Finish Report | Work Project  |

  Scenario Outline: Assign a non-existent to-do (Error Flow)
    When assigning invalid to-do "<invalid_todo>" to project "Work Project"
    Then the system should respond with status code 404

    Examples:
      | invalid_todo |
      | 999          |
      | invalid      |

  Scenario Outline: Assign to a non-existent project (Error Flow)
    When assigning to-do "Finish Report" to invalid project "<invalid_project>"
    Then the system should respond with status code 404
    Then receive error "Could not find parent thing for relationship projects/<invalid_project>/tasks"

    Examples:
      | invalid_project |
      | 999             |
      | invalid         |
