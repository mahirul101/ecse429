Feature: Remove Project Category

  As a student, I want to remove a category from a project, so I can manage my project categories effectively.

  Background: Server is running
    Given the server is running
    And existing project:
      | id | title                | completed | active | description            |
      | 1  | "Complete project A" | false     | true   | "Ongoing project work" |
    And existing category:
      | id | title      | description            |
      | 1  | "Homework" | "Category for homework" |
    And the category "1" is assigned to project "1"

  Scenario Outline: Remove a category from a project (Normal Flow)
    When removing category "<category_id>" from project "<project_id>"
    Then the system should respond with status code 200
    And the category "<category_id>" should not be assigned to project "<project_id>"

    Examples:
      | category_id | project_id |
      | 1           | 1          |

  Scenario Outline: Remove a non-existent category from a project (Error Flow)
    When attempting to remove category "<invalid_category_id>" from project "<project_id>"
    Then receive category removal error "<error_message>"

    Examples:
      | invalid_category_id | project_id | error_message      |
      | 999                 | 1          | Category not found |

  Scenario Outline: Remove a category from a non-existent project (Error Flow)
    When attempting to remove category "<category_id>" from project "<invalid_project_id>"
    Then receive project removal error "<error_message>"

    Examples:
      | category_id | invalid_project_id | error_message     |
      | 1           | 999                | Project not found |

  Scenario Outline: Remove a category that is not assigned to the project (Alternate Flow)
    Given the category "<category_id>" is not assigned to project "<project_id>"
    When removing category "<category_id>" from project "<project_id>"
    Then the system should respond with status code 200
    And the category "<category_id>" should not be assigned to project "<project_id>"

    Examples:
      | category_id | project_id |
      | 1           | 1          |