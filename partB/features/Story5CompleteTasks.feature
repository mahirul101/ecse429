Feature: Marking tasks as Complete

  As a student, I want to mark tasks as complete, so I can track progress on my TODOs.

  Background: TODOs are created and related to course todo list.
    Given the server is running
    And the following TODOs exist:
      | title                  | doneStatus | description       |
      | Work on group project  | false      | setup the project |
      | Finish webwork         | false      | 3 problems left   |
      | Do Shakespeare Reading | false      | Act 1 only        |
    And the following course todo list projects exist:
      | title       | completed | description | active |
      | MATH 141    | false     | Calc 2      | true   |
      | ENGL 202    | false     | Literature  | true   |
      | Intro to SE | false     | Coding      | true   |

  Scenario Outline: Mark a task as complete on a course todo list (Normal Flow)
    When a student sets the doneStatus <doneStatus> for the TODO with title <title>
    Then the TODO with title <title> should have doneStatus <doneStatus>
    And the student should be notified of the successful update

    Examples:
      | title                    | doneStatus | description       |
      | "Work on group project"  | "true"     | setup the project |
      | "Finish webwork"         | "true"     | 3 problems left   |
      | "Do Shakespeare Reading" | "false"    | Act 1 only        |

  Scenario Outline: Mark a task as complete after adding it to the course todo list (Alternative Flow)
    When a student adds the TODO with title <title> to the course todo list named <course>
    And the student sets the doneStatus <doneStatus> for the TODO with title <title>
    Then the TODO with title <title> should have doneStatus <doneStatus>
    And the student should be notified of the successful update

    Examples:
      | title                    | doneStatus | description       | course        |
      | "Finish webwork"         | "true"     | 3 problems left   | "MATH 141"    |
      | "Do Shakespeare Reading" | "true"     | Act 1 only        | "ENGL 202"    |
      | "Work on group project"  | "true"     | setup the project | "Intro to SE" |

  Scenario Outline: Attempt to mark a non-existent task as complete (Error Flow)
    Given a TODO with id <non_existing_id> does not exist
    When a student sets the doneStatus <doneStatus> for the TODO with id <non_existing_id>
    Then the student should receive an error message <message>

    Examples:
      | non_existing_id | doneStatus | message                                                 |
      | "50"            | "true"     | "No such TODO entity instance with GUID or ID 50 found" |