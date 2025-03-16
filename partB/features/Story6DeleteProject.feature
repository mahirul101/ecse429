Feature: Delete a Project
  As a user, I want to delete a project by its ID so that I can remove projects that are no longer active.

  Background: Server is running and initial projects are set up
    Given the server is running
    And the following projects exist:
      | project_id | title                  | description                   | active |
      | "701"      | "Physics Lab Report"   | "Lab report for physics"      | true   |
      | "702"      | "Calculus Assignment"  | "Assignment for calculus"     | true   |
      | "703"      | "Essay on Shakespeare" | "Literature essay"            | true   |

  # Normal Flow: Successfully delete an existing project.
  Scenario Outline: Delete an existing project (Normal Flow)
    When the user deletes the project with id "<project_id>"
    Then the project with id "<project_id>" should no longer exist in the system
    And the user receives a confirmation message "Project deleted successfully"

    Examples:
      | project_id |
      | "701"      |
      | "702"      |

  # Alternate Flow: Delete a project that has associated tasks or categories.
  Scenario Outline: Delete a project with associated relationships (Alternate Flow)
    Given the project with id "<project_id>" is linked to tasks and categories
    When the user deletes the project with id "<project_id>"
    Then the project with id "<project_id>" and its associations should be removed from the system
    And the user receives a confirmation message "Project and associations deleted successfully"

    Examples:
      | project_id |
      | "703"      |

  # Error Flow: Attempt to delete a non-existent project.
  Scenario Outline: Delete a non-existent project (Error Flow)
    When the user attempts to delete a project with id "<invalid_project_id>"
    Then the user should receive an error message "Project not found for id <invalid_project_id>"

    Examples:
      | invalid_project_id |
      | "9999"             |
      | "8888"             |