Feature: Retrieve All Todos

  As a student, I want to retrieve all todos, so I can view my complete task list.

  Background: Server is running with existing todos
    Given the server is running
    And existing todos:
      | id | title                  | doneStatus | description            |
      | 1  | "Complete assignment"  | false      | "Finish math homework" |
      | 2  | "Study for exam"       | true       | "Review chapter 5"     |
      | 3  | "Buy groceries"        | false      | "Get milk and eggs"    |

  Scenario: Retrieve all todos (Normal Flow)
    When retrieving all todos
    Then the system should respond with status code 200
    And the response should contain at least 3 todos
    And the retrieved todos should include todo "1"
    And the retrieved todos should include todo "2"
    And the retrieved todos should include todo "3"

  Scenario Outline: Filter todos by done status (Alternate Flow)
    When retrieving todos with done status "<status>"
    Then the system should respond with status code 200
    And all retrieved todos should have done status "<status>"

    Examples:
      | status |
      | true   |
      | false  |

   Scenario Outline: Retrieve todos with non-existent title (Error Flow)
    When retrieving todos with title "<non_existent_title>"
    Then the system should respond with status code 200
    And the response should contain <count> todos

    Examples:
      | non_existent_title    | count |
      | ThisTodoDoesNotExist  | 0     |

      