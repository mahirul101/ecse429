Feature: Retrieve Specific Project

  As a student, I want to retrieve specific project details, so I can view my project information.

  Background: Server is running
    Given the server is running
    And existing projects:
      | id | title                | completed | active | description            |
      | 1  | "School Project"     | false     | true   | "Research assignment"  |
      | 2  | "Personal Project"   | true      | true   | "Side project"         |

  Scenario Outline: Retrieve an existing project (Normal Flow)
    When retrieving project "1"
    Then the system should respond with status code 200
    And the project details should match:
      | title            | completed | active | description           |
      | "School Project" | false     | true   | "Research assignment" |

  Scenario Outline: Retrieve projects with specific fields (Alternate Flow)
    When retrieving project "1" with fields "<fields>"
    Then the system should respond with status code 200
    And the response should only contain fields "<fields>"

    Examples:
      | fields                |
      | "title,description"   |
      | "completed,active"    |

  Scenario Outline: Retrieve non-existent project (Error Flow)
    When attempting to retrieve project "<invalid_id>"
    Then the system should respond with status code 404
    And receive project error "Could not find an instance with projects/<invalid_id>"

    Examples:
      | invalid_id |
      | "999"      |
      | "invalid"  |