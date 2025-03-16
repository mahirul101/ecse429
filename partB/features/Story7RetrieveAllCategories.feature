Feature: Retrieve All Categories
  As a user, I want to retrieve all categories so that I can view all available classifications for my todos and projects.

  Background: Server is running and categories are initialized
    Given the server is running
    And the following categories exist:
      | name                  | description                |
      | Subject: Physics      | Physics related tasks      |
      | Subject: Mathematics  | Mathematics related tasks  |
      | Subject: Literature   | Literature related tasks   |

  # Normal Flow: Successfully retrieve all categories.
  Scenario Outline: Retrieve all categories (Normal Flow)
    When the user retrieves all categories
    Then the response should contain at least <min_count> categories
    And each category in the response should include "id", "title", and "description"

    Examples:
      | min_count |
      | 3         |

  # Alternate Flow: Retrieve categories when none exist.
  Scenario: Retrieve categories when none exist (Alternate Flow)
    Given all categories are removed from the system
    When the user retrieves all categories
    Then the response should be an empty list
    And the user receives a notification "No categories found"

  # Error Flow: Attempt to retrieve categories from an invalid endpoint.
  Scenario Outline: Retrieve categories from an invalid endpoint (Error Flow)
    When the user attempts to retrieve categories from an invalid endpoint
    Then the user should receive a 404 status code


