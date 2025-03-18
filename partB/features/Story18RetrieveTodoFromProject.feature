Feature: Retrieve To-Do from Project

  As a user, I want to retrieve all to-dos associated with a project, so I can view and manage tasks for that project.

  Background: Server is running with existing projects and to-dos
    Given the server is running
    And existing projects with title and active status:
      | title          | active |
      | "Work Project" | true   |
    And existing to-dos:
      | title          | doneStatus |
      | "Write Report" | false      |
    And the to-do "Write Report" is assigned to project "Work Project"

  Scenario Outline: Successfully retrieve to-dos from a project (Normal Flow)
    When retrieving to-dos from project "<project_title>"
    Then the system should respond with status code 200
    And the response should contain:
      | title          | doneStatus |
      | "Write Report" | false      |

    Examples:
      | project_title |
      | Work Project  |

  Scenario Outline: Retrieve to-dos from a non-existent project (Error Flow)
    When retrieving to-dos from project "<invalid_project>"
    # BUG: The system should respond with status code 404 (from part A)
    Then the system should respond with status code 200

    Examples:
      | invalid_project |
      | 999             |
      | invalid         |