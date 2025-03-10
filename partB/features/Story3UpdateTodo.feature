Feature: Update TODO Status and Details

  As a student, I want to update task status and details, so I can keep track of my academic progress.

  Background: Server is running
    Given the server is running
    And existing TODO:
      | id | title                  | doneStatus |
      | 1  | "Finish math homework" | false      |

  Scenario Outline: Mark TODO as complete (Normal Flow)
    When updating todo "1" doneStatus to "<doneStatus>"
    Then todo "1" shows doneStatus "<doneStatus>"

    Examples:
      | doneStatus |
      | true       |

  Scenario Outline: Update TODO description (Alternate Flow)
    When updating todo "1" with title "Finish math homework" description to "<new_desc>"
    Then todo "1" description matches "<new_desc>"

    Examples:
      | new_desc                             |
      | "Complete all calculus problems"     |
      | "Review solutions before submission" |

  Scenario Outline: Update non-existent TODO (Error Flow)
    When attempting to update todo "<invalid_id>"
    Then receive todo update error "Invalid GUID for <invalid_id> entity todo"

    Examples:
      | invalid_id |
      | "999"      |
      | "invalid"  |