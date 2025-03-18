Feature: Remove a To-Do from a Project

  As a user, I want to remove a to-do from a project, so I can reassign tasks.

  Background: Server is running with existing to-dos and projects
    Given the server is running
    And existing projects:
      | id | title         | active |
      | 2  | "Research"    | true  |
    And to-dos in project "Research":
      | id | title            | completed |
      | 5  | "Gather Data"    | false     |

  Scenario Outline: Successfully remove a to-do from a project (Normal Flow)
    When removing to-do "<todo_id>" from project "<project_id>"
    Then the system should respond with status code 200
    And the to-do should no longer be associated with the project

    Examples:
      | todo_id | project_id |
      | 5       | 2         |

  Scenario Outline: Remove a non-existent to-do (Error Flow)
    When removing to-do "<invalid_todo_id>" from project "2"
    Then the system should respond with status code 404
    And receive error message "To-Do not found"

    Examples:
      | invalid_todo_id |
      | 999             |
      | invalid         |

  Scenario Outline: Remove from a non-existent project (Error Flow)
    When removing to-do "5" from project "<invalid_project_id>"
    Then the system should respond with status code 404
    And receive error message "Project not found"

    Examples:
      | invalid_project_id |
      | 999               |
      | invalid           |
