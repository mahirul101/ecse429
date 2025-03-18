Feature: Retrieve Projects Associated with a Category

  As a user, I want to retrieve all projects under a category, so I can manage grouped projects.

  Background: Server is running with existing projects and categories
    Given the server is running
    And existing categories:
      | id | name          |
      | 3  | "Personal"    |
    And projects under category "Personal":
      | id | title       | active |
      | 7  | "Home Renovation" | true  |

  Scenario Outline: Successfully retrieve projects of a category (Normal Flow)
    When retrieving projects under category "<category_id>"
    Then the system should respond with status code 200
    And the response should contain:
      | id | title           | active |
      | 7  | "Home Renovation" | true  |

    Examples:
      | category_id |
      | 3          |

  Scenario Outline: Retrieve from a non-existent category (Error Flow)
    When retrieving projects under category "<invalid_category_id>"
    Then the system should respond with status code 404
    And receive error message "Category not found"

    Examples:
      | invalid_category_id |
      | 999                |
      | invalid            |
