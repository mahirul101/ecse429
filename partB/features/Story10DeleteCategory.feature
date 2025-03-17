Feature: Delete a Category
  As a user, I want to delete a category by its ID so that I can remove classifications that are no longer relevant.

  Background: Server is running and categories are set up
    Given the server is running
    And the following categories exist in the system:
      | name        | description               |
      | Physics     | Physics related tasks     |
      | Mathematics | Mathematics related tasks |

  # Normal Flow: Successfully delete an existing category.
  Scenario Outline: Delete an existing category (Normal Flow)
  Given a category "<name>" exists in the system
  When the user deletes the category with name "<name>"
  Then the category with name "<name>" should no longer exist in the system

  Examples:
    | name        |
    | Physics     |

  # Alternate Flow: Delete a category that is linked to items.
  Scenario Outline: Delete a category with linked items (Alternate Flow)
    Given a category "<name>" has related items
    When the user deletes the category with name "<name>"
    Then the category with name <name> should be removed from the system

    Examples:
      | name          |
      | Music         |


  # Error Flow: Attempt to delete a non-existent category.
  Scenario Outline: Delete a non-existent category (Error Flow)
    When the user attempts to delete the category with id "<invalid_category_id>" delete category
    Then the system should respond with status code 404 delete category
    And the user should receive an error message "Could not find any instances with categories <invalid_category_id>" delete category

    Examples:
      | invalid_category_id |
      | 999                 |
      | 888                 |