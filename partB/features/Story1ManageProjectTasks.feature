Feature: Manage Project Tasks

  As a student, I want to associate TODOs with projects as tasks, so I can track work items for different initiatives.

  Background: Server is running, projects and TODOs exist
    Given the server is running
    And a project with title "CS101 Coursework" exists
    And TODOs with the following details exist:
      | title              | description       |
      | "Study Chapter 1"  | "read slides 1-4" |
      | "Start assignment" | "assignment 1"    |

  Scenario Outline: Adding existing TODO to project tasks (Normal Flow)
    When adding todo "<todo_title>" to project "CS101 Coursework" tasks
    Then the project tasks include "<todo_title>"
    And the response status is 201

    Examples:
      | todo_title         |
      | "Study Chapter 1"  |
      | "Start assignment" |

  Scenario Outline: Create and add new TODO to project tasks (Alternate Flow)
    When creating new todo "<new_title>" with description "<desc>"
    And adding it to project "CS101 Coursework" tasks
    Then the project tasks include "<new_title>"

    Examples:
      | new_title            | desc                 |
      | "Review assignments" | "Weekly submissions" |
      | "Update notes"       | "Post lecture notes" |

  Scenario Outline: Adding non-existent TODO to project (Error Flow)
    When attempting to add non-existent todo "<invalid_id>" to project
    Then receive error "Could not find thing matching value for id"

    Examples:
      | "9999" |
      | "0000" |