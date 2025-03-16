Feature: Retrieve a Specific Category
  As a user, I want to retrieve a specific category by its name so that I can see its details and related items.

  Background: Server is running and categories are set up
    Given the server is running
    And the following categories exist:
      | name                   | description               |
      | Physics                | Physics related tasks     |
      | Mathematics            | Mathematics related tasks |
      | Literature             | Literature related tasks  |

  # Normal Flow: Successfully retrieve an existing category by name.
  Scenario Outline: Retrieve an existing category by name (Normal Flow)
    When the user retrieves the category with name "<name>" categories
    Then the response should contain the category details with name "<name>"
    And the category description should be "<description>"

    Examples:
      | name              | description               |
      | Physics           | Physics related tasks     |
      | Mathematics       | Mathematics related tasks |

  # Alternate Flow: Retrieve a category with related items.
  Scenario Outline: Retrieve a category with related items (Alternate Flow)
    Given the category with name "<name>" has related items
    When the user retrieves the category with name "<name>" categories
    Then the response should include related items for category "<name>"
    And the category name should be "<name>"

    Examples:
      | name          |
      | Music         |

  # Error Flow: Attempt to retrieve a non-existent category.
  Scenario Outline: Retrieve a non-existent category by id (Error Flow)
    When the user retrieves the category with id "<invalid_id>"
    Then the system should respond with status code 404
    And category the user should receive an error message <invalid_id> category

    Examples:
      | invalid_id  |
      | 99999       |
      | 88888       |
