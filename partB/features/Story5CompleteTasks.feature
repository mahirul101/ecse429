Feature: Marking tasks as Complete

  As a student, I want to mark tasks as complete, so I can track progress on my TODOs.

  Background: TODOs are created and related to course todo list.
    Given the server is running
    And the following TODOs exist:
      | title                 | doneStatus | description        |
      | "Complete lab report" | false      | "write the report" |
      | "Study for midterm"   | false      | "chapters 1-3"     |
      | "Do homework"         | false      | "chapters 3-5"     |
    And the following course todo list projects exist:
      | title      | completed | description   | active |
      | "CHEM 102" | false     | "Chemistry"   | true   |
      | "CS 103"   | false     | "Programming" | true   |

  Scenario Outline: Mark a task as complete on a course todo list (Normal Flow)
    When the student sets the doneStatus <doneStatus> for the TODO with title <title>
    Then the TODO with title <title> should have doneStatus <doneStatus>
    And the student should be notified of the successful update

    Examples:
      | title                 | doneStatus | description      |
      | "Complete lab report" | true       | write the report |
      | "Study for midterm"   | true       | chapters 1-3     |
      | "Do homework"         | true       | chapters 3-5     |

  Scenario Outline: Mark a task as complete after adding it to the course todo list (Alternative Flow)
    When a student adds the TODO with title <title> to the course todo list named <course>
    And the student sets the doneStatus <doneStatus> for the TODO with title <title>
    Then the TODO with title <title> should have doneStatus <doneStatus>
    And the student should be notified of the successful update

    Examples:
      | title                 | doneStatus | description      | course     |
      | "Study for midterm"   | true       | chapters 1-3     | "CHEM 102" |
      | "Do homework"         | true       | chapters 3-5     | "CHEM 102" |
      | "Complete lab report" | true       | write the report | "CS 103"   |

  Scenario Outline: Attempt to mark a non-existent task as complete (Error Flow)
    Given a TODO with id <invalid_id> does not exist
    When a student sets the doneStatus <doneStatus> for the TODO with id <invalid_id>
    Then the student should receive an error message <message> for the invalid TODO id <invalid_id>

    Examples:
      | invalid_id | doneStatus | message                            |
      | "999"      | true       | Invalid GUID for "999" entity todo |