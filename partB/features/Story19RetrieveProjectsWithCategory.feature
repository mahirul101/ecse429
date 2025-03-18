Feature: Retrieve Projects Associated with a Category

  As a user, I want to retrieve all projects under a category, so I can manage grouped projects.

  Background: Server is running with existing projects and categories
    Given the server is running
    And the following categories exist retreived from the API:
      | title       |
      | Personal   |
      | Work       |
    And the following projects exist under category Personal:
      | title             | active |
      | Home Renovation   | True   |

  Scenario Outline: Successfully retrieve projects of a category (Normal Flow)
    When retrieving projects under category "<category_title>"
    Then the system should respond with status code 200 retreive projects
    And the response should contain the following projects:
      | title             | active |
      | Home Renovation   | True   |

    Examples:
      | category_title |
      | Personal       |

  Scenario Outline: Retrieve projects from a category with no associated projects (Alternate Flow)
    Given category "<category_title>" exists but has no projects
    When retrieving projects under category "<category_title>"
    Then the system should respond with status code 200 retreive projects
    And the response should be an empty list of projects

    Examples:
      | category_title |
      | Work           |

  Scenario Outline: Retrieve from a non-existent category (Error Flow) BUG HERE Should be 404
    When retrieving projects under category "<invalid_category>"
    Then the system should respond with status code 404 retreive projects

    Examples:
      | invalid_category |
      | Nonexistent      |
