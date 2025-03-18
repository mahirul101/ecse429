from behave import *
import requests

BASE_URL = "http://localhost:4567"
CATEGORIES_ENDPOINT = f"{BASE_URL}/categories"
TODOS_ENDPOINT = f"{BASE_URL}/todos"

# Helper function to print response details for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

@given('existing categories')
def step_impl_existing_categories(context):
    """Ensure the categories defined in the scenario's data table exist."""
    context.category_ids = {}
    for row in context.table:
        name = row['name'].strip('"')

        # Check if the category already exists
        response = requests.get(CATEGORIES_ENDPOINT)
        if response.status_code == 200:
            categories = response.json().get("categories", [])
            existing_category = next((cat for cat in categories if cat['title'] == name), None)
            if existing_category:
                print(f"Category '{name}' already exists with ID {existing_category['id']}")
                context.category_ids[name] = existing_category['id']
                continue

        # Create the category
        payload = {"title": name}
        response = requests.post(CATEGORIES_ENDPOINT, json=payload)
        assert response.status_code == 201, f"Failed to create category: {response.text}"
        category_id = response.json().get("id")
        context.category_ids[name] = category_id
        print(f"Created Category '{name}' with ID {category_id}")

@given('to-dos under category "{category_name}"')
def step_impl_todos_under_category(context, category_name):
    """Ensure the to-dos defined in the scenario's data table are assigned to the category."""
    category_id = context.category_ids.get(category_name)
    assert category_id, f"Category '{category_name}' does not exist in context."

    for row in context.table:
        title = row['title'].strip('"')
        doneStatus = row['doneStatus'].lower() == 'true'

        # Check if the to-do already exists
        response = requests.get(TODOS_ENDPOINT)
        if response.status_code == 200:
            todos = response.json().get("todos", [])
            existing_todo = next((todo for todo in todos if todo['title'] == title), None)
            if existing_todo:
                print(f"To-Do '{title}' already exists with ID {existing_todo['id']}")
                assign_todo_to_category(existing_todo['id'], category_id)
                continue

        # Create the to-do
        payload = {"title": title, "doneStatus": doneStatus}
        response = requests.post(TODOS_ENDPOINT, json=payload)
        assert response.status_code == 201, f"Failed to create to-do: {response.text}"
        todo_id = response.json().get("id")
        print(f"Created To-Do '{title}' with ID {todo_id}")

        # Assign the to-do to the category
        assign_todo_to_category(todo_id, category_id)

def assign_todo_to_category(todo_id, category_id):
    """Helper function to assign a to-do to a category."""
    url = f"{CATEGORIES_ENDPOINT}/{category_id}/todos"
    payload = {"id": todo_id}
    response = requests.post(url, json=payload)
    assert response.status_code == 201, f"Failed to assign to-do to category: {response.text}"
    print(f"Assigned To-Do with ID {todo_id} to Category with ID {category_id}")

@when('retrieving to-dos under category "{category_name}"')
def step_impl_retrieve_todos_under_category(context, category_name):
    """Retrieve to-dos under a specific category."""
    category_id = context.category_ids.get(category_name)
    assert category_id, f"Category '{category_name}' does not exist in context."
    url = f"{CATEGORIES_ENDPOINT}/{category_id}/todos"
    context.response = requests.get(url)
    print_response(context.response)

@when('retrieving to-dos under invalid category "{category_name}"')
def step_impl_retrieve_todos_under_invalid_category(context, category_name):
    """Retrieve to-dos under an invalid category."""
    category_id = context.category_ids.get(category_name, "invalid")
    url = f"{CATEGORIES_ENDPOINT}/{category_id}/todos"
    context.response = requests.get(url)
    print_response(context.response)

@then('the response should contain')
def step_impl_verify_response_contains_todos(context):
    """Verify that the response contains the expected to-dos."""
    response_data = context.response.json()
    todos = response_data.get("todos", [])
    expected_todos = [row for row in context.table]
    print(f"Actual To-Dos: {todos}")
    print(f"Expected To-Dos: {expected_todos}")

    for expected_todo in expected_todos:
        # Extract expected values
        expected_title = expected_todo['title'].strip('"')
        expected_done_status = expected_todo['doneStatus'].lower() == 'true'

        # Find the matching to-do in the response
        matching_todo = next((todo for todo in todos if todo['title'] == expected_title), None)
        assert matching_todo, f"To-Do with title '{expected_title}' not found in response."

        # Verify the doneStatus matches
        actual_done_status = matching_todo['doneStatus'].lower() == 'true'
        assert actual_done_status == expected_done_status, (
            f"Expected doneStatus '{expected_done_status}' for To-Do '{expected_title}', "
            f"but got '{matching_todo['doneStatus']}'."
        )