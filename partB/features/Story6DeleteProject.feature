Feature: Delete a Project
  As a user, I want to delete a project so that I can remove projects that are no longer active.

  Background: Server is running and initial projects are set up
    Given the server is running
    And the following projects exist:
      | title                  | description                   | active |
      | Physics Lab Report     | Lab report for physics        | True   |
      | Calculus Assignment    | Assignment for calculus       | True   |
      | Essay on Shakespeare   | Literature essay              | True   |

  # Normal Flow: Successfully delete an existing project.
  Scenario Outline: Delete an existing project (Normal Flow)
    When the user deletes the project with id "<title>"
    Then the project with id "<title>" should no longer exist in the system

    Examples:
      | title              |
      | Physics Lab Report |
      | Calculus Assignment|

  # Alternate Flow: Delete a project that has associated tasks and categories.
  Scenario Outline: Delete a project with associated relationships (Alternate Flow)
    Given the project with title "<title>" has tasks associated with it
    And the project with title "<title>" has categories associated with it
    When the user deletes the project with id "<title>"
    Then the project with id "<title>" should no longer exist in the system
    And the relationships between the project and its tasks should be removed
    And the relationships between the project and its categories should be removed

    Examples:
      | title               |
      | Essay on Shakespeare|

  # Error Flow: Attempt to delete a non-existent project.
  Scenario Outline: Delete a non-existent project (Error Flow)
    When the user attempts to delete a project with id "<invalid_project_id>"
    Then the user should receive an error message "Project not found for id <invalid_project_id>"

    Examples:
      | invalid_project_id |
      | "9999"             |
      | "8888"             |