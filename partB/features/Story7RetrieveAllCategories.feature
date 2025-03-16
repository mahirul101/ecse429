Feature: Retrieve All Categories
  As a user, I want to retrieve all categories so that I can view all available classifications for my todos and projects.
  This uses GET on /categories.

  Background: Server is running and categories are initialized
    Given the server is running
    And the following categories exist:
      | category_id | name                  | description                |
      | "601"       | "Subject: Physics"    | "Physics related tasks"    |
      | "602"       | "Subject: Mathematics"| "Mathematics related tasks"|
      | "603"       | "Subject: Literature" | "Literature related tasks" |

  # Normal Flow: Successfully retrieve all categories.
  Scenario Outline: Retrieve all categories (Normal Flow)
    When the user retrieves all categories
    Then the response should contain at least <min_count> categories
    And each category in the response should include "category_id", "name", and "description"
    
    Examples:
      | min_count |
      | 3         |

  # Alternate Flow: Retrieve categories when none exist.
  Scenario Outline: Retrieve categories when none exist (Alternate Flow)
    Given all categories are removed from the system
    When the user retrieves all categories
    Then the response should be an empty list
    And the user receives a notification "No categories found"
    
    Examples:
      | dummy |
      | "X"   |

  # Error Flow: Attempt to retrieve categories when the server is down.
  Scenario Outline: Retrieve categories with server down (Error Flow)
    Given the server is not running
    When the user attempts to retrieve all categories
    Then the user should receive an error message "Service Unavailable"
    
    Examples:
      | error_message         |
      | "Service Unavailable" |
