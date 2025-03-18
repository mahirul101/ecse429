from behave import given, when, then
import requests
import time

BASE_URL = "http://localhost:4567"
TODO_ENDPOINT = f"{BASE_URL}/todos"
PROJECT_ENDPOINT = f"{BASE_URL}/projects"

@given('existing to-dos')
def step_impl_existing_todos(context):
    """Ensure that the to-dos exist."""
    for row in context.table:
        todo_id = row['id']
        title = row['title']
        completed = row['completed'].lower() == "true"

        response = requests.get(f"{TODO_ENDPOINT}/{todo_id}")
        if response.status_code != 200:
            payload = {"id": todo_id, "title": title, "completed": completed}
            create_response = requests.post(TODO_ENDPOINT, json=payload)
            assert create_response.status_code == 201, f"Failed to create to-do {todo_id}"

@given('existing projects assigned to todo')
def step_impl_existing_projects(context):
    """Ensure that the projects exist."""
    for row in context.table:
        project_id = row['id']
        title = row['title']
        active = row['active'].lower() == "true"

        response = requests.get(f"{PROJECT_ENDPOINT}/{project_id}")
        if response.status_code != 200:
            payload = {"id": project_id, "title": title, "active": active}
            create_response = requests.post(PROJECT_ENDPOINT, json=payload)
            assert create_response.status_code == 201, f"Failed to create project {project_id}"

@when('assigning to-do "{todo_id}" to project "{project_id}"')
def step_impl_assign_todo_to_project(context, todo_id, project_id):
    """Assign a to-do to a project."""
    payload = {"id": todo_id}
    context.response = requests.post(f"{PROJECT_ENDPOINT}/{project_id}/tasks", json=payload)

@then('the to-do should now belong to the project')
def step_impl_verify_todo_in_project(context):
    """Verify that the to-do is linked to the project."""
    assert context.response.status_code == 201, f"Failed to assign to-do: {context.response.text}"
