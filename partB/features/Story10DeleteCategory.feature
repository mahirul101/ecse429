Feature: Delete a Category
  As a user, I want to delete a category by its ID so that I can remove classifications that are no longer relevant.
  This uses DELETE on /categories/:id.

  Background: Server is running and categories are set up
    Given the server is running
    And the following categories exist:
      | category_id | name                   | description                 |
      | "601"       | "Subject: Physics"     | "Physics related tasks"     |
      | "602"       | "Subject: Mathematics" | "Mathematics related tasks" |
      | "603"       | "Subject: Literature"  | "Literature related tasks"  |

  # Normal Flow: Successfully delete an existing category.
  Scenario Outline: Delete an existing category (Normal Flow)
    When the user deletes the category with id "<category_id>"
    Then the category with id "<category_id>" should no longer exist in the system
    And the user receives a confirmation message "Category deleted successfully"

    Examples:
      | category_id |
      | "601"       |
      | "602"       |

  # Alternate Flow: Delete a category that is linked to items.
  Scenario Outline: Delete a category with linked items (Alternate Flow)
    Given the category with id "<category_id>" is linked to items
    When the user deletes the category with id "<category_id>"
    Then the category with id "<category_id>" and its associations should be removed from the system
    And the user receives a confirmation message "Category and associations deleted successfully"

    Examples:
      | category_id |
      | "603"       |

  # Error Flow: Attempt to delete a non-existent category.
  Scenario Outline: Delete a non-existent category (Error Flow)
    When the user attempts to delete the category with id "<invalid_category_id>"
    Then the system should respond with status code 404
    And the user should receive an error message "Category not found for id <invalid_category_id>"

    Examples:
      | invalid_category_id |
      | "999"               |
      | "888"               |


