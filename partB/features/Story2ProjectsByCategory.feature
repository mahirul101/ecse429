Feature: Organize Projects by Category

  As a student, I want to categorize my projects by subject, so I can easily find and manage them.

  Background: Server is running
    Given the server is running
    And projects exist:
      | title                 |
      | "Physics Lab Report"  |
      | "Calculus Assignment" |

  Scenario Outline: Assign existing category to a project (Normal Flow)
    Given category "Subject: <subject>" exists
    When assigning "<subject>" category to "<project>" project
    Then "<subject>" category appears in "<project>" project

    Examples:
      | project               | subject       |
      | "Physics Lab Report"  | "Physics"     |
      | "Calculus Assignment" | "Mathematics" |

  Scenario Outline: Create new subject category and assign (Alternate Flow)
    When creating new category "<subject>"
    And assigning it to "<project>" project
    Then "<subject>" category appears in "<project>" project

    Examples:
      | project               | subject       |
      | "Physics Lab Report"  | "Experiments" |
      | "Calculus Assignment" | "Algebra"     |

  Scenario Outline: Assign category to non-existent project (Error Flow)
    When attempting to assign "Literature" category to non-existent project "<invalid_id>"
    Then receive error "Could not find parent thing for relationship projects/<invalid_id>/categories"

    Examples:
      | invalid_id |
      | "9999"     |
      | "5555"     |
