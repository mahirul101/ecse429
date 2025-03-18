Feature: Retrieve To-Dos by Category

  As a user, I want to retrieve all to-dos under a specific category, so I can see related tasks.

  Background: Server is running with existing categories and to-dos
    Given the server is running
    And existing categories:
      | id | name          |
      | 5  | "Work"        |
    And to-dos under category "Work":
      | id | title            | completed |
      | 1  | "Submit report"  | false     |
      | 2  | "Prepare slides" | true      |

  Scenario Outline: Successfully retrieve to-dos of a category (Normal Flow)
    When retrieving to-dos under category "<category_id>"
    Then the system should respond with status code 200
    And the response should contain:
      | id | title            | completed |
      | 1  | "Submit report"  | false     |
      | 2  | "Prepare slides" | true      |

    Examples:
      | category_id |
      | 5          |

  Scenario Outline: Retrieve from a non-existent category (Error Flow)
    When retrieving to-dos under category "<invalid_category_id>"
    Then the system should respond with status code 404
    And receive error message "Category not found"

    Examples:
      | invalid_category_id |
      | 999                |
      | invalid            |
