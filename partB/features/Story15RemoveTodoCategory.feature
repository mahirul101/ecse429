Feature: Remove Todo Category

  As a student, I want to remove a category from a todo, so I can update my task categorization as needed.

  Background: Server is running
    Given the server is running
    And existing todo:
      | id | title                 | doneStatus | description            |
      | 1  | "Complete assignment" | false      | "Finish math homework" |
    And existing category:
      | title    | description      |
      | "School" | "Academic tasks" |
    And the category "School" is assigned to todo "1"

  Scenario Outline: Remove a category from a todo (Normal Flow)
    When removing category "<category_title>" from todo "<todo_id>"
    Then the system should respond with status code 200
    And the category "<category_title>" should not be assigned to todo "<todo_id>"

    Examples:
      | category_title | todo_id |
      | School         | 1       |

  Scenario Outline: Remove a non-existent category from a todo (Alternate Flow)
    When attempting to remove category "<invalid_category_title>" from todo "<todo_id>"
    Then receive category removal error "Could not find any instances with categories/<invalid_category_id>"

    Examples:
      | invalid_category_title | todo_id |
      | fdvddfg                | 1       |

  Scenario Outline: Remove a category from a non-existent todo (Error Flow)
    When attempting to remove category "<category_title>" from todo "<invalid_todo_id>"
    Then receive todo removal error "Could not find any instances with todos/<invalid_todo_id>"

    Examples:
      | category_title | invalid_todo_id |
      | School         | 999             |