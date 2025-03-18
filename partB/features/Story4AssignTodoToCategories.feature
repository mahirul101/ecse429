Feature: Manage tasks by categories

  As a student, I want to create todos and assign it to categories, so I can easily find and manage them.

  Background: Server is running
    Given the server is running
    And categories exist:
      | name       |
      | "Homework" |
      | "Project"  |

  Scenario Outline: Assign existing category to a todo (Normal Flow)
    Given todo "<todo_title>" exists
    And category "<category>" exists
    When assigning "<category>" category to "<todo_title>" todo
    Then "<category>" category appears in "<todo_title>" todo

    Examples:
      | todo_title         | category   |
      | "Study Chapter 1"  | "Homework" |
      | "Start assignment" | "Project"  |

  Scenario Outline: Create new category and assign to todo (Alternate Flow)
    Given todo "<todo_title>" exists
    When creating a new category "<new_category>"
    And assigning it to "<todo_title>" todo
    Then "<new_category>" category appears in "<todo_title>" todo

    Examples:
      | todo_title         | new_category |
      | "Study Chapter 1"  | "Reading"    |
      | "Start assignment" | "Coding"     |

  Scenario Outline: Assign category to non-existent todo (Error Flow)
    When attempting to assign "Homework" category to non-existent todo "<invalid_id>"
    Then receive error "Could not find parent thing for relationship todos/<invalid_id>/categories"

    Examples:
      | invalid_id |
      | "9999"     |
      | "5555"     |
