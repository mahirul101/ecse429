Feature: Retrieve Projects Associated with a Category

  As a user, I want to retrieve all projects under a category, so I can manage grouped projects.

  Background: Server is running with existing projects and categories
    Given the server is running
    And existing categories:
      | name       |
      | "Personal" |
    And projects under category "Personal":
      | title             | active |
      | "Home Renovation" | true   |

  Scenario Outline: Successfully retrieve projects of a category (Normal Flow)
    When retrieving projects under category "<category_title>"
    Then the system should respond with status code 200
    And the response should contain:
      | title             | active |
      | "Home Renovation" | true   |

    Examples:
      | category_title |
      | "Personal"     |

  Scenario Outline: Retrieve from a non-existent category (Error Flow)
    When retrieving projects under category "<invalid_category>"
    Then the system should respond with status code 404
    And receive error message "Category not found"

    Examples:
      | invalid_category |
      | 999              |
      | invalid          |
