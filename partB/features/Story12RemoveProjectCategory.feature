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

  Scenario: Remove a category from a project (Normal Flow)
    When removing category "1" from project "1"
    Then the system should respond with status code 200
    And the category "1" should not be assigned to project "1"

  Scenario: Remove a non-existent category from a project (Error Flow)
    When attempting to remove category "999" from project "1"
    Then receive category removal error "Category not found"

  Scenario: Remove a category from a non-existent project (Error Flow)
    When attempting to remove category "1" from project "999"
    Then receive project removal error "Project not found"

  Scenario: Remove a category that is not assigned to the project (Alternate Flow)
    Given the category "1" is not assigned to project "1"
    When removing category "1" from project "1"
    Then the system should respond with status code 200
    And the category "1" should not be assigned to project "1"