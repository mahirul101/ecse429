Feature: Update Project Status and Details

  As a student, I want to update project status and details, so I can keep track of my academic progress.

  Background: Server is running
    Given the server is running
    And existing project:
      | id | title                | completed | active | description            |
      | 1  | "Complete project A" | false     | true   | "Ongoing project work" |

  Scenario Outline: Mark project as completed (Normal Flow)
    When updating project "1" completed status to "<completed>"
    Then project "1" shows completed status "<completed>"

    Examples:
      | completed |
      | true      |

  Scenario Outline: Update project description (Alternate Flow)
    When updating project "1" with title "Complete project A" description to "<new_desc>"
    Then project "1" description matches "<new_desc>"

    Examples:
      | new_desc                          |
      | "Finalizing project deliverables" |
      | "Preparing for project review"    |

  Scenario Outline: Update non-existent project (Error Flow)
    When attempting to update project "<invalid_id>"
    Then receive project update error "Invalid GUID for <invalid_id> entity project"

    Examples:
      | invalid_id |
      | "999"      |
      | "invalid"  |