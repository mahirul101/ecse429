Feature: Retrieve a Specific Category
  As a user, I want to retrieve a specific category by its ID so that I can see its details and related items.
  This uses GET on /categories/:id.

  Background: Server is running and categories are set up
    Given the server is running
    And the following categories exist:
      | category_id | name                   | description                 |
      | "601"       | "Subject: Physics"     | "Physics related tasks"     |
      | "602"       | "Subject: Mathematics" | "Mathematics related tasks" |
      | "603"       | "Subject: Literature"  | "Literature related tasks"  |

  # Normal Flow: Successfully retrieve an existing category.
  Scenario Outline: Retrieve an existing category (Normal Flow)
    When the user retrieves the category with id "<category_id>"
    Then the response should contain the category details with id "<category_id>"
    And the category name should be "<name>"
    And the category description should be "<description>"

    Examples:
      | category_id | name                   | description                 |
      | "601"       | "Subject: Physics"     | "Physics related tasks"     |
      | "602"       | "Subject: Mathematics" | "Mathematics related tasks" |

  # Alternate Flow: Retrieve a category with related items.
  Scenario Outline: Retrieve a category with related items (Alternate Flow)
    Given the category with id "<category_id>" has related items
    When the user retrieves the category with id "<category_id>"
    Then the response should include related items for category "<category_id>"
    And the category name should be "<name>"

    Examples:
      | category_id | name                  |
      | "603"       | "Subject: Literature" |

  # Error Flow: Attempt to retrieve a non-existent category.
  Scenario Outline: Retrieve a non-existent category (Error Flow)
    When the user retrieves the category with id "<invalid_category_id>"
    Then the system should respond with status code 404
    And the user should receive an error message "Category not found for id <invalid_category_id>"

    Examples:
      | invalid_category_id |
      | "999"               |
      | "888"               |
