Feature: Create a New Category
  As a user, I want to create a new category without providing an ID so that I can classify my tasks and projects easily.
  This uses POST on /categories.

  Background:
    Given the server is running
    And the system is reset to its initial state

  # Normal Flow: Successfully create a new category.
  Scenario Outline: Create a new category successfully (Normal Flow)
    When the user creates a new category with name "<name>" and description "<description>"
    Then the system should respond with status code 201 and generate a new category id
    And the category with name "<name>" and description "<description>" should be present in the system
    And the user receives a confirmation message "Category created successfully"

    Examples:
      | name               | description                      |
      | "Subject: Chemistry" | "Chemistry related tasks"      |
      | "Subject: History"   | "History related projects"     |

  # Alternate Flow: Attempt to create a duplicate category.
  Scenario Outline: Attempt to create a duplicate category (Alternate Flow)
    Given a category with name "<name>" already exists
    When the user creates a new category with name "<name>" and description "<description>"
    Then the system should respond with status code 201 and generate a new category id
    And the category with name "<name>" should be successfully created again

    Examples:
      | name              | description                  |
      | "Subject: Biology"| "Biology related topics"     |

  # Error Flow: Create a category with missing required field.
  Scenario Outline: Create a category with missing required field (Error Flow)
    When the user attempts to create a new category with name <name> and description <description>
    Then the system should respond with status code 400
    And the user should receive an error message <missing_field>

    Examples:
      | name                 | description        | missing_field  |
      | ""                   | "Some description" | "title"        |