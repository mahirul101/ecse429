from behave import *
import requests

BASE_URL = "http://localhost:4567"
PROJECTS_ENDPOINT = f"{BASE_URL}/projects"
TODOS_ENDPOINT = f"{BASE_URL}/todos"

# Helper function to print response details for debugging
def print_response(response):
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

@given('existing to-dos')
def step_impl_existing_todos(context):
    """Ensure the to-dos defined in the scenario's data table exist."""
    context.todo_ids = {}
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
                context.todo_ids[title] = existing_todo['id']
                continue

        # Create the to-do
        payload = {"title": title, "doneStatus": doneStatus}
        response = requests.post(TODOS_ENDPOINT, json=payload)
        assert response.status_code == 201, f"Failed to create to-do: {response.text}"
        todo_id = response.json().get("id")
        context.todo_ids[title] = todo_id
        print(f"Created To-Do '{title}' with ID {todo_id}")

@given('existing projects assigned to todo')
def step_impl_existing_projects(context):
    """Ensure the projects defined in the scenario's data table exist."""
    context.project_ids = {}
    for row in context.table:
        title = row['project_title'].strip('"')
        active = row['active'].lower() == 'true'
        todo_title = row['todo_title'].strip('"')

        # Check if the project already exists
        response = requests.get(PROJECTS_ENDPOINT)
        if response.status_code == 200:
            projects = response.json().get("projects", [])
            existing_project = next((project for project in projects if project['title'] == title), None)
            if existing_project:
                print(f"Project '{title}' already exists with ID {existing_project['id']}")
                context.project_ids[title] = existing_project['id']
                continue

        # Create the project
        payload = {"title": title, "active": active}
        response = requests.post(PROJECTS_ENDPOINT, json=payload)
        assert response.status_code == 201, f"Failed to create project: {response.text}"
        project_id = response.json().get("id")
        context.project_ids[title] = project_id
        print(f"Created Project '{title}' with ID {project_id}")

        # Assign the to-do to the project
        todo_id = context.todo_ids.get(todo_title)
        assert todo_id, f"To-Do '{todo_title}' does not exist in context."
        assign_todo_to_project(context, todo_id, title)

def assign_todo_to_project(context, todo_id, project_title):
    """Helper function to assign a to-do to a project."""
    project_id = context.project_ids.get(project_title)
    url = f"{PROJECTS_ENDPOINT}/{project_id}/tasks"
    payload = {"id": todo_id}
    response = requests.post(url, json=payload)
    assert response.status_code == 201, f"Failed to assign to-do to project: {response.text}"
    print(f"Assigned To-Do with ID {todo_id} to Project with ID {project_id}")
    context.response = response

@when('assigning to-do "{todo_title}" to project "{project_title}"')
def step_impl_assign_todo_to_project(context, todo_title, project_title):
    """Assign a to-do to a project."""
    todo_id = context.todo_ids.get(todo_title)
    assert todo_id, f"To-Do '{todo_title}' does not exist in context."
    project_id = context.project_ids.get(project_title)
    assert project_id, f"Project '{project_title}' does not exist in context."
    assign_todo_to_project(context, todo_id, project_title)

@when('assigning invalid to-do "{invalid_todo}" to project "{project_title}"')
def step_impl_assign_invalid_todo_to_project(context, invalid_todo, project_title):
    """Attempt to assign an invalid to-do to a project and verify the error."""
    project_id = context.project_ids.get(project_title)
    assert project_id, f"Project '{project_title}' does not exist in context."

    # Attempt to assign the invalid to-do
    url = f"{PROJECTS_ENDPOINT}/{project_id}/tasks"
    payload = {"id": invalid_todo}
    context.response = requests.post(url, json=payload)
    print_response(context.response)

    # Verify the response
    assert context.response.status_code == 404, f"Expected status code 404, but got {context.response.status_code}."
    error_messages = context.response.json().get('errorMessages', [])
    assert "Could not find thing matching value for id" in error_messages[0]

@when('assigning to-do "{todo_title}" to invalid project "{invalid_project}"')
def step_impl_assign_todo_to_invalid_project(context, todo_title, invalid_project):
    """Attempt to assign a to-do to an invalid project and verify the error."""
    todo_id = context.todo_ids.get(todo_title)
    assert todo_id, f"To-Do '{todo_title}' does not exist in context."

    # Attempt to assign the to-do to an invalid project
    url = f"{PROJECTS_ENDPOINT}/{invalid_project}/tasks"
    payload = {"id": todo_id}
    context.response = requests.post(url, json=payload)
    print_response(context.response)

    # Verify the response
    assert context.response.status_code == 404, f"Expected status code 404, but got {context.response.status_code}."

@then('the system should respond with status code 201')
def step_impl_verify_status_code(context):
    """Verify the status code of the response."""
    assert context.response.status_code == 201

@then('the to-do "{todo_title}" should now belong to the project "{project_title}"')
def step_impl_verify_todo_belongs_to_project(context, todo_title, project_title):
    """Verify that the to-do is now assigned to the project."""
    todo_id = context.todo_ids.get(todo_title)
    assert todo_id, f"To-Do '{todo_title}' does not exist in context."
    project_id = context.project_ids.get(project_title)
    assert project_id, f"Project '{project_title}' does not exist in context."

    # Verify the to-do is assigned to the project
    url = f"{PROJECTS_ENDPOINT}/{project_id}/tasks"
    response = requests.get(url)
    assert response.status_code == 200, f"Failed to retrieve tasks for project: {response.text}"
    tasks = response.json().get("todos", [])
    assert any(task['id'] == todo_id for task in tasks), f"To-Do '{todo_title}' is not assigned to Project '{project_title}'."