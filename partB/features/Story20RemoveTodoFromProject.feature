Feature: Remove a To-Do from a Project

  As a user, I want to remove a to-do from a project, so I can reassign tasks.

  Background: Server is running with existing to-dos and projects
    Given the server is running
    And projects exist:
      | title    |
      | "Research"   |
    And to-dos in project "Research":
      | title            | doneStatus |
      | "Gather Data"    | false      |

  Scenario Outline: Successfully remove a to-do from a project (Normal Flow)
    When removing todo with title "Gather Data" from project with title "Research"
    Then the system should respond with status code <status_code>
    And the todo should no longer be associated with the project

    Examples:
      | status_code |
      | 200         |

  Scenario Outline: Remove with invalid IDs (Error Flow)
    When removing todo with title "<todo_title>" from project with title "<project_title>"
    Then the system should respond with status code <status_code>

    Examples:
      | todo_title        | project_title | status_code |
      | Does Not Exist    | Research      | 404         |
      
  Scenario Outline: Remove already removed to-do from a project (Alternate Flow)
    Given todo with title "Gather Data" has been removed from project with title "Research"
    When removing todo with title "Gather Data" from project with title "Research" again
    Then the system should respond with status code <status_code>
    And the todo should not be associated with the project

    Examples:
      | status_code |
      | 404         |