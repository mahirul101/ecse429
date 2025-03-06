Feature: Delete Completed TODOs

  As a productivity enthusiast, I want to clean up completed tasks, so I can focus on remaining work.

  Background: Server is running
    Given the server is running
    And existing TODOs:
      | id | title          | doneStatus |
      | 10 | "Call dentist" | true       |
      | 11 | "Pay bills"    | true       |

  Scenario Outline: Delete completed TODO (Normal Flow)
    When deleting todo "<id>" with doneStatus true
    Then todo "<id>" is removed from system
    And remaining todos exclude "<title>"

    Examples:
      | id | title          |
      | 10 | "Call dentist" |
      | 11 | "Pay bills"    |

  Scenario Outline: Attempt delete active TODO (Alternate Flow)
    Given todo "12" has doneStatus false
    When attempting to delete todo "12"
    Then system warns "Cannot delete incomplete tasks"
    And todo "12" remains in system

  Scenario Outline: Delete non-existent TODO (Error Flow)
    When attempting to delete todo "<invalid_id>"
    Then receive error "Could not find thing with ID <invalid_id>"

    Examples:
      | invalid_id |
      | "9999"     |
      | "deleted"  |
