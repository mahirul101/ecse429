Feature: Retrieve To-Dos by Category

  As a user, I want to retrieve all to-dos under a specific category, so I can see related tasks.

  Background: Server is running with existing categories and to-dos
    Given the server is running
    And existing categories:
      | name   |
      | "Work" |
    And to-dos under category "Work":
      | title            | doneStatus |
      | "Submit report"  | false      |
      | "Prepare slides" | true       |

  Scenario Outline: Successfully retrieve to-dos of a category (Normal Flow)
    When retrieving to-dos under category "<category_title>"
    Then the system should respond with status code 200
    And the response should contain:
      | title            | doneStatus |
      | "Submit report"  | false      |
      | "Prepare slides" | true       |

    Examples:
      | category_title |
      | Work           |

  Scenario Outline: Retrieve from a non-existent category (Error Flow)
    When retrieving to-dos under invalid category "<invalid_category>"
    #BUG: The system should respond with status code 404 (from part A)
    Then the system should respond with status code 200

    Examples:
      | invalid_category |
      | 999              |
      | invalid          |
